"""Rebuild or verify the feature comparison, both submodule pins and copied MATLAB sections."""
import argparse
import csv
import io
import re
import subprocess
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from scipy.io import loadmat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GUIDE = ROOT / 'upstream/acycle'
MASTER = ROOT / 'upstream/master'
BASE_PIN = 'b52ea9f510f3be00bde9a0238b9898a1e2315b74'
MASTER_PIN = 'dcba4279168745b563e0535b954297023dd62fc7'
SECTION = re.compile(r'^%% Copied from mingsongli/acycle@' + MASTER_PIN + r' (.+):L(\d+)-L(\d+)$')


def read_rows(file, delimiter='\t'):
    with file.open(encoding='utf8', newline='') as f:
        return list(csv.DictReader(f, delimiter=delimiter))


def git(directory, *args):
    return subprocess.check_output(['git', '-C', str(directory), *args], text=True)


def pinned_tree(directory, expected):
    assert git(directory, 'rev-parse', 'HEAD').strip() == expected, directory
    items = git(directory, 'ls-tree', '-r', '-z', 'HEAD').rstrip('\0').split('\0')
    return {path: meta.split()[2] for meta, path in (i.split('\t', 1) for i in items)}


def compare_tsv(filename, columns, rows, write):
    out = io.StringIO()
    writer = csv.writer(out, delimiter='\t', lineterminator='\n')
    writer.writerow(columns)
    writer.writerows(rows)
    file = HERE / filename
    if write:
        file.write_text(out.getvalue(), encoding='utf8')
    else:
        assert file.read_text(encoding='utf8') == out.getvalue(), f'Stale {filename}: run compare.py --write'


@lru_cache(None)
def lines(path):
    return (MASTER / path).read_bytes().decode('utf-8-sig', errors='replace').splitlines()


def verify_roles():
    listed = {(r['package'], r['role']): r for r in read_rows(HERE/'methods.tsv')}
    found = set()
    by_source = defaultdict(set)
    count = 0
    for file in sorted((ROOT/'matlab/+acmaster').glob('+*/*.m')):
        method, role = file.parent.name[1:], file.stem
        found.add((method, role))
        entry = listed[method, role]
        code = file.read_text(encoding='utf8').splitlines()
        assert role in {'helper','analyzer','plotter'}
        assert any(f"'{method}-v3.1.1+dcba427/{role}'" in l for l in code), file
        assert not any('acmethods.' in l for l in code if not l.lstrip().startswith('%')), file
        source_links = [l.split(MASTER_PIN+'/',1)[1].split('#')[0] for l in code if l.startswith('% Source: ')]
        assert set(source_links) == set(entry['source_files'].split()), file
        markers = 0
        for path in source_links:
            assert (MASTER/path).is_file(), path
            by_source[path].add(method+'.'+role)
        for i, line in enumerate(code):
            if not line.startswith('%% Copied from'):
                continue
            match = SECTION.fullmatch(line)
            assert match, (file, i+1)
            path, first, last = match.groups()
            first, last = int(first), int(last)
            original = lines(path)
            assert 1 <= first <= last <= len(original), (file, line)
            assert code[i+1:i+2+last-first] == original[first-1:last], (file, line)
            assert code[i+2+last-first] == '%% End copied source', (file, line)
            markers += 1
            by_source[path].add(method+'.'+role)
        assert markers == code.count('%% End copied source'), file
        count += markers
    assert found == set(listed)
    return listed, by_source, count


def guide_visibility():
    raw = loadmat(GUIDE/'code/guicode/AC.fig', simplify_cells=True)
    tree = raw[next(k for k in raw if k.startswith('hgS'))]
    result = {}

    def visit(node, visible):
        if not isinstance(node, dict):
            if isinstance(node, (list, tuple)):
                for child in node:
                    visit(child, visible)
            elif hasattr(node, 'flat'):
                for child in node.flat:
                    visit(child, visible)
            return
        props = node['properties']
        visible = visible and props.get('Visible','on') != 'off'
        if node.get('type') == 'uimenu':
            result[props['Tag']] = 'visible' if visible else 'hidden'
        visit(node.get('children', []), visible)

    visit(tree, True)
    return result


def source_inventory(old, new, references, write):
    data = []
    for path in sorted(old.keys() | new.keys()):
        status = ('added' if path not in old else 'removed' if path not in new else
                  'same' if old[path] == new[path] else 'modified')
        portable = ' '.join(sorted(references[path]))
        data.append([path,status,old.get(path,''),new.get(path,''),portable])
    compare_tsv('sources.tsv',['path','status','guide_blob','master_blob','directly_referenced_master_roles'],data,write)
    return Counter(r[1] for r in data)


def menu_inventory(roles, write):
    base = {r['guide_tag']:r for r in read_rows(HERE.parent/'menus.tsv')}
    current = {r['tag']:r for r in read_rows(ROOT/'audit/reports/menus.csv', ',')}
    vis = guide_visibility()
    assert set(vis) == set(base)
    evidence = read_rows(HERE/'features.tsv')
    notes = {}
    known = {method for method, _ in roles}
    for row in evidence:
        for source in row['evidence'].split():
            assert (MASTER/source).is_file(), source
        for method in row['master_packages'].split():
            assert method in known, method
        for tag in row['guide_tags'].split():
            assert tag in base or tag in current, tag
            assert tag not in notes, tag
            notes[tag] = row
    paths = {}
    def path(tag):
        if tag not in paths:
            row = current[tag]
            parent = row['parent'].removeprefix('handles.')
            paths[tag] = (path(parent)+' > ' if parent in current else '') + row['label']
        return paths[tag]
    rows = []
    for tag in sorted(base.keys() | current.keys()):
        b, n = base.get(tag,{}), current.get(tag,{})
        gv = vis.get(tag,'absent')
        mv = ('hidden' if n['own_visible']=='off' or n['ancestor_hidden']=='True' else 'visible') if n else 'absent'
        if n:
            decl = int(n['line'])
            near = '\n'.join(lines('code/guicode/AC.m')[max(0,decl-10):decl+3])
            assert tag in near or (tag in {'menu_log10','menu_norm','menu_utilities'} and 'menu_log10' in near), (tag,decl)
        desc = notes.get(tag,{})
        old_methods = b.get('packages','').split()
        choices = desc.get('master_packages','').split()
        if n and n.get('callback'):
            choices = list(dict.fromkeys([x for x in old_methods if x in known]+choices))
        if not n:
            choices = desc.get('master_packages','').split()
        numerical = [x for x in choices if x!='Desktop']
        if b and n:
            entry = 'visibility changed' if gv!=mv else 'retained'
        else:
            entry = 'new declaration' if n else 'old declaration only'
        native = ('heading' if not n.get('callback') else
                  'hidden declaration' if mv=='hidden' else
                  'acmaster.Desktop.plotter') if n else 'GUIDE source'
        rows.append([tag,b.get('menu_path',''),gv,path(tag) if n else '',mv,entry,b.get('source',''),
                     ('code/guicode/AC.m:'+n['line']) if n else '',n.get('callback',''),
                     ' '.join(old_methods),' '.join(numerical),native,
                     desc.get('feature',''),desc.get('change','')])
    compare_tsv('menus.tsv',['tag','guide_menu','guide_initial','master_menu','master_initial','declaration',
                'guide_source','master_source','master_callback','guide_packages','master_related_packages',
                'native_route','feature','observed_change'],rows,write)
    return Counter((r[2],r[4]) for r in rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    old, new = pinned_tree(GUIDE,BASE_PIN), pinned_tree(MASTER,MASTER_PIN)
    roles, references, sections = verify_roles()
    print('Repository tree:', dict(source_inventory(old,new,references,args.write)))
    print('Menu visibility:', dict(menu_inventory(roles,args.write)))
    print(f'{len(set(k[0] for k in roles))} master packages, {len(roles)} roles, {sections} exact sections.')

