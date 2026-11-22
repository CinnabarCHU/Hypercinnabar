"""Extract scoped MATLAB declarations and direct calls from the two pinned Git trees."""
import hashlib
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from audit_acycle import entry, resolve, visible_variables
from compare_guide_coupling import tree, blobs
from track_analysis_cores import SNAPSHOTS, parse_trace


ROOT = Path(__file__).resolve().parents[2]
EFFECTS = {
    'gui_input': 'ginput myginput inputdlg questdlg uigetfile uigetdir uiputfile listdlg uiselectcolor uiwait waitfor waitforbuttonpress',
    'gui_notice': 'errordlg warndlg msgbox helpdlg uialert',
    'gui_progress': 'waitbar uiprogressdlg uiprogressbar timedwaitbar getCanceling',
    'gui_state': 'getappdata setappdata rmappdata guidata gui_mainfcn guihandles uicontrol uimenu uifigure uiaxes uitable uipanel uigridlayout uibutton uieditfield uidropdown uicheckbox uislider uilabel uimulticomponent',
    'graphics': 'figure gcf gca axes subplot tiledlayout nexttile plot plot3 semilogx semilogy loglog imagesc image imshow contour contourf pcolor surface surf scatter scatter3 histogram bar errorbar patch fill line yyaxis legend colormap colorbar xlim ylim xlabel ylabel title hold cla gobjects isgraphics exportgraphics savefig printdlg',
    'workspace': 'assignin evalin',
    'cwd': 'cd chdir GETac_pwd CDac_pwd',
    'file_io': 'fopen fclose dlmwrite writetable writematrix writecell readtable readmatrix save saveas print load loadmat movefile copyfile delete mkdir rmdir xlswrite xlsread',
}
EFFECT_NAMES = {n: group for group, names in EFFECTS.items() for n in names.split()}
EXPLICIT = {'call_or_index', 'bare_name', 'command', 'literal_dispatch', 'function_handle'}


@lru_cache(maxsize=1)
def snapshots():
    import csv
    with (ROOT / 'migration/recovered.tsv').open() as f:
        recovered = list(csv.DictReader(f, delimiter='\t'))
    with (ROOT / 'migration/master/sources.tsv').open() as f:
        known_names = {Path(row['path']).stem for row in csv.DictReader(f,delimiter='\t')
                       if row['path'].endswith('.m')}
    known_names.update(Path(row['local_path']).stem for row in recovered)
    cache = {}
    all_facts = {}
    for revision, directory, pin in [('guide', 'acycle', SNAPSHOTS['guide']), ('master', 'master', SNAPSHOTS['current'])]:
        root = ROOT / 'upstream' / directory
        items = {p: oid for p, oid in tree(root, pin).items() if p.endswith('.m')}
        raw = blobs(root, set(items.values()))
        sources = {p: (pin, oid, raw[oid]) for p, oid in items.items()}
        if revision == 'guide':
            for row in recovered:
                p = row['local_path']
                content = (ROOT / p).read_bytes()
                assert hashlib.sha256(content).hexdigest() == row['sha256']
                sources[p] = (row['origin'], row['sha256'], content)
        exports = defaultdict(list)
        for p in sources:
            exports[Path(p).stem].append(entry(p))
        # A compatibility source has its own opt-in path policy. Keep it out of ordinary master lookup.
        if revision == 'master':
            p = 'upstream/compatibility/coco/freq2target.m'
            content = (ROOT / p).read_bytes()
            sources[p] = ('compatibility/b52ea9f', hashlib.sha256(content).hexdigest(), content)

        facts = {}
        for path, (origin, oid, content) in sorted(sources.items()):
            key = (path, oid)
            if key not in cache:
                collector, _ = parse_trace(path, content)
                cache[key] = collector
            c = cache[key]
            seen_vars = {}
            nodes = {ident: [n['name'], n['parent'], n['kind'], n['line'], n['end_line']]
                     for ident, n in c.nodes.items()}
            effects, edges, ambiguous, dynamic, missing = set(), set(), set(), set(), set()
            for ref in c.refs:
                st, name, kind, ln = ref['source'], ref['name'], ref['kind'], ref['line']
                if kind not in EXPLICIT:
                    continue
                if st not in seen_vars:
                    seen_vars[st] = visible_variables(c, st)
                if kind in ('bare_name','call_or_index') and name in seen_vars[st]:
                    continue
                if name in EFFECT_NAMES and kind != 'function_handle':
                    effects.add((st, ln, EFFECT_NAMES[name], name))
                if name not in exports:
                    if name in known_names and kind in {'call_or_index','command','literal_dispatch','function_handle'}:
                        if not resolve(ref,c,{}):
                            missing.add((st, ln, name))
                    continue
                targets = resolve(ref, c, exports)
                outside = [t.split('::',1)[0] for t in targets if t.endswith('::<file>') and not t.startswith(path + '::')]
                if len(outside) == 1:
                    edges.add((st, ln, kind, outside[0]))
                elif len(outside) > 1:
                    ambiguous.add((st, ln, name, '|'.join(sorted(outside))))
            for call in c.calls:
                if call['name'] in {'feval','str2func','run','eval','evalin','builtin'} and not (
                    call['args'] and call['args'][0] and call['name'] in {'feval','str2func','run'}):
                    dynamic.add((call['source'],call['line'],call['name']))
            facts[path] = dict(origin=origin, blob=oid, kind=c.kind, nodes=nodes, effects=sorted(effects),
                               edges=sorted(edges), ambiguous=sorted(ambiguous), dynamic=sorted(dynamic),
                               missing=sorted(missing))
        all_facts[revision] = facts
    return all_facts
