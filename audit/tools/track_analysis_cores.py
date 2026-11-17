#!/usr/bin/env python3
"""Trace pinned Acycle core history and direct dependencies; no MATLAB execution.

Keep the original audit reports immutable. Supplement their graph with a
collector that distinguishes assignment LHS from binary-expression LHS.
Changes are source changes, not demonstrated changes of numerical results.
"""
import argparse
from collections import Counter, defaultdict
import contextlib
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

from audit_acycle import (A, Collect, Config, Message_Handler, MATLAB_Lexer,
    MATLAB_Parser, entry, resolve, reachability, visible_variables, write_csv,
    write_json)
from compare_guide_coupling import tree, blobs, production

SNAPSHOTS = {
    'guide': 'b52ea9f510f3be00bde9a0238b9898a1e2315b74',
    'release_3_0': '083c949e5635fefb6a2227273c49329a0891147a',
    'before_cores': '1ed99c8142753fce1bd2deb4f73ae150407757cb',
    'core_commit': '885c742de1d582c4b56afc6aab083f412f8bd373',
    'current': 'dcba4279168745b563e0535b954297023dd62fc7',
}
COMPARISONS = [('guide','current'), ('release_3_0','current'),
               ('before_cores','core_commit'), ('core_commit','current')]


class TraceCollect(Collect):
    def visit(self, node, parent, relation):
        # MISS_HIT also calls the left operand of a binary expression LHS.
        # e.g. fft(x).*gain is a call, whereas x(i)=value is an assignment.
        if relation == 'LHS' and not isinstance(parent,
                (A.Simple_Assignment_Statement, A.Compound_Assignment_Statement)):
            relation = 'ExpressionLeft'
        super().visit(node, parent, relation)


def parse_trace(path, raw):
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('latin-1')
    text = text.replace('\r\n','\n').replace('\r','\n')
    if path.startswith('code/package/swa/'):
        import re
        text = re.sub(r'(?<![\w.])(\d+(?:\.\d*)?|\.\d+)[dD]([+-]?\d+)(?!\w)',
                      r'\1e\2', text)
    cfg = Config()
    mh = Message_Handler('debug')
    mh.register_file(path)
    with contextlib.redirect_stdout(io.StringIO()):
        ast = MATLAB_Parser(mh, MATLAB_Lexer(cfg.language,mh,text,path),cfg).parse_file()
    kind = {'Function_File':'function_file','Class_File':'class_file',
            'Script_File':'script'}[type(ast).__name__]
    result = TraceCollect(path,kind)
    ast.visit(None,result,'Root')
    return result, text


def git(source, *args):
    return subprocess.check_output(['git','-C',str(source),*args],text=True).strip()


def selected(path):
    return (path.startswith('code/') and not path.startswith('code/guicode/')
            and production(path))


def declarations(c, text):
    """Name plus lexical scope; source comparison includes comments/formatting."""
    result = {}
    for node in c.nodes.values():
        if node['name'] == '<file>':
            continue
        parts = [node['name']]
        parent = node['parent']
        while parent and c.nodes[parent]['name'] != '<file>':
            parts.append(c.nodes[parent]['name'])
            parent = c.nodes[parent]['parent']
        key = '/'.join(reversed(parts))
        if key in result:
            raise ValueError(f'Duplicate lexical declaration: {c.path}:{key}')
        block = '\n'.join(text.splitlines()[node['line']-1:node['end_line']])
        result[key] = dict(node, block_sha256=hashlib.sha256(block.encode()).hexdigest())
    return result


def csv_rows(path):
    with path.open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_csv(output, name, rows, columns):
    write_csv(output/name, rows, columns)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    repo = Path(__file__).resolve().parents[2]
    parser.add_argument('--source',type=Path,default=repo/'upstream/acycle')
    parser.add_argument('--output',type=Path,default=repo/'audit/cores')
    args = parser.parse_args()
    source, output = args.source, args.output
    output.mkdir(parents=True,exist_ok=True)
    assert git(source,'rev-parse','HEAD') == SNAPSHOTS['current']
    assert not git(source,'status','--porcelain','--untracked-files=no')
    trees = {key:tree(source,sha) for key,sha in SNAPSHOTS.items()}
    content = blobs(source,{oid for files in trees.values() for path,oid in files.items()
                            if production(path)})
    cache = {}
    def parsed(path, oid):
        if (path,oid) not in cache:
            cache[path,oid] = parse_trace(path,content[oid])
        return cache[path,oid]

    changes, function_changes, comparison_summary = [], [], {}
    for before, after in COMPARISONS:
        label = before+'..'+after
        old, new = trees[before], trees[after]
        stats = {}
        for line in git(source,'diff','--no-renames','--numstat',
                        SNAPSHOTS[before],SNAPSHOTS[after]).splitlines():
            added, deleted, path = line.split('\t',2)
            if selected(path):
                stats[path] = (int(added),int(deleted))
        counts = Counter()
        groups = defaultdict(Counter)
        function_counts = Counter()
        for path in sorted(set(old)|set(new)):
            if not selected(path):
                continue
            status = ('added' if path not in old else 'removed' if path not in new
                      else 'unchanged' if old[path] == new[path] else 'modified')
            counts[status] += 1
            groups[path.split('/')[1]][status] += 1
            added, deleted = stats.get(path,(0,0))
            counts['lines_added'] += added
            counts['lines_deleted'] += deleted
            old_c, old_text = parsed(path,old[path]) if path in old else (None,'')
            new_c, new_text = parsed(path,new[path]) if path in new else (None,'')
            old_f = declarations(old_c,old_text) if old_c else {}
            new_f = declarations(new_c,new_text) if new_c else {}
            changes.append(dict(comparison=label,path=path,status=status,
                lines_added=added,lines_deleted=deleted,
                old_blob=old.get(path,''),new_blob=new.get(path,''),
                old_kind=old_c.kind if old_c else '',new_kind=new_c.kind if new_c else '',
                old_declarations=len(old_f),new_declarations=len(new_f)))
            for name in sorted(set(old_f)|set(new_f)):
                a,b = old_f.get(name),new_f.get(name)
                fstatus = ('added' if a is None else 'removed' if b is None else
                    'unchanged' if a['block_sha256']==b['block_sha256'] else 'modified')
                function_counts[fstatus] += 1
                if fstatus == 'unchanged':
                    continue
                function_changes.append(dict(comparison=label,path=path,function=name,
                    status=fstatus,old_line=a['line'] if a else '',new_line=b['line'] if b else '',
                    old_inputs=a['inputs'] if a else [],new_inputs=b['inputs'] if b else [],
                    old_outputs=a['outputs'] if a else [],new_outputs=b['outputs'] if b else []))
        assert sum(counts[k] for k in ('added','modified','removed')) == len(stats)
        comparison_summary[label] = dict(counts=counts,groups=dict(groups),
                                         declarations=function_counts)

    current = trees['current']
    collectors = {p:parsed(p,oid)[0] for p,oid in current.items() if production(p)}
    nodes = {key:value for c in collectors.values() for key,value in c.nodes.items()}
    exports = defaultdict(list)
    for path in collectors:
        exports[Path(path).stem].append(entry(path))
    old_edges = csv_rows(repo/'audit/reports/edges.csv')
    edges = {(e['source'],e['target'],int(e['line']),e['kind']) for e in old_edges}
    baseline_edges = set(edges)
    for c in collectors.values():
        for ref in c.refs:
            for target in resolve(ref,c,exports):
                edges.add((ref['source'],target,ref['line'],ref['kind']))
    assert all(s in nodes and t in nodes for s,t,_,_ in edges)
    additions = sorted(edges-baseline_edges)
    config = json.loads((repo/'audit/decisions.json').read_text())
    desktop = reachability([entry(p) for p in config['desktop_roots']],
        [dict(source=s,target=t) for s,t,_,_ in edges])
    cores = sorted(p for p in current if p.startswith('code/seriesanalysis/acycle') and p.endswith('.m'))
    core_set = set(cores)
    inventory, dependencies, callers, external = [],[],[],[]
    for path in cores:
        cross = sorted(e for e in edges if nodes[e[0]]['path']==path and nodes[e[1]]['path']!=path)
        incoming = sorted(e for e in edges if nodes[e[1]]['path']==path and nodes[e[0]]['path']!=path)
        deps = sorted({nodes[e[1]]['path'] for e in cross})
        for s,t,line,kind in cross:
            target = nodes[t]['path']
            dependencies.append(dict(core=Path(path).stem,source_function=nodes[s]['name'],
                line=line,target=target,kind=kind,target_is_core=target in core_set,
                existed_in_guide=target in trees['guide'],
                same_as_guide=current[target]==trees['guide'].get(target),
                modified_in_core_commit=trees['before_cores'].get(target)!=trees['core_commit'].get(target)))
        for s,t,line,kind in incoming:
            callers.append(dict(core=Path(path).stem,caller_path=nodes[s]['path'],
                caller_function=nodes[s]['name'],line=line,kind=kind,
                source_desktop_possible=s in desktop,
                direct_from_guicode=nodes[s]['path'].startswith('code/guicode/')))
        c = collectors[path]
        for ref in c.refs:
            if (ref['kind'] in ('call_or_index','command','function_handle')
                    and ref['name'] not in visible_variables(c,ref['source'])
                    and not resolve(ref,c,exports)):
                external.append(dict(core=Path(path).stem,function=nodes[ref['source']]['name'],
                    line=ref['line'],name=ref['name'],kind=ref['kind']))
        birth = git(source,'log','--diff-filter=A','--format=%H\t%cs\t%s','--',path).splitlines()[0].split('\t',2)
        inventory.append(dict(core=Path(path).stem,path=path,birth_commit=birth[0],
            birth_date=birth[1],birth_subject=birth[2],
            initial_batch=birth[0]==SNAPSHOTS['core_commit'],
            lines=len(content[current[path]].splitlines()),
            declarations=len(c.nodes)-1,local_declarations=max(0,len(c.nodes)-2),
            repository_dependencies=deps,legacy_dependencies=[d for d in deps if d not in core_set],
            direct_gui_callers=sorted({nodes[s]['path'] for s,_,_,_ in incoming if nodes[s]['path'].startswith('code/guicode/')}),
            desktop_possible=entry(path) in desktop,
            changed_after_introduction=git(source,'rev-parse',birth[0]+':'+path)!=current[path]))

    legacy = sorted({r['target'] for r in dependencies if not r['target_is_core']})
    related = sorted(set(cores)|set(legacy)|{
        r['path'] for r in changes if r['comparison']=='before_cores..core_commit' and r['status']=='modified'
    }|{'code/seriesanalysis/find_extrema.m','code/seriesanalysis/eemd.m',
       'code/seriesanalysis/interpolate.m','code/seriesanalysis/erhoAR1.m',
       'code/seriesanalysis/spectralmoments.m','code/seriesanalysis/rmse4leadlag.m'})
    history = []
    for path in related:
        for line in git(source,'log','--ancestry-path','--format=%H\t%cs\t%s',
                        SNAPSHOTS['guide']+'..'+SNAPSHOTS['current'],'--',path).splitlines():
            commit,date,subject=line.split('\t',2)
            history.append(dict(path=path,commit=commit,date=date,subject=subject))
    summary = dict(snapshots=SNAPSHOTS,scope='Production code/**/*.m excluding code/guicode and test/tests directories',
        comparisons=comparison_summary,core_files=len(cores),
        initial_core_files=sum(r['initial_batch'] for r in inventory),
        core_lines=sum(r['lines'] for r in inventory),
        core_declarations=sum(r['declarations'] for r in inventory),
        direct_legacy_dependencies=legacy,
        core_files_without_repository_dependencies=sum(not r['repository_dependencies'] for r in inventory),
        core_files_without_legacy_dependencies=sum(not r['legacy_dependencies'] for r in inventory),
        direct_gui_core_files=sum(bool(r['direct_gui_callers']) for r in inventory),
        desktop_possible_core_files=sum(r['desktop_possible'] for r in inventory),
        supplemented_edges=len(additions),
        limitations=[
            'Syntactic possible calls; no runtime path, MATLAB execution, toolbox or numerical parity validation.',
            'Old function means a separate repository MATLAB file, excluding MATLAB/toolbox functions and local helpers.',
            'Initial batch means precisely commit 885c742, not every change during the 3.X migration.',
            'Outside guicode includes UI helpers and package GUIs; it is not a pure numerical-code category.',
            'Line changes include comments and validation; declarations include local/nested helpers and methods.',
            'Declaration matching uses lexical names; renames count as removal/addition and parent blocks overlap nested functions.',
            'Source history cannot establish authorship of AI prompts or numerical equivalence.',
            'Original graph retained; additional calls fix binary-expression LHS omissions without rewriting archived reports.',
            'External references are unresolved by repository lookup, not an exhaustive certified MATLAB toolbox manifest.',
        ])
    save_csv(output,'non_guicode_changes.csv',changes,list(changes[0]))
    save_csv(output,'function_changes.csv',function_changes,list(function_changes[0]))
    save_csv(output,'core_inventory.csv',inventory,list(inventory[0]))
    save_csv(output,'direct_dependencies.csv',dependencies,list(dependencies[0]))
    save_csv(output,'core_callers.csv',callers,list(callers[0]))
    save_csv(output,'external_references.csv',external,list(external[0]))
    save_csv(output,'history.csv',history,list(history[0]))
    save_csv(output,'graph_supplement.csv',[dict(source=s,target=t,line=l,kind=k) for s,t,l,k in additions],
             ['source','target','line','kind'])
    write_json(output/'summary.json',summary)
    names=['non_guicode_changes.csv','function_changes.csv','core_inventory.csv','direct_dependencies.csv',
           'core_callers.csv','external_references.csv','history.csv','graph_supplement.csv','summary.json']
    write_json(output/'validation.json',dict(passed=True,parsed_versions=len(cache),parse_failures=[],
        upstream_commit=SNAPSHOTS['current'],tracked_source_unchanged=True,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        dependency_script_sha256={name:hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()
            for name in ['audit_acycle.py','compare_guide_coupling.py']},
        report_sha256={name:hashlib.sha256((output/name).read_bytes()).hexdigest() for name in names}))
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
