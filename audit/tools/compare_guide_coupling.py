#!/usr/bin/env python3
"""Compare pinned GUIDE-era and code-only Acycle snapshots without MATLAB.

Counts are syntactic indicators, not a coupling score or runtime coverage.
Production .m excludes directories named test/tests and retains legacy code.
"""
import argparse
from collections import Counter
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess

from audit_acycle import parse_source, visible_variables


SNAPSHOTS = {
    'guide_2x': 'b52ea9f510f3be00bde9a0238b9898a1e2315b74',
    'migration_february': '681c1dc742cace22f515c5508b7b962692811739',
    'release_3_0': '083c949e5635fefb6a2227273c49329a0891147a',
    'current_3_1_1': 'dcba4279168745b563e0535b954297023dd62fc7',
}
GROUPS = {
    'guide_runtime': {'gui_mainfcn'},
    'ui_state': {'guidata', 'getappdata', 'setappdata'},
    'base_workspace': {'assignin', 'evalin'},
    'interaction_progress': {'inputdlg', 'questdlg', 'uigetfile', 'uiputfile',
        'uigetdir', 'ginput', 'myginput', 'uiwait', 'waitfor', 'waitbar',
        'uiprogressdlg', 'uialert', 'warndlg', 'errordlg'},
    'graphics': {'figure', 'uifigure', 'axes', 'uiaxes', 'subplot', 'plot',
        'semilogx', 'semilogy', 'loglog', 'imagesc', 'contour', 'pcolor', 'yyaxis'},
    'working_directory': {'cd', 'GETac_pwd', 'CDac_pwd'},
    'selected_numerics': {'pmtm', 'periodogram', 'plomb', 'fft', 'ifft',
        'filter', 'filtfilt', 'butter', 'designfilt', 'polyfit', 'polyval',
        'interp1', 'hilbert', 'cpsd', 'mscohere', 'pwelch', 'detrend',
        'redconf', 'redconfML', 'redconfchi2', 'pdan'},
}
SELECTED = ['code/guicode/' + x + '.m' for x in
            ('AC', 'spectrum', 'DYNOS', 'ft', 'eCOCOGUI')]


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def tree(root, sha):
    result = {}
    for entry in git(root, 'ls-tree', '-rz', sha).split(b'\0'):
        if not entry:
            continue
        meta, path = entry.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        if kind == 'blob':
            result[path.decode()] = oid
    return result


def production(path):
    return path.endswith('.m') and not {'test', 'tests'}.intersection(Path(path).parts)


def blobs(root, hashes):
    payload = ''.join(oid + '\n' for oid in sorted(hashes)).encode()
    raw = subprocess.run(['git', '-C', str(root), 'cat-file', '--batch'],
                         input=payload, stdout=subprocess.PIPE, check=True).stdout
    output, pos = {}, 0
    while pos < len(raw):
        end = raw.index(b'\n', pos)
        oid, kind, size = raw[pos:end].decode().split()
        if kind != 'blob':
            raise ValueError(kind)
        pos = end + 1
        output[oid] = raw[pos:pos + int(size)]
        pos += int(size) + 1
    return output


def parse(path, raw):
    adaptations = []
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('latin-1')
        adaptations.append('Latin-1 comments fallback')
    if path.startswith('code/package/swa/'):
        text, count = re.subn(r'(?<![\w.])(\d+(?:\.\d*)?|\.\d+)[dD]([+-]?\d+)(?!\w)',
                             r'\1e\2', text)
        if count:
            adaptations.append(f'{count} D-exponents normalized in analysis buffer')
    return parse_source(path, text), adaptations


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    repo = Path(__file__).resolve().parents[2]
    parser.add_argument('--source', type=Path, default=repo / 'upstream/acycle')
    parser.add_argument('--output', type=Path, default=repo / 'audit/coupling')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    trees = {key: tree(args.source, sha) for key, sha in SNAPSHOTS.items()}
    data = blobs(args.source, {oid for files in trees.values() for path, oid in files.items() if production(path)})
    cache, rows, evidence, summaries = {}, [], [], {}
    for key, sha in SNAPSHOTS.items():
        files = trees[key]
        for path, oid in sorted(files.items()):
            if not production(path):
                continue
            if (path, oid) not in cache:
                collector, adapters = parse(path, data[oid])
                refs = [r for r in collector.refs if r['kind'] in
                        ('call_or_index', 'command', 'bare_name') and
                        r['name'] not in visible_variables(collector, r['source'])]
                names = {r['name'] for r in refs}
                row = dict(path=path, blob=oid, sha256=hashlib.sha256(data[oid]).hexdigest(),
                    lines=len(data[oid].splitlines()), kind=collector.kind,
                    declarations=len(collector.nodes)-1, adapters='; '.join(adapters))
                row.update({group: ';'.join(sorted(names & tokens)) for group, tokens in GROUPS.items()})
                cache[path, oid] = row, refs, collector.nodes
            row, refs, nodes = cache[path, oid]
            rows.append(dict(snapshot=key, **row))
            if path in SELECTED:
                for ref in refs:
                    groups = [group for group, tokens in GROUPS.items() if ref['name'] in tokens]
                    if groups:
                        node = nodes[ref['source']]
                        evidence.append(dict(snapshot=key, path=path, function=node['name'],
                            function_start=node['line'], function_end=node['end_line'],
                            line=ref['line'], name=ref['name'], groups=';'.join(groups)))
        snapshot_rows = [row for row in rows if row['snapshot'] == key]
        guicode = [row for row in snapshot_rows if row['path'].startswith('code/guicode/')]
        summaries[key] = dict(
            commit=sha, date=git(args.source, 'show', '-s', '--format=%cI', sha).decode().strip(),
            tracked_files=len(files), production_matlab_files=len(snapshot_rows),
            excluded_test_matlab_files=sum(path.endswith('.m') and not production(path) for path in files),
            fig_files=sum(path.endswith('.fig') for path in files),
            guicode_fig_files=sum(path.startswith('code/guicode/') and path.endswith('.fig') for path in files),
            guicode_matlab_files=len(guicode), guicode_classes=sum(row['kind']=='class_file' for row in guicode),
            seriesanalysis_acycle_files=[path for path in files if path.startswith('code/seriesanalysis/acycle') and path.endswith('.m')],
            selected_file_lines={row['path']:row['lines'] for row in guicode if row['path'] in SELECTED},
            files_with_markers={group:[row['path'] for row in snapshot_rows if row[group]] for group in GROUPS},
            guicode_marker_counts={group:sum(bool(row[group]) for row in guicode) for group in GROUPS},
            non_guicode_marker_counts={group:sum(bool(row[group]) for row in snapshot_rows if row not in guicode) for group in GROUPS},
        )
    old, new = trees['guide_2x'], trees['current_3_1_1']
    changes = []
    for path in sorted(set(old) | set(new)):
        if not production(path):
            continue
        status = 'added' if path not in old else 'removed' if path not in new else 'unchanged' if old[path]==new[path] else 'modified'
        changes.append(dict(path=path,status=status,old_blob=old.get(path,''),new_blob=new.get(path,'')))
    by_directory = {}
    for prefix in ('code/guicode/', 'code/seriesanalysis/', 'code/corrcoef/', 'code/misc/', 'code/package/'):
        by_directory[prefix] = dict(Counter(row['status'] for row in changes if row['path'].startswith(prefix)))
    result = dict(snapshots=summaries, same_path_changes=by_directory,
        marker_definitions={k:sorted(v) for k,v in GROUPS.items()},
        versions={name:importlib.metadata.version(name) for name in ('miss-hit','scipy')},
        parse_failures=[],
        limitations=[
            'AST source indicators, not dynamic execution or a coupling index.',
            'Markers count files with matching direct or bare-name references; branches are not evaluated.',
            'Non-guicode includes third-party GUI and workspace scripts; it is not synonymous with numerical core.',
            'New algorithms, moved .fig layouts, and excluded tests prevent raw LOC or marker totals from measuring coupling reduction.',
            'Same-path blob identity is byte equality; modification does not establish numerical change.',
            'Parser adaptations only affect analysis buffers; no upstream source is changed.',
        ])
    (args.output/'comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    write_csv(args.output/'file_indicators.csv', rows)
    write_csv(args.output/'selected_call_evidence.csv', evidence)
    write_csv(args.output/'same_path_changes.csv', changes)
    print(json.dumps({key:{name:value for name,value in row.items() if name in
        ('production_matlab_files','guicode_matlab_files','guicode_classes','fig_files','guicode_fig_files','selected_file_lines','guicode_marker_counts','non_guicode_marker_counts')}
        for key,row in summaries.items()},ensure_ascii=False,indent=2))
    print(json.dumps(by_directory,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
