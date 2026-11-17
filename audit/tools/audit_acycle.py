#!/usr/bin/env python3
"""Reproducible, conservative MATLAB source inventory; never executes MATLAB.

The graph records syntactic evidence, not a proof of runtime reachability.
MISS_HIT parses comments, strings, scopes, command syntax and nested functions.
Private lookup and local scopes are considered; runtime object dispatch, eval,
workspace injection and the MATLAB/toolbox path are not fully resolved.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import contextlib
import csv
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import re
import subprocess

from miss_hit_core import m_ast as A
from miss_hit_core.config import Config
from miss_hit_core.errors import Message_Handler
from miss_hit_core.m_lexer import MATLAB_Lexer
from miss_hit_core.m_parser import MATLAB_Parser


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def write_csv(path, rows, columns):
    with path.open('w', newline='', encoding='utf-8') as out:
        writer = csv.DictWriter(out, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                             for k, v in row.items() if k in columns})


def entry(path):
    return path + '::<file>'


def literal(node):
    if isinstance(node, (A.Char_Array_Literal, A.String_Literal)):
        return node.t_string.value
    return None


def display(node):
    # MISS_HIT omits __str__ for some containers; never persist memory addresses.
    return re.sub(r'<miss_hit_core\.m_ast\.(\w+) object at 0x[0-9a-f]+>', r'<\1>', str(node))


def atoms(node):
    values = []
    class V(A.AST_Visitor):
        def visit(self, n, parent, relation):
            if literal(n) is not None:
                values.append(literal(n))
            elif isinstance(n, A.Function_Pointer):
                values.append(str(n.n_name))
    node.visit(None, V(), 'Root')
    return values


def base_name(node):
    """Root variable of an assignment, not its field or indexing arguments."""
    if isinstance(node, A.Identifier):
        return str(node)
    for attr in ('n_ident', 'n_prefix'):
        if hasattr(node, attr):
            return base_name(getattr(node, attr))
    return str(node).split('.')[0].split('(')[0].split('{')[0]


class Collect(A.AST_Visitor):
    def __init__(self, path, kind):
        self.path, self.kind = path, kind
        self.nodes = {entry(path): dict(id=entry(path), path=path, name='<file>',
                     parent=None, kind=kind, line=1, end_line=1, inputs=[], outputs=[], empty=False)}
        self.stack = [entry(path)]
        self.variables = defaultdict(set)
        self.refs, self.strings, self.calls, self.constant_conditions = [], [], [], []
        self.menus = []

    def visit(self, n, parent, relation):
        if isinstance(n, A.Function_Definition):
            name = str(n.n_sig.n_name)
            ident = f'{self.path}::{name}@{n.loc().line}'
            scope = self.stack[-1]
            if isinstance(parent, A.Special_Block):
                kind = 'method'
            elif isinstance(parent, A.Function_Definition):
                kind = 'nested'
            else:
                kind = 'function'
            self.nodes[ident] = dict(id=ident, path=self.path, name=name, parent=scope,
                kind=kind, line=n.loc().line, end_line=n.t_end.location.line if n.t_end else n.loc().line,
                inputs=list(map(str, n.n_sig.l_inputs)), outputs=list(map(str, n.n_sig.l_outputs)),
                empty=not n.n_body.l_statements)
            self.stack.append(ident)
            self.variables[ident].update(self.nodes[ident]['inputs'] + self.nodes[ident]['outputs'])
        current = self.stack[-1]
        try:
            line = n.loc().line or self.nodes[current]['line']
        except Exception:
            line = self.nodes[current]['line']
        for ident in self.stack:
            self.nodes[ident]['end_line'] = max(line, self.nodes[ident]['end_line'])
        if isinstance(n, A.Simple_Assignment_Statement):
            self.variables[current].add(base_name(n.n_lhs))
        elif isinstance(n, A.Compound_Assignment_Statement):
            self.variables[current].update(base_name(x) for x in n.l_lhs)
        elif isinstance(n, A.For_Loop_Statement):
            self.variables[current].add(str(n.n_ident))
        elif isinstance(n, (A.Global_Statement, A.Persistent_Statement)):
            self.variables[current].update(map(str, n.l_names))
        if isinstance(n, (A.Reference, A.Function_Call)):
            if relation == 'LHS':
                return
            name = str(n.n_ident if isinstance(n, A.Reference) else n.n_name)
            kind = 'command' if isinstance(n, A.Function_Call) and n.variant == 'command' else 'call_or_index'
            self.refs.append(dict(source=current, name=name, line=line, kind=kind))
            args = [literal(x) for x in n.l_args]
            self.calls.append(dict(source=current, name=name, line=line, args=args,
                                   expression=display(n)[:200]))
            if name == 'uimenu' and self.path == 'code/guicode/AC.m':
                props = {}
                for i in range(1, len(n.l_args)-1, 2):
                    if args[i]:
                        props[args[i]] = args[i+1] if args[i+1] is not None else display(n.l_args[i+1])
                        if args[i] == 'Callback':
                            values = atoms(n.l_args[i+1])
                            callbacks = [v for v in values if v.endswith('_Callback')]
                            if callbacks:
                                props[args[i]] = callbacks[0]
                callback = props.get('Callback', '')
                match = re.search(r"AC_dispatch\('([^']+)'", callback)
                self.menus.append(dict(line=line, handle=str(parent.n_lhs) if isinstance(parent, A.Simple_Assignment_Statement) else '',
                    parent=str(n.l_args[0]), label=props.get('Label',''), tag=props.get('Tag',''),
                    own_visible=props.get('Visible','on'), callback=match[1] if match else callback))
            if name in ('feval', 'str2func', 'run') and args and args[0]:
                self.refs.append(dict(source=current, name=Path(args[0]).stem, line=line, kind='literal_dispatch'))
            if name in ('help', 'type') and args and args[0]:
                self.refs.append(dict(source=current, name=Path(args[0]).stem, line=line, kind='source_documentation'))
        elif isinstance(n, A.Function_Pointer):
            self.refs.append(dict(source=current, name=str(n.n_name), line=line, kind='function_handle'))
        elif isinstance(n, A.Identifier):
            # A no-argument function/script can appear in expression or command position.
            # Exclude signatures, property/field names and assignment targets.
            if (relation not in ('Name', 'LHS', 'Inputs', 'Outputs', 'Names', 'Ident')
                    and not isinstance(parent, (A.Function_Signature, A.Selection))):
                self.refs.append(dict(source=current, name=str(n), line=line, kind='bare_name'))
        if literal(n) is not None:
            value = literal(n)
            self.strings.append(dict(source=current, line=line, value=value))
            # Conservative possible edge. This can be a callback, a dispatch key,
            # an existence check or data: it is NOT labelled a proven call.
            if re.fullmatch(r'[A-Za-z]\w*', value):
                self.refs.append(dict(source=current, name=value, line=line, kind='symbol_literal_possible'))
        conditional = isinstance(parent, A.While_Statement) or (isinstance(parent, A.Action) and parent.kind() in ('if','elseif'))
        if conditional and isinstance(n, (A.Number_Literal, A.Identifier)) and relation == 'Guard' and str(n) in ('0','false'):
            self.constant_conditions.append(dict(source=current, line=line, expression=str(n)))

    def visit_end(self, n, parent, relation):
        if isinstance(n, A.Function_Definition):
            self.stack.pop()


def parse_source(path, text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    cfg = Config()
    mh = Message_Handler('debug')
    mh.register_file(path)
    with contextlib.redirect_stdout(io.StringIO()):
        ast = MATLAB_Parser(mh, MATLAB_Lexer(cfg.language, mh, text, path), cfg).parse_file()
    kind = {'Function_File':'function_file', 'Class_File':'class_file', 'Script_File':'script'}[type(ast).__name__]
    collector = Collect(path, kind)
    ast.visit(None, collector, 'Root')
    return collector


def visible_variables(collector, ident):
    names = set()
    while ident:
        names.update(collector.variables[ident])
        ident = collector.nodes[ident]['parent']
    return names


def resolve(ref, collector, exports):
    source, name = ref['source'], ref['name']
    if ref['kind'] in ('call_or_index', 'bare_name') and name in visible_variables(collector, source):
        return []
    # Local and nested functions: search lexical ancestors and their children.
    scope = source
    while scope:
        matches = [n['id'] for n in collector.nodes.values()
                   if n['name'] == name and n['parent'] == scope]
        if matches:
            return matches
        if collector.nodes[scope]['name'] == name:
            return [scope]
        scope = collector.nodes[scope]['parent']
    # app.method(...) and Class.method(...): conservatively match own class methods.
    if collector.kind == 'class_file' and '.' in name:
        matches = [n['id'] for n in collector.nodes.values()
                   if n['kind'] == 'method' and n['name'] == name.split('.')[-1]]
        if matches:
            return matches
    # A data string such as unit='ft' must not create a dependency on ft.m.
    # External literal dispatch is handled only at call sites with known targets.
    if ref['kind'] == 'symbol_literal_possible':
        return []
    matches = exports.get(name, [])
    allowed = []
    for target in matches:
        target_path = target.split('::')[0]
        if '/private/' in target_path:
            owner = target_path.split('/private/')[0]
            # Only functions in private's direct parent and private itself see it.
            if str(Path(collector.path).parent) not in (owner, owner+'/private'):
                continue
        allowed.append(target)
    private = [t for t in allowed if '/private/' in t]
    return private or allowed


def reachability(roots, edges):
    graph = defaultdict(set)
    for edge in edges:
        graph[edge['source']].add(edge['target'])
    seen, queue = set(roots), deque(roots)
    while queue:
        for target in sorted(graph[queue.popleft()]):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def branch_inventory(root):
    rows = []
    # Full refs avoid Git shortening origin/HEAD to the alias "origin".
    refs = git(root,'for-each-ref','--format=%(refname)','refs/remotes/origin/').splitlines()
    for ref in refs:
        if ref == 'refs/remotes/origin/HEAD':
            continue
        sha = git(root, 'rev-parse', ref)
        behind, ahead = map(int, git(root, 'rev-list','--left-right','--count', f'origin/master...{ref}').split())
        rows.append(dict(branch=ref.removeprefix('refs/remotes/origin/'), commit=sha,
            tree=git(root,'rev-parse',ref+'^{tree}'), date=git(root,'show','-s','--format=%cI',ref),
            subject=git(root,'show','-s','--format=%s',ref), ahead_of_master=ahead, behind_master=behind,
            changed_paths=git(root,'diff','--name-only','origin/master',ref).splitlines()))
    return rows


EFFECTS = {
 'gui': {'uifigure','uicontrol','uilabel','uibutton','uimenu','guidata','gui_mainfcn','createCallbackFcn','uiwait','waitfor'},
 'plot': {'figure','plot','subplot','axes','imagesc','contour','surf','pcolor','yyaxis','errorbar','scatter','patch','bar'},
 'dialog': {'inputdlg','questdlg','uigetfile','uiputfile','uigetdir','listdlg','ginput','myginput','input','waitforbuttonpress'},
 'workspace': {'assignin','evalin','eval','global','cd','clear'},
 'io': {'load','save','readmatrix','readtable','writematrix','writetable','fopen','xlsread','xlswrite','importdata','imread','imwrite','websave','urlwrite','copyfile','delete'},
 'parallel': {'parfeval','parpool','gcp'},
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('upstream/acycle'))
    parser.add_argument('--output', type=Path, default=Path('audit/reports'))
    parser.add_argument('--config', type=Path, default=Path('audit/decisions.json'))
    args = parser.parse_args()
    root, out = args.source.resolve(), args.output
    out.mkdir(parents=True, exist_ok=True)
    config = json.loads(args.config.read_text())
    files = git(root, 'ls-files').splitlines()
    pin = git(root, 'rev-parse', 'HEAD')
    if config.get('source_commit') != pin:
        raise SystemExit('Source pin differs from decisions.json; review decisions before updating the baseline.')
    stale_files = set(config.get('file_decisions', {})) - set(files)
    if stale_files:
        raise SystemExit(f'Stale file decisions: {sorted(stale_files)}')
    if git(root, 'status', '--porcelain', '--untracked-files=no'):
        raise SystemExit('Source has modified tracked files; audit a clean snapshot.')
    nodes, collectors, failures, refs, calls, strings = {}, {}, [], [], [], []
    parser_adaptations = []
    for path in files:
        if not path.endswith('.m'):
            continue
        try:
            raw = (root/path).read_bytes()
            try:
                text = raw.decode('utf-8-sig')
            except UnicodeDecodeError:
                text = raw.decode('latin-1')
                parser_adaptations.append(dict(path=path, adaptation='Latin-1 fallback for legacy source comments'))
            if path in config.get('d_exponent_parser_adapters', []):
                text, count = re.subn(r'(?<![\w.])(\d+(?:\.\d*)?|\.\d+)[dD]([+-]?\d+)(?!\w)',
                                      r'\1e\2', text)
                parser_adaptations.append(dict(path=path, adaptation='D exponent to E in analysis buffer only', count=count))
            c = parse_source(path, text)
            collectors[path] = c
            nodes.update(c.nodes)
            refs.extend(c.refs)
            calls.extend(c.calls)
            strings.extend(c.strings)
        except Exception as exc:
            failures.append(dict(path=path, error=f'{type(exc).__name__}: {exc}'))
    if failures:
        write_json(out/'parse_failures.json', failures)
        raise SystemExit(f'Incomplete parse: {len(failures)} files; see parse_failures.json')
    (out/'parse_failures.json').unlink(missing_ok=True)
    exports = defaultdict(list)
    known_blocks = {n['path']+'::'+n['name'] for n in nodes.values()}
    stale_blocks = set(config.get('block_decisions', {})) - known_blocks
    if stale_blocks:
        raise SystemExit(f'Stale block decisions: {sorted(stale_blocks)}')
    for path in collectors:
        exports[Path(path).stem].append(entry(path))
    edges = []
    def edge(source, target, line, kind):
        edges.append(dict(source=source, target=target, line=line, kind=kind))
    for path, c in collectors.items():
        children = [n for n in c.nodes.values() if n['parent'] == entry(path)]
        if c.kind == 'function_file' and children:
            edge(entry(path), children[0]['id'], children[0]['line'], 'file_entry')
        elif c.kind == 'class_file':
            for n in children:
                edge(entry(path), n['id'], n['line'], 'class_method_possible')
        for ref in c.refs:
            for target in resolve(ref, c, exports):
                edge(ref['source'], target, ref['line'], ref['kind'])
    for call in calls:
        # GUIDE-compatible Foo('callback',...) external dispatch.
        if not call['args'] or not call['args'][0]:
            continue
        for target_entry in exports.get(call['name'], []):
            target_collector = collectors[nodes[target_entry]['path']]
            for n in target_collector.nodes.values():
                if n['name'] == call['args'][0]:
                    edge(call['source'], n['id'], call['line'], 'external_literal_callback')
    # Reviewed dynamic constructions with evidence; kept separate from parser logic.
    for item in config.get('dynamic_edges', []):
        c = collectors[item['path']]
        source = next(n['id'] for n in c.nodes.values() if n['name'] == item['source'])
        for target_name in item['targets']:
            targets = [n['id'] for n in c.nodes.values() if n['name'] == target_name]
            if not targets:
                raise ValueError(f'Stale dynamic-edge decision: {target_name}')
            for target in targets:
                edge(source, target, item['line'], 'reviewed_dynamic')
    # GUIDE .fig files are MATLAB containers, not executable .m text. Extract only
    # callback character strings with scipy; never instantiate graphics objects.
    fig_callbacks = []
    from scipy.io import loadmat
    import numpy as np
    def walk_mat(value):
        if isinstance(value, str):
            yield value
        elif hasattr(value, '_fieldnames'):
            for field in value._fieldnames:
                yield from walk_mat(getattr(value, field))
        elif isinstance(value, dict):
            for key, child in value.items():
                if not key.startswith('__'):
                    yield from walk_mat(child)
        elif isinstance(value, np.ndarray):
            if value.dtype.kind in ('U','S'):
                yield str(value.item()) if value.size == 1 else ''.join(str(v) for v in value.flat)
            elif value.dtype.kind == 'O':
                for child in value.flat:
                    yield from walk_mat(child)
    for path in files:
        if not path.endswith('.fig'):
            continue
        owner = str(Path(path).with_suffix('.m'))
        if owner not in collectors:
            continue
        values = sorted(set(walk_mat(loadmat(root/path, struct_as_record=False, squeeze_me=True))))
        for value in values:
            for name in re.findall(r"['\"]([A-Za-z]\w*(?:Callback|CreateFcn|OpeningFcn|OutputFcn|CloseRequestFcn))['\"]", value):
                matches = [n for n in collectors[owner].nodes.values() if n['name'] == name]
                fig_callbacks.append(dict(asset=path, owner=owner, callback=name, resolved=bool(matches), expression=value))
                for n in matches:
                    edge(entry(owner), n['id'], n['line'], 'fig_callback')
    edges = [dict(zip(('source','target','line','kind'), row)) for row in
             sorted({(e['source'], e['target'], e['line'], e['kind']) for e in edges})]
    desktop_roots = [entry(p) for p in config['desktop_roots']]
    api_roots = [entry(p) for p in config['api_roots']]
    optional_roots = [entry(p) for p in config.get('optional_roots', [])]
    assert all(r in nodes for r in desktop_roots + api_roots + optional_roots)
    desktop = reachability(desktop_roots, edges)
    api = reachability(api_roots, edges)
    optional = reachability(optional_roots, edges)
    incoming = defaultdict(list)
    for e in edges:
        incoming[e['target']].append(e)
    file_by_node = {key:n['path'] for key,n in nodes.items()}
    file_edges = defaultdict(set)
    for e in edges:
        source, target = file_by_node[e['source']], file_by_node[e['target']]
        if source != target:
            file_edges[(source,target)].add(e['kind'])
    desktop_files = {nodes[n]['path'] for n in desktop}
    api_files = {nodes[n]['path'] for n in api}
    optional_files = {nodes[n]['path'] for n in optional}
    calls_by_path = defaultdict(set)
    for call in calls:
        calls_by_path[nodes[call['source']]['path']].add(call['name'])
    manifest = []
    for path in files:
        data = (root/path).read_bytes()
        callers = sorted({s for s,t in file_edges if t == path})
        row = dict(path=path, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                   kind=collectors[path].kind if path in collectors else 'resource',
                   desktop_possible=path in desktop_files, api_possible=path in api_files,
                   optional_possible=path in optional_files,
                   incoming_files=callers, effects=[], category='', decision='', evidence='')
        if path in collectors:
            row['effects'] = sorted(k for k,v in EFFECTS.items() if v & calls_by_path[path])
            row['lines'] = len(data.splitlines())
            row['declarations'] = len(collectors[path].nodes)-1
            if path in desktop_files:
                row.update(category='desktop_dependency', decision='retain_review_boundary')
            elif path in api_files:
                row.update(category='api_dependency', decision='retain_api')
            elif path in optional_files:
                row.update(category='optional_dependency', decision='retain_optional')
            else:
                row.update(category='unreached_candidate', decision='review_no_delete')
            row['evidence'] = 'Conservative AST graph; consult edges.csv and unresolved_dynamic.csv.'
        else:
            row.update(category='resource_review', decision='retain_until_resource_audit', evidence='Not analysed as MATLAB code.')
        if path in config.get('file_decisions', {}):
            row.update(config['file_decisions'][path])
        manifest.append(row)
    for n in nodes.values():
        n['desktop_possible'] = n['id'] in desktop
        n['api_possible'] = n['id'] in api
        n['incoming_count'] = len(incoming[n['id']])
    dynamic = [dict(path=nodes[c['source']]['path'], **c) for c in calls
               if c['name'] in ('eval','evalin','feval','str2func','run','assignin')
               and not (c['name'] in ('feval','str2func','run') and c['args'] and c['args'][0])]
    menus = [m for m in collectors['code/guicode/AC.m'].menus if m['handle'] != 'handles.(key)']
    menus += config.get('dynamic_menus', [])
    by_handle = {m['handle']:m for m in menus}
    for m in menus:
        m['ancestor_hidden'] = False
        parent = m['parent']
        visited = set()
        while parent in by_handle and parent not in visited:
            visited.add(parent)
            if by_handle[parent]['own_visible'] == 'off':
                m['ancestor_hidden'] = True
            parent = by_handle[parent]['parent']
        m['resolved'] = any(n['name'] == m['callback'] for n in collectors['code/guicode/AC.m'].nodes.values()) if m['callback'] else None
    block_candidates = []
    for n in nodes.values():
        if n['name'] == '<file>' or n['path'] not in desktop_files or n['desktop_possible']:
            continue
        row = dict(n, decision='review_external_or_legacy_dispatch', evidence='Not in conservative desktop closure; external dispatch remains possible.')
        key = n['path'] + '::' + n['name']
        row.update(config.get('block_decisions', {}).get(key, {}))
        block_candidates.append(row)
    resources = []
    for s in strings:
        for path in files:
            if path.endswith('.m'):
                continue
            # Full path or filename equality is stronger than substring matching.
            if s['value'] in (path, Path(path).name):
                resources.append(dict(resource=path, source=s['source'], line=s['line'], evidence=s['value']))
    branch_rows = branch_inventory(root)
    if config.get('cleanup_commit'):
        cleanup = git(root,'rev-parse',config['cleanup_commit'])
        parent = git(root,'rev-parse',cleanup+'^')
        removed = []
        for row in git(root,'diff','--name-status',parent,cleanup).splitlines():
            status, path = row.split('\t')
            category = 'production_edit' if status != 'D' else 'backup_archive' if path.endswith('.bak') else 'historical_validation'
            removed.append(dict(path=path, change=status, category=category,
                recover_from=parent if status=='D' else '',
                source_url=f'https://github.com/mingsongli/acycle/blob/{parent}/{path}'))
        write_json(out/'release_cleanup.json', dict(cleanup_commit=cleanup,parent_commit=parent,
            counts=dict(Counter(x['category'] for x in removed)),files=removed))
    summary = dict(audit_date=config['audit_date'], upstream='https://github.com/mingsongli/acycle',
        commit=pin, tree=git(root,'rev-parse','HEAD^{tree}'), branches=branch_rows,
        tracked_files=len(files), matlab_files=len(collectors), parsed_files=len(collectors), parse_failures=failures,
        parser_adaptations=parser_adaptations,
        declarations=len(nodes)-len(collectors), edges=len(edges), cross_file_pairs=len(file_edges),
        desktop_possible_files=len(desktop_files), api_possible_files=len(api_files),
        optional_possible_files=len(optional_files),
        unreached_files=sorted(set(collectors)-desktop_files-api_files-optional_files),
        categories=dict(Counter(r['category'] for r in manifest)),
        fig_callbacks=len(fig_callbacks), unresolved_dynamic_sites=len(dynamic),
        menus=len(menus), menu_callbacks=sum(bool(m['callback']) for m in menus),
        dangling_menu_callbacks=[m for m in menus if m['callback'] and not m['resolved']],
        roots=dict(desktop=config['desktop_roots'], api=config['api_roots'], optional=config.get('optional_roots', [])),
        versions={p:importlib.metadata.version(p) for p in ('miss-hit','scipy')},
        limitations=['Conservative syntactic reachability, not a call trace or dead-code proof.',
        'Class methods are retained conservatively; object types and event dispatch are not inferred.',
        'Symbol strings create possible edges; runtime branches and platform conditions are not evaluated.',
        'Eval, injected workspace variables, external callers and arbitrary MATLAB path shadowing remain open.',
        'No MATLAB, scientific equivalence, GUI or MEX execution was performed.'])
    write_json(out/'summary.json', summary)
    write_json(out/'manifest.json', manifest)
    native_edges = []
    for call in calls:
        for path in files:
            if not Path(path).suffix.startswith('.mex') or Path(path).stem != call['name']:
                continue
            caller_path = nodes[call['source']]['path']
            owner = path.split('/private/')[0] if '/private/' in path else None
            if owner and str(Path(caller_path).parent) not in (owner,owner+'/private'):
                continue
            native_edges.append(dict(source=call['source'],resource=path,line=call['line'],kind='platform_dependent_mex'))
    write_csv(out/'native_dependencies.csv', native_edges, ['source','resource','line','kind'])
    write_csv(out/'migration_inventory.csv', manifest, ['path','kind','category','decision','desktop_possible','api_possible','optional_possible','incoming_files','effects','lines','declarations','bytes','sha256','evidence'])
    write_csv(out/'symbols.csv', sorted(nodes.values(),key=lambda n:(n['path'],n['line'],n['id'])), ['id','path','name','parent','kind','line','end_line','inputs','outputs','empty','desktop_possible','api_possible','incoming_count'])
    write_csv(out/'edges.csv', edges, ['source','target','line','kind'])
    write_csv(out/'file_edges.csv', [dict(source=s,target=t,kinds=sorted(k)) for (s,t),k in sorted(file_edges.items())], ['source','target','kinds'])
    write_csv(out/'unresolved_dynamic.csv', dynamic, ['path','source','line','name','expression'])
    write_csv(out/'resource_references.csv', resources, ['resource','source','line','evidence'])
    write_json(out/'fig_callbacks.json', fig_callbacks)
    write_csv(out/'menus.csv', menus, ['line','handle','parent','label','tag','own_visible','ancestor_hidden','callback','resolved'])
    write_csv(out/'block_candidates.csv', sorted(block_candidates,key=lambda n:(n['path'],n['line'])), ['path','name','line','end_line','empty','incoming_count','decision','evidence'])
    write_json(out/'constant_conditions.json', [dict(path=p,**row) for p,c in collectors.items() for row in c.constant_conditions])
    write_json(out/'empty_functions.json', [n for n in nodes.values() if n['empty']])
    print(json.dumps({k:summary[k] for k in ('matlab_files','declarations','edges','desktop_possible_files','api_possible_files','unreached_files','categories')},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
