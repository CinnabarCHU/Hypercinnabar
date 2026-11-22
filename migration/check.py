"""Verify source sections, the registered role catalogue and the GUIDE inventory."""
import argparse
import csv
import io
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / 'migration'
SOURCE = ROOT / 'upstream' / 'acycle'
METHODS = ROOT / 'matlab' / '+acmethods'
PIN = 'b52ea9f510f3be00bde9a0238b9898a1e2315b74'
LINK = 'https://github.com/mingsongli/acycle/blob/' + PIN + '/'
MARK = '%% Copied from mingsongli/acycle@' + PIN + ' '
SECTIONS = re.compile(re.escape(MARK) + r'(.+):L(\d+)-L(\d+)$')
SOURCES = re.compile(r'^% Source: ' + re.escape(LINK) + r'([^#]+?)(?:#L(\d+))?$')
ROLES = {'helper', 'analyzer', 'plotter'}


@lru_cache(None)
def original(path):
    return (SOURCE / path).read_bytes().decode('utf-8-sig', 'replace').splitlines()


def check_sections(file, lines, references):
    count = 0
    for i, line in enumerate(lines):
        if line.startswith('% Source:'):
            match = SOURCES.fullmatch(line)
            assert match, (file, i + 1, line)
            path, first = match.groups()
            assert (SOURCE / path).is_file(), (file, path)
            if first:
                assert 1 <= int(first) <= len(original(path)), (file, path, first)
            references.add(path)
        if not line.startswith('%% Copied from'):
            continue
        match = SECTIONS.fullmatch(line)
        assert match, (file, i + 1, line)
        path, first, last = match.groups()
        source = original(path)
        first, last = int(first), int(last)
        assert 1 <= first <= last <= len(source), (file, path, first, last)
        length = last - first + 1
        assert lines[i + 1:i + 1 + length] == source[first - 1:last], (file, path, first, last)
        assert lines[i + 1 + length] == '%% End copied source', (file, path, first, last, 'closing marker')
        references.add(path)
        count += 1
    assert count == lines.count('%% End copied source'), (file, 'unmatched source markers')
    return count


def table(header, rows):
    output = io.StringIO()
    writer = csv.writer(output, delimiter='\t', lineterminator='\n')
    writer.writerow(header)
    writer.writerows(rows)
    return output.getvalue()


def sync(path, data, write):
    if write:
        path.write_text(data, encoding='utf8')
    else:
        assert path.read_text(encoding='utf8') == data, f'Stale index: {path}. Run python migration/check.py --write.'


def rows(path):
    with path.open(encoding='utf8', newline='') as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def check_methods(write):
    by_source = defaultdict(set)
    catalogue = []
    packages = set()
    section_total = 0
    for file in sorted(METHODS.glob('+*/*.m')):
        method = file.parent.name[1:]
        role = file.stem
        assert role in ROLES, file
        packages.add(method)
        lines = file.read_text(encoding='utf8').splitlines()
        assert f'= {role}(params, id)' in lines[0], file
        assert any(f"'{method}-v1.0/{role}'" in line for line in lines), file
        refs = set()
        count = check_sections(file, lines, refs)
        assert refs, file
        section_total += count
        for source in refs:
            by_source[source].add(method + '.' + role)
        fields = next((line.partition(' parameters: ')[2].rstrip('.') for line in lines if ' parameters: ' in line), '')
        catalogue.append([method, role, fields, count, ' | '.join(sorted(refs))])
    assert len(set(x.casefold() for x in packages)) == len(packages), 'case-only package collision'
    sync(MIGRATION / 'methods.tsv', table(['package','role','parameters','copied_sections','source_files'], catalogue), write)
    files = subprocess.check_output(['git','-C',str(SOURCE),'ls-tree','-r','--name-only','HEAD'],text=True).splitlines()
    sources = [[name, ' | '.join(sorted(by_source[name]))] for name in files if name.lower().endswith(('.m','.p','.fig'))]
    sync(MIGRATION / 'baseline.tsv', table(['source_path','directly_attributed_roles'], sources), write)
    menus = rows(MIGRATION / 'menus.tsv')
    assert len({m['guide_tag'] for m in menus}) == len(menus) == 130
    for menu in menus:
        for package in menu['packages'].split():
            assert package in packages, (menu['guide_tag'],package)
    print(f'{len(packages)} packages, {len(catalogue)} roles, {section_total} exact source sections, {len(sources)} baseline files.')
    print('Main GUIDE menu:', dict(Counter(m['coverage'] for m in menus)))


def check_figures():
    from scipy.io import loadmat
    import numpy as np

    def children(obj):
        if isinstance(obj, dict):
            yield obj
        elif isinstance(obj, (list,tuple)):
            for item in obj:
                yield from children(item)

    def descend(obj, parents=()):
        props = obj['properties']
        kind = obj['type']
        if kind == 'uimenu':
            parents = parents + (props['Label'].strip(),)
        yield obj, parents
        for child in children(obj.get('children')):
            yield from descend(child, parents)

    def fmt(value):
        if isinstance(value, np.ndarray):
            if value.size > 100:
                return f'[{value.size} values]'
            return ' | '.join(s for s in map(fmt,value.flat) if s)
        if isinstance(value, (list,tuple)):
            return ' | '.join(map(fmt,value))
        if isinstance(value, (str,int,float,np.integer,np.floating)):
            return ' '.join(str(value).split())
        return ''

    menus = rows(MIGRATION / 'menus.tsv')
    interactive = {'uicontrol','uimenu','uitoolbar','uipushtool','uitoggletool','uitable','axes','uibuttongroup','uipanel'}
    figures = sorted(SOURCE.glob('code/**/*.fig'))
    assert {p.stem for p in figures} == {p.stem for p in (MIGRATION / 'controls').glob('*.tsv')}
    total = 0
    for file in figures:
        raw = loadmat(file, simplify_cells=True)
        entries = list(descend(raw[next(key for key in raw if key.startswith('hgS'))]))
        seen = []
        for item, path in entries:
            kind = item['type']
            if kind not in interactive:
                continue
            prop = item['properties']
            tag = fmt(prop.get('Tag',''))
            if kind == 'uimenu' and file.stem == 'AC':
                match = [m for m in menus if m['guide_tag'] == tag]
                assert len(match)==1 and match[0]['menu_path']==' > '.join(path), (file,tag)
            label = fmt(prop.get('Label',prop.get('String',prop.get('Title',''))))
            callbacks = ','.join(k for k in ('Callback','SelectionChangeFcn','ButtonDownFcn','ClickedCallback') if k in prop)
            seen.append([tag,kind,fmt(prop.get('Style','')),label,fmt(prop.get('Value','')),fmt(prop.get('Enable','')),callbacks])
        index = MIGRATION / 'controls' / (file.stem+'.tsv')
        sync(index, table(['tag','type','style','label_or_string','fig_value','fig_enable','callback_properties'], seen), False)
        total += len(seen)
    print(f'{len(figures)} original GUIDE figures, {total} serialized controls verified.')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='refresh the method and baseline indexes')
    parser.add_argument('--figures',action='store_true',help='also reread the original .fig files (SciPy required)')
    args=parser.parse_args()
    actual=subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip()
    assert actual==PIN, (actual,PIN)
    check_methods(args.write)
    if args.figures:
        check_figures()
