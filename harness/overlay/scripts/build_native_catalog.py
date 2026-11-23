#!/usr/bin/env python3
"""Inventory pinned MATLAB sources without pretending static scans are runtime tests."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess


SIGNATURE = re.compile(r'^\s*function\s+(?:(\[[^\]]*\]|\w+)\s*=\s*)?(\w+)\s*(?:\(([^)]*)\))?', re.M)
EFFECTS = {
    'dialog': r'\b(inputdlg|questdlg|uigetfile|uiputfile|uigetdir|listdlg|menu|input)\s*\(',
    'interaction': r'\b(ginput|myginput|uiwait|waitfor|waitforbuttonpress)\s*\(',
    'graphics': r'\b(figure|uifigure|axes|uiaxes|plot|imagesc|contourf|surf|subplot|waitbar)\s*\(',
    'gui_state': r'\b(guidata|getappdata|setappdata|uicontrol|findobj|findall)\s*\(',
    'workspace': r'\b(evalin|assignin|global|eval)\b',
    'file_io': r'\b(save|load|fopen|writematrix|writetable|readmatrix|readtable|copyfile|delete|movefile|cd)\b',
    'external': r'\b(system|unix|dos|web|webread|websave|urlread|urlwrite)\s*\(',
    'parallel': r'\b(parfor|parfeval|parpool|gcp)\b',
}


def source_lines(text):
    """Drop comment-only lines, preserving line numbers; retain strings conservatively."""
    block = False
    lines = []
    for line in text.splitlines():
        if line.strip() == '%{':
            block = True
        lines.append('' if block or line.lstrip().startswith('%') else line)
        if line.strip() == '%}':
            block = False
    return '\n'.join(lines)


def signatures(text):
    # Join MATLAB continuation lines before parsing declarations.
    joined = re.sub(r'\.\.\.[^\n]*\n\s*', ' ', source_lines(text))
    return [{'name': m[2], 'inputs': re.findall(r'\w+|~', m[3] or ''),
             'outputs': re.findall(r'\w+', m[1] or ''),
             'signature': re.sub(r'\s+', ' ', m[0].strip())}
            for m in SIGNATURE.finditer(joined)]


def build(root):
    root = Path(root).resolve()
    revision = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    tracked = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z']).decode().split('\0')
    entries = []
    for relative in sorted(x for x in tracked if x.endswith('.m')):
        path = root / relative
        raw = path.read_bytes()
        text = raw.decode('utf-8-sig', errors='replace')
        code = source_lines(text)
        first = next((l.strip() for l in code.splitlines() if l.strip()), '')
        kind = 'class' if first.startswith('classdef') else 'function' if first.startswith('function') else 'script'
        declarations = signatures(text)
        public = declarations[0] if kind == 'function' and declarations else {
            'name': path.stem, 'inputs': ['varargin'] if kind == 'class' else [],
            'outputs': ['object'] if kind == 'class' else [], 'signature': first}
        effects = sorted(k for k, pattern in EFFECTS.items() if re.search(pattern, code))
        gui = bool(re.search(r'\b(gui_mainfcn|uifigure|AC_buildCodeUI)\s*\(|matlab\.apps\.AppBase', code))
        role = ('gui' if gui else 'plotter' if re.search(r'(?i)^(plot|phaseplot|save.*fig|.*plot)', path.stem)
                and 'graphics' in effects else 'mixed' if set(effects) & {'graphics', 'gui_state', 'dialog', 'interaction'}
                else 'helper' if '/misc/' in relative else 'calculation')
        head_comments = []
        for line in text.splitlines()[:100]:
            if line.lstrip().startswith('%'):
                head_comments.append(line.lstrip()[1:].strip())
        entry = {'id': relative, 'name': path.stem, 'kind': kind, 'role': role,
                 'visibility': 'private' if '/private/' in relative else 'public',
                 'sha256': hashlib.sha256(raw).hexdigest(), 'lines': len(text.splitlines()),
                 **{k: public[k] for k in ('inputs', 'outputs', 'signature')},
                 'help': '\n'.join(head_comments)[:12000], 'effects': effects,
                 'declarations': declarations,
                 'call_names': sorted(set(re.findall(r'(?<![\w.])([A-Za-z]\w*)\s*\(', code))),
                 'interface': 'owner_only' if '/private/' in relative else 'script' if kind == 'script'
                    else 'gui' if gui else 'call',
                 'validation': 'source_indexed; MATLAB runtime not run in this fork'}
        entries.append(entry)
    names = {e['name']: e for e in entries}
    for e in entries:
        e['dependencies'] = sorted({names[n]['id'] for n in e.pop('call_names') if n in names and names[n]['id'] != e['id']})
    menus = []
    ac = (root / 'code/guicode/AC.m').read_text()
    # Menu label/tag bindings are code-generated in this revision.
    for m in re.finditer(r"handles\.(\w+)\s*=\s*uimenu\(handles\.(\w+),([\s\S]*?);", ac):
        label = re.search(r"'Label'\s*,\s*'([^']*)'", m[3])
        cb = re.search(r"AC_dispatch\('([^']+)'", m[3])
        if label:
            menus.append({'tag': m[1], 'parent': m[2], 'label': label[1], 'callback': cb[1] if cb else None,
                          'source': 'code/guicode/AC.m', 'line': ac[:m.start()].count('\n') + 1})
    return {'schema_version': 1, 'repository': 'mingsongli/acycle', 'revision': revision,
            'coverage_unit': 'every tracked .m file; menu bindings and local declarations are navigation, not headless claims',
            'summary': {'files': len(entries), 'kinds': dict(Counter(e['kind'] for e in entries)),
                        'interfaces': dict(Counter(e['interface'] for e in entries)),
                        'roles': dict(Counter(e['role'] for e in entries)), 'menu_bindings': len(menus)},
            'path_directories': sorted({str(Path(name).parent) for name in tracked
                                        if name and '/private/' not in name}),
            'resources': [{'id': name, 'sha256': hashlib.sha256((root / name).read_bytes()).hexdigest(),
                           'bytes': (root / name).stat().st_size}
                          for name in sorted(tracked) if name and not name.endswith('.m')],
            'entries': entries, 'menus': menus}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('acycle_root', type=Path)
    parser.add_argument('--output', type=Path, default=Path('matlab/native_catalog.json'))
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    catalog = build(args.acycle_root)
    content = json.dumps(catalog, ensure_ascii=False, indent=2) + '\n'
    if args.check:
        if args.output.read_text() != content:
            raise SystemExit('Catalog differs: review upstream changes and regenerate explicitly')
    else:
        args.output.write_text(content)
    print(json.dumps(catalog['summary'], ensure_ascii=False))


if __name__ == '__main__':
    main()
