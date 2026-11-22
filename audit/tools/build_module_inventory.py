"""Rebuild or check the module, source, call-site and compatibility inventories."""
import argparse
import csv
import io
import re
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

from module_source_facts import ROOT, snapshots

sys.path.insert(0, str(ROOT))
from migration.export_method import executable


OUT = ROOT / 'audit/modules'
ROLE_NAMES = ('helper', 'analyzer', 'plotter')
SCIENCE = {'analysis', 'data', 'view', 'workflow'}
DIRECT = {'call_or_index', 'command', 'bare_name', 'literal_dispatch'}
SECTION = re.compile(r'^%% Copied from (\S+) (.+):L(\d+)-L(\d+)$', re.M)
AC_CALLBACKS = {'AC_runEmpiricalModeMenu': 'EMD'}
MIXED_GUI = {'code/guicode/eCOCOGUI.m': ('Coco', 'EvolutionaryCoco'),
             'code/guicode/waveletGUI.m': ('Wavelet', 'WaveletCoherence')}


def read(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def joined(values):
    return ' '.join(sorted(set(values)))


def interface_name(module, role):
    return 'ac' + module + '_' + role


class Ownership:
    def __init__(self):
        self.families = {r['module']: r for r in read(OUT / 'families.tsv')}
        self.names, self.folders = {}, {}
        self.tags = defaultdict(list)
        self.menus = {r['tag']: r for r in read(ROOT / 'migration/master/menus.tsv')}
        for module, row in self.families.items():
            for name in row['owned_names'].split():
                mapping = self.folders if name.startswith('@') else self.names
                key = name.lstrip('@')
                assert key not in mapping, (module, key, mapping.get(key))
                mapping[key] = module
            for tag in row['menu_tags'].split():
                self.tags[tag].append(module)
        assert self.tags.keys() == self.menus.keys(), 'menu ownership is incomplete'

    def file(self, path):
        name = Path(path).stem
        if name in self.names:
            return self.names[name]
        for folder, module in self.folders.items():
            if path.startswith(folder + '/'):
                return module
        raise ValueError('Assign a module to ' + path)

    def scope(self, version, path, ident, facts):
        """A shared GUI or menu does not cast one vote for each topic it contains."""
        module = self.file(path)
        if path.endswith('/spectrumBKUP.m'):
            return module, 'backup'
        if path in MIXED_GUI:
            return '/'.join(MIXED_GUI[path]), 'mixed-gui'
        if path != 'code/guicode/AC.m':
            return module, 'owned'
        while ident:
            name, parent, *_ = facts['nodes'][ident]
            if name in AC_CALLBACKS:
                return AC_CALLBACKS[name], 'callback'
            if name.endswith('_Callback'):
                tag = name[:-9]
                if tag in self.tags:
                    groups = self.tags[tag]
                    flag = self.menus[tag][version + '_initial']
                    if flag in {'hidden', 'absent'}:
                        return '/'.join(groups), flag + '-menu'
                    return '/'.join(groups), 'callback' if len(groups) == 1 else 'mixed-menu'
            ident = parent
        return module, 'desktop'


def collect_calls(all_facts, owners):
    calls = defaultdict(list)
    for version, files in all_facts.items():
        for path, facts in files.items():
            for scope, ln, kind, target in facts['edges']:
                module, attribution = owners.scope(version, path, scope, facts)
                # Scripts inherit variables. The wavelet scripts index their period grid;
                # the SWA routine period.m is an unrelated Lomb periodogram function.
                if path.startswith('code/package/wavelet/') and target == 'code/package/swa/period.m':
                    attribution = 'workspace-variable'
                elif kind == 'bare_name' and files[target]['kind'] != 'script':
                    attribution = 'unconfirmed-name'
                calls[version, target].append((module, attribution, path, scope, ln, kind))
    return calls


def direct_modules(rows, owners, science_only=True):
    return {m for m, attr, path, scope, ln, kind in rows
            if attr in {'owned', 'callback'} and kind in DIRECT
            and (not science_only or owners.families[m]['kind'] in SCIENCE)}


GUI_KINDS = {'gui_input','gui_notice','gui_progress','gui_state','graphics'}
GATED = {'ftestmtmML','redconfML','minirhos0'}  # Plot guards verified in both pinned source files.
DESKTOP_ADAPTERS = {'ac_refresh_main_list','ac_update_listbox_acmain','ac_working_directory',
                    'ac_user_settings','findjobj','myginput','dynotCloseProgressWindow'}
GUI_SHELLS = set('AC ac ACUpdate About copyright ac_gui_dispatch basicseries agescale circularspecGUI coherenceGUI '
                 'column_manipulateGUI CorrelationGUI data_type DataExtractML DataExtractTab datatransformationsGUI '
                 'DynamicFilter DYNOS eCOCOGUI eTimeOptGUI evofftGUI ft Insolation InterplationSeries interpolationGUI '
                 'languageGUI leadlagGUI linegenerator LODGUI PlotAdv plotdigitizer PlotPro2DLineGUI prewhiten '
                 'prewhitenGUI RecPlotGUI RobotGUI settingsGUI SmoothBootGUI SpectralMomentsGUI spectrum SWAgui '
                 'timeOptGUI waveletGUI AcycleDataTableGUI ANOVAUI BivCorrUI BivCovUI BivLinearRegUI UniChi2GOFUI '
                 'UniNormalityUI UniStatisticSum Unittest UniTwoSampleTestsUI undatableGUI bispectralGUI'.split())
PLOTS = set('bispectralPlot plotAdaptiveCocoPublication plotcvcoco ecocoplot ecocoplots ac_protect_coco_result_figures '
            'cocoShadeOutsideAllPeriodRange pAxes18 phaseplot plot2raster imscrollpanel_ac imscrollpanel_acDig'.split())


def effects_at(records):
    by_name = defaultdict(list)
    for _, line, group, name in records:
        by_name[group, name].append(line)
    return ' | '.join(f'{group}/{name}@{min(lines)}' for (group,name),lines in sorted(by_name.items()))


def source_action(path, facts, gui_dependencies):
    name = Path(path).stem
    effects = {group for _, _, group, _ in facts['effects']}
    if path == 'doc/ac_acknowledgment.m':
        return 'retain-document'
    if path.endswith('/spectrumBKUP.m'):
        return 'preserve-archival'
    if path.startswith('upstream/compatibility/'):
        return 'keep-opt-in-compatibility'
    if facts['kind'] == 'script':
        return 'functionize-script'
    if name in DESKTOP_ADAPTERS:
        return 'retain-desktop-adapter'
    if name == 'redmark':
        return 'review-clock-seeded-rng'
    if name == 'smoothbestSpanRand':
        return 'use-explicit-progress-switch'
    if name in GUI_SHELLS or facts['kind'] == 'class_file':
        return 'separate-gui-callbacks'
    if name in PLOTS:
        return 'retain-plot-implementation'
    if name in GATED and not (effects & {'gui_input','gui_notice','gui_progress','gui_state','workspace'}):
        return 'use-explicit-plot-switch'
    if effects & {'gui_input','gui_notice','gui_progress','gui_state'}:
        return 'detach-gui'
    if 'graphics' in effects:
        return 'check-plot-switch-or-split'
    if effects & {'workspace','cwd'}:
        return 'make-state-explicit'
    if gui_dependencies:
        return 'retain-check-callee-side-effects'
    if 'file_io' in effects:
        return 'retain-check-io'
    return 'retain-original-function'


def role_tables(owners, all_facts):
    result, counts, implementation_roles = [], defaultdict(set), defaultdict(set)
    copied_ranges = defaultdict(list)
    recovered = {(r['origin'], r['member']): r['local_path'] for r in read(ROOT/'migration/recovered.tsv')}
    workflow = {package:r['module'] for r in read(OUT/'workflow_entries.tsv')
                for package in r['menu_or_script_entries'].split()}
    seen_packages = set()
    existing_names = set()
    for files in all_facts.values():
        for path, f in files.items():
            existing_names.add(Path(path).stem.casefold())
            existing_names.update(n[0].casefold() for n in f['nodes'].values())
    existing_names.update(p.stem.casefold() for p in (ROOT/'matlab').rglob('*.m'))
    for p in (ROOT/'matlab').rglob('*.m'):
        for line in p.read_text(encoding='utf-8').splitlines():
            m = re.match(r'^\s*function\s+(?:[^=]+=\s*)?(\w+)\s*\(',line)
            if m:
                existing_names.add(m[1].casefold())
    assert 'acprivatefunctions' not in existing_names
    proposed = {}
    for module in owners.families:
        for role in ROLE_NAMES:
            key = interface_name(module,role).casefold()
            assert key not in existing_names and key not in proposed and len(key)<=63, key
            proposed[key] = module
    for version, namespace, location in [('guide','+acmethods','migration/methods.tsv'),
                                         ('master','+acmaster','migration/master/methods.tsv')]:
        files = all_facts[version]
        mapping = {Path(p).stem:owners.file(p) for p in files}
        base = ROOT/'matlab'/namespace
        rows = read(ROOT/location)
        listed = {(v['package'],v['role']) for v in rows}
        assert listed == {(f.parent.name[1:],f.stem) for f in base.glob('+*/*.m')}
        for row in rows:
            package, role = row['package'], row['role']
            module = owners.names.get(package) or mapping[package]
            seen_packages.add(package)
            path = base/('+'+package)/(role+'.m')
            text = path.read_text(encoding='utf-8')
            op = re.search(r"(?:aclog\.invoke|accompat\.masterInvoke)\('([^']+)'",text)[1]
            body = executable(text)
            refs = defaultdict(list)
            for repo, src, start, end in SECTION.findall(text):
                key = src if repo == 'mingsongli/acycle@'+files['ac.m']['origin'] else repo+' '+src
                refs[key].append(start if end==start else start+'-'+end)
                source = recovered.get((repo,src),src)
                assert source in files, (repo,src)
                copied_ranges[version,repo,source,int(start),int(end)].append((module,op))
            sections = ' | '.join(k+':'+','.join(v) for k,v in refs.items())
            if package in workflow:
                assert workflow[package] == module, (package,module)
                counts[version,module].add(role)
            for name in re.findall(r'\b(ac(?:compat|log)\.\w+)\(',body):
                implementation_roles[name].add((version,module,package,role))
            contract = row['parameters']
            fields = joined(re.findall(r'\bp\.([A-Za-z]\w*(?:\.[A-Za-z]\w*)*)',body))
            route = 'family-entry' if package in workflow else 'expert-compatibility'
            target = interface_name(module,role) if package in workflow else 'original implementation via old op'
            if route == 'family-entry' and role not in owners.families[module]['planned_roles'].split():
                target = 'preserve versioned role'
            if module == 'MethodValidation':
                route, target = 'verification', 'retain validation/experiment via old op'
            if package in {'BispectralExport','EvolutionaryWorkbook'}:
                route, target = 'product-io', 'family product + Core I/O'
            result.append([version,module,op,package,role,route,target,contract,fields,
                           str(path.relative_to(ROOT)),row['source_files'],sections])
    assert set(workflow) <= seen_packages
    return result,counts,implementation_roles,copied_ranges


def asset_owner(path, owners):
    p = Path(path)
    if p.suffix == '.fig':
        return owners.file(str(p.with_suffix('.m')))
    if 'undatable' in p.parts:
        return 'Undatable'
    if 'secular_periods' in p.parts or p.name == 'Berger1989Periods.txt':
        return 'OrbitalPeriods'
    if 'LR04' in path.upper() or 'CENOGRID' in path.upper():
        return 'ReferenceSeries'
    if p.name == 'Undatable User Manual.pdf':
        return 'Undatable'
    if p.name in {'SecularFreqLa04Tab3.txt','Berger1989Periods.txt'}:
        return 'OrbitalPeriods'
    if 'Examples' in p.parts:
        return 'Examples'
    if p.parts[0]=='data':
        return 'OrbitSolution'
    if p.parts[0]=='doc' or p.name in {'langdict.xlsx','ac_lang.txt','ac_version.txt','ac_date.txt','ac_datenow.txt','ac_opendate.txt'}:
        return 'SettingsHelp'
    if p.name in {'PlotAdvSettingSeed.xlsx','axesTheme.mat'}:
        return 'SeriesPlot'
    if 'bin' in p.parts:
        return 'Workspace'
    return 'Desktop'


def gui_dependency_paths(version, files, calls):
    graph = defaultdict(set)
    marked = {p for p,f in files.items() if any(e[2] in GUI_KINDS for e in f['effects'])}
    for target in files:
        for _,attr,source,_,_,kind in calls[version,target]:
            if kind in DIRECT and attr not in {'unconfirmed-name','workspace-variable','backup'}:
                graph[source].add(target)
    paths = {}
    for source in files:
        seen = {source}
        pending = deque([(p,) for p in sorted(graph[source])])
        while pending:
            path = pending.popleft()
            tail = path[-1]
            if tail in seen:
                continue
            seen.add(tail)
            if tail in marked:
                paths[source] = ' > '.join(path)
                break
            pending.extend(path+(other,) for other in sorted(graph[tail]) if other not in seen)
    return paths


def produce(owners, all_facts):
    calls = collect_calls(all_facts,owners)
    decisions = {r['function']:r for r in read(OUT/'core_review.tsv')}
    legacy,role_counts,infra_use,copied_ranges = role_tables(owners, all_facts)
    files_out, decls, cross, uses, deferred, assets = [], [], [], [], [], []
    per_version = defaultdict(Counter)
    for revision, module, *_ in legacy:
        per_version[revision,module]['legacy_roles'] += 1
    for (revision, _, _, _, _), callers in copied_ranges.items():
        for module, _ in callers:
            per_version[revision,module]['blocks'] += 1
    for version, files in all_facts.items():
        gui_paths = gui_dependency_paths(version, files, calls)
        for path, f in sorted(files.items()):
            module = owners.file(path)
            incoming = calls[version,path]
            mods = direct_modules(incoming,owners)
            direct_all = direct_modules(incoming,owners,False)
            name = Path(path).stem
            gui_path = gui_paths.get(path,'')
            action = source_action(path,f,gui_path)
            files_out.append([version,module,path,f['origin'],f['blob'],f['kind'],action,
                              len(f['nodes'])-1,effects_at(f['effects']),gui_path,len(f['dynamic'])])
            per_version[version,module]['sources']+=1
            per_scope = defaultdict(list)
            for e in f['effects']:
                per_scope[e[0]].append(e)
            for ident,n in f['nodes'].items():
                if n[0]=='<file>':
                    continue
                mod, tag = owners.scope(version,path,ident,f)
                if '/' in mod:
                    for family in mod.split('/'):
                        per_version[version,family]['shared_declarations'] += 1
                else:
                    per_version[version,mod]['declarations'] += 1
                decls.append([version,mod,path,n[0],n[3],n[4],n[2],tag,
                              (n[1] or '').split('::')[-1],effects_at(per_scope[ident])])
            for group, reason in [('dynamic','runtime dispatch / workspace'),
                                  ('missing','known in another source tree; missing on native path')]:
                for scope,line,name_ref in f[group]:
                    scope_module, attribution = owners.scope(version,path,scope,f)
                    deferred.append([version,scope_module,path,scope.split('::')[1],line,name_ref,reason,attribution])
            for scope,line,name_ref,targets in f['ambiguous']:
                scope_module, attribution = owners.scope(version,path,scope,f)
                deferred.append([version,scope_module,path,scope.split('::')[1],line,name_ref,'ambiguous: '+targets,attribution])
            for mod,attr,src,scope,ln,kind in incoming:
                if attr in {'workspace-variable','unconfirmed-name'}:
                    _, attribution = owners.scope(version,src,scope,files[src])
                    deferred.append([version,mod,src,scope.split('::')[1],ln,name,attr,attribution])
            if len(direct_all)<2 and name not in decisions:
                continue
            choice = decisions.get(name,{})
            default = 'domain-shared' if len(mods)>=2 else 'shared-support'
            decision = choice.get('recommendation',default)
            if decision.startswith('core-') and len(mods)<2:
                raise ValueError(f'Insufficient independent sources for {version} {name}')
            uses.append([version,name,path,module,decision,len(mods),joined(mods),joined(direct_all-mods),
                         choice.get('reason_zh','保留所属模块；跨模块直接调用原函数。')])
            by_site = defaultdict(set)
            for mod,attr,src,scope,ln,kind in incoming:
                by_site[mod,attr,src,scope.split('::')[1],kind].add(ln)
            for (mod,attr,src,scope,kind),lines in sorted(by_site.items()):
                cross.append([version,name,path,mod,attr,src,scope,kind,','.join(map(str,sorted(lines)))])
    for row in read(ROOT/'migration/master/sources.tsv'):
        path = row['path']
        if path.endswith('.m'):
            continue
        assets.append([asset_owner(path,owners),path,row['status'],row['guide_blob'],row['master_blob']])
    actions = {(r[0],r[2]):r[6] for r in files_out}
    extraction = []
    for (version,origin,path,first,last), callers in sorted(copied_ranges.items()):
        f = all_facts[version][path]
        action = actions[version,path]
        enclosing = [n for n in f['nodes'].values() if n[0]!='<file>' and n[3]<=first and n[4]>=last]
        scope = min(enclosing,key=lambda n:n[4]-n[3])[0] if enclosing else '<file>'
        if f['kind'] == 'script':
            disposition = 'functionize-or-fold-script'
        elif action == 'separate-gui-callbacks':
            disposition = 'extract-callback-if-needed'
        elif action in {'check-plot-switch-or-split','detach-gui','make-state-explicit','retain-check-callee-side-effects'}:
            disposition = 'check-independent-call-and-detach-effects'
        else:
            disposition = 'check-existing-function-contract-first'
        extraction.append([version,joined(m for m,_ in callers),origin,path,first,last,scope,action,
                           disposition,len(callers),joined(op for _,op in callers)])
    index = []
    for key,f in owners.families.items():
        plan = f['planned_roles'].split()
        index.append([f['area'],key,f['name_zh'],f['kind'],f['menu_tags'],f['params_choices_zh'],f['result_zh'],
                      ' '.join(interface_name(key,s)+'.m' for s in plan),
                      joined(role_counts['guide',key]),joined(role_counts['master',key]),
                      *[per_version[rev,key][field] for field in ('sources','legacy_roles','blocks','declarations','shared_declarations')
                        for rev in ('guide','master')]])
    result = {
        'modules': ('area module name_zh kind menu_tags params_summary_zh products_zh proposed_filenames guide_workflow_roles master_workflow_roles guide_owned_files master_owned_files guide_legacy_roles master_legacy_roles guide_copied_blocks master_copied_blocks guide_attributed_declarations master_attributed_declarations guide_shared_declarations master_shared_declarations',index),
        'roles': ('revision module op legacy_package role route_kind proposed_route legacy_params directly_read_fields wrapper_path attributed_sources copied_source_ranges',legacy),
        'sources': ('revision module source origin content_id kind migration_action declarations direct_effects_first_lines example_path_to_gui_dependency dynamic_sites',files_out),
        'declarations': ('revision module source name line end_line kind attribution parent direct_effects_first_lines',decls),
        'shared_functions': ('revision function source owner recommendation scientific_modules_n scientific_modules other_direct_modules reason_zh',uses),
        'shared_call_sites': ('revision function target caller_module attribution caller_file caller_scope evidence_kind lines',cross),
        'binding_review': ('revision module caller_file scope line symbol reason attribution',deferred),
        'copied_blocks': ('revision consuming_modules origin source first_line last_line enclosing_scope source_action next_step occurrences old_ops',extraction),
        'assets': ('module path status guide_blob master_blob',assets),
    }
    return result,infra_use


def check_table(name, fields, rows, write):
    buf=io.StringIO()
    writer=csv.writer(buf,delimiter='\t',lineterminator='\n')
    writer.writerow(fields.split())
    writer.writerows(rows)
    # An explicit empty last field survives editors that trim trailing tabs.
    contents = buf.getvalue().replace('\t\n', '\t""\n')
    path=OUT/(name+'.tsv')
    if write:
        path.write_text(contents,encoding='utf-8')
    elif not path.is_file() or path.read_text(encoding='utf-8')!=contents:
        raise SystemExit('Outdated inventory: '+str(path))
    print(f'{name}: {len(rows)}')


def validate_and_emit(all_facts, write):
    owners = Ownership()
    result, infra_use = produce(owners, all_facts)
    original = read(ROOT/'migration/master/sources.tsv')
    for revision, col in [('guide','guide_blob'),('master','master_blob')]:
        expected = {r['path'] for r in original if r[col] and r['path'].endswith('.m')}
        if revision == 'guide':
            expected.update(r['local_path'] for r in read(ROOT/'migration/recovered.tsv'))
        else:
            expected.add('upstream/compatibility/coco/freq2target.m')
        assert set(all_facts[revision]) == expected, revision
    role_rows = result['roles'][1]
    assert len({r[2] for r in role_rows}) == len(role_rows)
    decisions = {r['function'] for r in read(OUT/'core_review.tsv')}
    assert decisions <= {r[1] for r in result['shared_functions'][1]}
    selections = read(OUT/'selection_values.tsv')
    assert Counter((r['module'],r['choice_kind']) for r in selections) == {
        ('Interpolation','one'):9, ('Transform','one'):16, ('PowerSpectrum','one'):3, ('PowerSpectrum','flag'):6}
    for namespace in ('+acmethods','+acmaster'):
        base = ROOT/'matlab'/namespace
        for r in selections:
            text = (base/('+'+r['legacy_entry'])/'analyzer.m').read_text()
            field = r['guide_params' if namespace == '+acmethods' else 'master_params']
            if r['choice_kind'] == 'flag':
                assert re.search(r'\b' + re.escape(field.split('.')[1]) + r'\b', text), field
            elif r['module'] in {'Interpolation','Transform'}:
                field, value = field.split('=')
                assert re.search(r'\b'+field+r'\s*==\s*'+value+r'\b',text), (field,value)
            else:
                assert field.split('=')[1] in text
    platform = read(OUT/'platform.tsv')
    expected = {'setup_migration.m','matlab/logger.m'}
    for package in ('+aclog','+accompat'):
        expected.update(str(p.relative_to(ROOT)) for p in (ROOT/'matlab'/package).glob('*.m'))
    assert {r['source'] for r in platform if r['disposition']!='proposed'} == expected
    usage = []
    for r in platform:
        path = Path(r['source'])
        key = path.parent.name.lstrip('+')+'.'+path.stem
        edges = infra_use.get(key,set())
        counts = [sum(v==revision for v,_,_,_ in edges) for revision in ('guide','master')]
        usage.append([r['source'],r['part'],r['disposition'],*counts,joined(k[1] for k in edges),r['responsibility_zh']])
    result['platform_usage'] = ('source part disposition direct_guide_roles direct_master_roles direct_module_ids responsibility_zh',usage)
    for name,(header,rows) in result.items():
        check_table(name,header,rows,write)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='replace the generated tables')
    args = parser.parse_args()
    validate_and_emit(snapshots(),args.write)
