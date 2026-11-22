"""Copy selected portable packages and their distributed Acycle dependencies, preserving file bytes."""
import argparse
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / 'matlab' / '+acmethods'
BASE = ROOT / 'upstream' / 'acycle'
HIST = ROOT / 'upstream' / 'recovered' / 'code'
WORD = re.compile(r'\b[A-Za-z]\w*\b')
METHOD = re.compile(r'\bacmethods\.([A-Za-z]\w*)\.(?:analyzer|helper|plotter)\b')
FILES = re.compile(r'[\w.()+-]+\.(?:mat|txt|csv|dat|jpg|png|xlsx|fig|14c)\b', re.I)

SETUP = """function setup_method()
root=fileparts(mfilename('fullpath'));
dirs={'upstream/recovered/code','upstream/acycle/code','upstream/acycle/data'};
for i=1:numel(dirs)
    folder=fullfile(root,dirs{i});
    if isfolder(folder), addpath(genpath(folder)); end
end
extra=getenv('ACYCLE_REFERENCE_DATA');
if ~isempty(extra), addpath(extra); end
addpath(fullfile(root,'matlab'));
end
"""


def files_under(directory):
    return (p for p in directory.rglob('*') if p.is_file())


def executable(text):
    """Drop comments and quoted literals, retaining MATLAB's postfix transpose operator."""
    result = []
    for line in text.splitlines():
        index=0
        fragment=[]
        while index<len(line):
            ch=line[index]
            if ch=='%':
                break
            is_transpose = ch=="'" and index>0 and (line[index-1].isalnum() or line[index-1] in '_)]}.')
            if ch not in {'"',"'"} or is_transpose:
                fragment.append(ch); index+=1; continue
            quoted=ch
            fragment.append(' ')
            index+=1
            while index<len(line):
                if line[index]==quoted:
                    index+=1
                    if index>=len(line) or line[index]!=quoted:
                        break
                index+=1
        result.append(''.join(fragment))
    return '\n'.join(result)


def dependencies(methods):
    sourcefiles = defaultdict(list)
    resources = defaultdict(list)
    for directory in (BASE / 'code', BASE / 'data', HIST):
        for p in files_under(directory):
            if p.suffix.lower() in {'.m', '.p'}:
                sourcefiles[p.stem].append(p)
            else:
                resources[p.name.lower()].append(p)
    packages = {p.name[1:]:p for p in PACKAGES.glob('+*') if p.is_dir()}
    unknown = set(methods) - set(packages)
    if unknown:
        raise ValueError('Unknown method: ' + ', '.join(sorted(unknown)))
    queue = [f for name in methods for f in packages[name].glob('*.m')]
    queue.extend(files_under(ROOT / 'matlab' / '+aclog'))
    queue.append(ROOT / 'matlab' / 'logger.m')
    seen = set()
    while queue:
        file = queue.pop()
        if file in seen:
            continue
        seen.add(file)
        if file.suffix != '.m':
            continue
        # Retain quoted filenames, feval names, script invocations and function handles.
        # Omit MATLAB comment lines, including the headers pointing back to GUIDE callbacks.
        code = '\n'.join(s for s in file.read_text(encoding='utf-8-sig', errors='replace').splitlines()
                         if not s.lstrip().startswith('%'))
        for name in METHOD.findall(code):
            queue.extend(packages[name].glob('*.m'))
        for name in re.findall(r'\baccompat\.([A-Za-z]\w*)', code):
            queue.append(ROOT / 'matlab' / '+accompat' / (name + '.m'))
        symbols = set(WORD.findall(METHOD.sub('', executable(code))))
        symbols.update(re.findall(r"(?:which|str2func|feval|nargin|run)\(\s*'([A-Za-z]\w*)'",code))
        for name in symbols:
            queue.extend(sourcefiles.get(name, ()))
        for name in FILES.findall(code):
            queue.extend(resources.get(name.lower(), ()))
        # Private calibration tables, MEX binaries and their source remain beside the original private functions.
        private = file.parent / 'private'
        if private.is_dir():
            queue.extend(files_under(private))
        if file.is_relative_to(BASE / 'code') or file.is_relative_to(HIST):
            for p in file.parent.iterdir():
                if p.is_file() and p.suffix.lower() in {'','.md','.txt','.html','.pdf'} and re.search(r'licen[cs]e|copying|copyright|^readme', p.name, re.I):
                    queue.append(p)
    seen.update({ROOT / 'LICENSE', BASE / 'README.md', ROOT / 'migration' / 'recovered.tsv'})
    if 'AstronomicalSolution' in methods or 'Insolation' in methods or 'insoML' in methods:
        seen.update({ROOT/'migration'/'fetch_orbits.py', ROOT/'migration'/'orbits.sha256'})
        # Insolation constructs the name of the chosen orbit table at runtime.
        seen.update(f for f in files_under(BASE/'data') if f.suffix.lower()=='.mat')
    return sorted(seen)


def master_dependencies(methods):
    source = ROOT / 'upstream' / 'master'
    if not (source / 'code' / 'seriesanalysis' / 'acycleSamplingIsUneven.m').is_file():
        raise ValueError('Initialize the upstream/master submodule.')
    if not (source / 'data' / 'La04.mat').is_file():
        raise ValueError('Check out the master data directory before exporting.')
    packages = ROOT / 'matlab' / '+acmaster'
    index = {p.name[1:]: p for p in packages.glob('+*') if p.is_dir()}
    selected = set()
    pending = list(methods)
    while pending:
        name = pending.pop()
        if name not in index:
            raise ValueError(f'Unknown master method: {name}')
        if name in selected:
            continue
        selected.add(name)
        for file in index[name].glob('*.m'):
            body = file.read_text(encoding='utf8')
            pending.extend(re.findall(r'\bacmaster\.([A-Za-z]\w*)\.', body))
    files = {f for n in selected for f in files_under(index[n])}
    for shared in ('+accompat', '+aclog'):
        files.update(files_under(ROOT / 'matlab' / shared))
    # The upstream desktop dispatches by callback name and looks up resources at run time.
    # Keep its original directory layout and licensed dependencies intact in a standalone export.
    for folder in ('code', 'data'):
        files.update(files_under(source / folder))
    files.update([ROOT / 'matlab' / 'logger.m', ROOT / 'LICENSE', source / 'README.md', source / 'ac.m'])
    if 'Desktop' in selected and (source / 'doc').is_dir():
        files.update(files_under(source / 'doc'))
    return sorted(files)


def export(methods, destination, revision='guide'):
    files = master_dependencies(methods) if revision == 'master' else dependencies(methods)
    destination=destination.resolve()
    if destination.exists():
        raise FileExistsError(f'Destination already exists: {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temp:
        stage=Path(temp)/'package'
        stage.mkdir()
        checks=[]
        for file in files:
            relative=file.relative_to(ROOT)
            target=stage/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file,target)
            checks.append(f'{sha256(target.read_bytes()).hexdigest()}  {relative.as_posix()}')
        (stage/'setup_method.m').write_text(SETUP, encoding='utf8')
        (stage/'SHA256SUMS').write_text('\n'.join(checks)+'\n', encoding='utf8')
        stage.rename(destination)
    return len(files)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('methods',nargs='+',help='Case-sensitive MATLAB package names')
    parser.add_argument('--revision', choices=('guide','master'), default='guide')
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    print(f'Exported {export(args.methods,args.output,args.revision)} files to {args.output}')
