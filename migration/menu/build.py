"""Build the public MATLAB menu interfaces from the two pinned migration inventories."""
import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'code/interface'
AUDIT = ROOT / 'audit/modules'
ROLES = ('helper', 'analyzer', 'plotter')

# Expert functions with multiple plausible menu owners, and new master operations.
EXTRA = {
    'menu_refreshlist': 'ac_sort_dir_entries strrep2',
    'menu_interp': 'RegularInterpolation interpolate_rand',
    'menu_datatransf': 'Standardize Log10',
    'menu_log10': 'Log10', 'menu_norm': 'Standardize',
    'menu_smooth': 'movemean', 'menu_movmedian': 'moveMedian',
    'menu_movmeanfbw': 'movmeanfbw',
    'menu_bootstrap': 'smoothbestSpan smoothci smoothciML',
    'menu_filter': 'gaussfilter gaussmf tanerhilbertML',
    'menu_dynfilter': 'dynamic_filter dynamic_filter_lang',
    'menu_emd': 'emdNL find_extrema', 'menu_eemd': 'eemd find_extrema',
    'menu_dynos': 'dynotIterationWorker dynotPercentilePlan pdan',
    'menu_rho': 'calculateRhoM erhoAR1 rhoAR1 rhoAR1ML Lag1V2 Lag1V2MonteCarlo',
    'menu_uni2SamTest': 'AnDarksamtest', 'menu_normaltest': 'swtest',
    'menu_bispectral': 'bispectralSelfTest bispectralLocalDataValidation bispectralValidateExamples',
    'menu_ecoco': ('runCocoEightMethodExperiment runCocoPublicationValidation runEcocoTwoMethodExperiment '
                   'runInterleavedCvCocoComparison runSyn3FourMethodPublicationStudy validateCocoPublicationValidation'),
}
PREFERRED = {
    'menu_ecoco':'ecoco', 'menu_leadlag':'LeadLag', 'menu_specmoments':'SpectralMoments',
    'menu_improfile':'ImageTransect', 'menu_insol':'insoML', 'menu_whiten':'AR1Prewhitening',
    'menu_prewhiten':'Detrending','menu_waveletGUI':'WaveletSpectrum','menu_bispectral':'Bispectral',
    'menu_power':'PowerSpectrum','menu_filter':'Bandpass','menu_interp':'interpolate',
    'menu_emd':'EMD','menu_eemd':'EnsembleEMD','menu_rho':'Lag1','menu_dynot_v2':'DYNOT_legacy',
    'menu_log10':'Log10','menu_norm':'Standardize','push_robot':'Robot',
}
# Required discriminator fields. The active branch is validated in acMenuValidate.
CONDITIONAL = {
    'AstronomicalSolution':'solution parameter t1 t2',
    'DataTransform':'data checkid j','Detrending':'data method',
    'PassFilter':'data passtype filter_s f11','SeriesGenerator':'x kind',
    'Lyapunov':'tau window step_size num_surrogates',
    'PowerSpectrum':'data method nw nfft fmin fmax models',
    'PowerSpectrum_legacy':'data method noise nw nzeropad fmax',
    'Bandpass_legacy':'data filter flow fhigh','CircularSpectrum_legacy':'data p1 p2 pn linlog clmodel mcn',
    'SpectralPowerLaw_legacy':'datax fd1 po method','SpectralBendingPowerLaw_legacy':'datax fd1 po method',
    'TimeOpt_legacy':'dat sedmin sedmax numsed nsim linLog fit fl fh roll targetE targetP detrend cormethod',
}
# Plot-only presentation fields used by the old adapters. All other plot-only values
# (sample coordinates, fitted series, etc.) travel in dat or the analyzer result.
STYLE = set(('unit unit_type unit_t_r filename dat_name ext name_insol data_name xlabel ylabel title xlabel_text '
             'ylabel_text labelx labely distance_label grayscale_label fmin fmax reverseY dimension '
             'usePeriod logFrequency logPower swaSelection linlogY logfreq Yticks figure_count '
             'log_y log_x period_axis curves flipx fliptime flipseries standardized offset '
             'settings PlotAdvSetting figureName directory view x_1 x_2 y_1 y_2 y_3 x1 x2 y1 y2 '
             'refxmin refxmax serxmin serxmax legendi titlei epsilon_plot flipxy genplot plotsar printme vcloud '
             'writedir baseName outputDirectory outputFile showseries plotseries qplot plotn '
             'lang_id lang_var color_type wtcthreshold frequencyMode').split())

def read(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))

def plain_fields(row):
    if not row:
        return set()
    return {s.split('.')[0] for s in row['directly_read_fields'].split()}

def scientific_fields(selector, package, row):
    if not row:
        return '', ''
    desc = row['legacy_params']
    base = desc.split(';')[0].replace('(none)','')
    base = re.sub(r'\([^)]*\)', '', base).split()
    required = CONDITIONAL.get(selector,CONDITIONAL.get(package,' '.join(base))).split()
    all_fields = plain_fields(row) | set(required)
    if package=='Lyapunov':
        all_fields.update('data data_even interpolate_rate padtype'.split())
    if 'optional legacyTarget' in desc:
        all_fields.add('legacyTarget')
    # Preserve nested required option names for name/value kernels, including ProgressFcn=[].
    for fields in re.findall(r'options\(([\w,]+)\)',desc):
        required.extend('options.'+name for name in fields.split(','))
    assert all(re.fullmatch(r'\w+(?:\.\w+)?',n) for n in required),(selector,required)
    return ' '.join(sorted(all_fields)),' '.join(dict.fromkeys(required))

def stem(tag):
    tail=tag.removeprefix('menu_') if tag!='push_robot' else 'Robot'
    return 'acMenu'+''.join(w[:1].upper()+w[1:] for w in tail.split('_'))

def build():
    rows=read(AUDIT/'roles.tsv')
    families={r['module']:r['menu_tags'].split() for r in read(AUDIT/'families.tsv')}
    menu_rows=read(ROOT/'migration/master/menus.tsv')
    audit={r['tag']:r for r in read(AUDIT/'menu_to_modules.tsv')}
    groups={r['package']:r['module'] for r in read(AUDIT/'package_to_modules.tsv')}
    by_name=defaultdict(dict)
    for row in rows:
        key=row['legacy_package']+('_legacy' if row['revision']=='guide' else '')
        assert row['role'] not in by_name[key]
        by_name[key][row['role']]=row
    engines={}
    for key, roles in sorted(by_name.items()):
        row=next(iter(roles.values()))
        package=row['legacy_package']
        fields,required=scientific_fields(key,package,roles.get('analyzer'))
        plot=plain_fields(roles.get('plotter'))
        styles={k for k in plot if k in STYLE or k.startswith('plot_')}
        engines[key]=dict(operation=key,package=package,revision=row['revision'],
                         roles=' '.join(r for r in ROLES if r in roles),fields=fields,
                         required=required,plotFields=' '.join(sorted(plot)),styles=' '.join(sorted(styles)))
    for key,pkg,rev in [('Desktop_legacy','Desktop','guide'),('Robot','Robot','master'),('Robot_legacy','Robot','guide')]:
        engines[key]=dict(operation=key,package=pkg,revision=rev,roles='plotter',fields='',required='',plotFields='',styles='')
    tags=defaultdict(set)
    for row in menu_rows:
        tag=row['tag']
        for pkg in row['guide_packages'].split():
            tags[pkg].add(tag)
    for tag,packages in EXTRA.items():
        for pkg in packages.split():
            assert pkg in groups,pkg
            tags[pkg].add(tag)
    for pkg,mod in groups.items():
        if pkg=='Desktop':
            continue
        if len(families[mod])==1:
            tags[pkg].update(families[mod])
        assert tags[pkg], (pkg,mod)
    # The button lives outside the menu tree. Its two historical callbacks remain usable.
    menu_rows.append(dict(tag='push_robot',guide_menu='Toolbar > Mini-Robot',master_menu='Toolbar > Mini-Robot',
                          guide_initial='visible',master_initial='visible',native_route='button',
                          guide_packages='',master_source='',master_callback='push_robot_clbk'))
    files={}
    menus=[]
    seen=set()
    for row in menu_rows:
        tag=row['tag']
        guide,master=row['guide_menu'],row['master_menu']
        location=master or guide
        headings=location.split(' > ')[:-1]
        folder='/'.join(re.sub(r'[^A-Za-z0-9]','',p) for p in headings)
        heading=row['native_route']=='heading' or audit.get(tag,{}).get('guide_coverage')=='heading' or tag=='menu_utilities'
        choices=set()
        if not heading:
            for key,e in engines.items():
                if tag in tags.get(e['package'],set()):
                    # A removed GUI item belongs to the GUIDE tree. Current implementations
                    # remain on the corresponding current menu, if one exists.
                    if master or e['revision']=='guide':
                        choices.add(key)
            if tag=='push_robot':
                choices.update(('Robot','Robot_legacy'))
            else:
                if guide: choices.add('Desktop_legacy')
                if master and row['native_route'] in ('acmaster.Desktop.plotter','hidden declaration'): choices.add('Desktop')
        priority=[PREFERRED.get(tag,'')]+row['guide_packages'].split()
        order=[p for name in priority for p in (name,name+'_legacy')]+sorted(choices)
        science=[s for s in order if s in choices and s not in ('Desktop','Desktop_legacy')]
        default=next(iter(science), 'Desktop' if 'Desktop' in choices else 'Desktop_legacy')
        if tag=='menu_refreshlist': default='Desktop'
        prefix=stem(tag) if choices else ''
        available=['helper'] if choices else []
        available += [r for r in ('analyzer','plotter') if any(r in engines[k]['roles'].split() for k in choices)]
        for role in available:
            name=prefix+'_'+role
            assert name.casefold() not in seen and len(name)<=63,name
            seen.add(name.casefold())
            args='params,varargin' if role=='analyzer' else 'varargin'
            forwarded='params,varargin{:}' if role=='analyzer' else 'varargin{:}'
            files[OUT/folder/(name+'.m')]=(f'function retval = {name}({args})\n'
                 f'% {location} ({tag}). See acMenuCatalog for available operations.\n'
                 f"retval = acMenuInvoke('{tag}','{role}',{forwarded});\nend\n")
        menus.append(dict(tag=tag,master=master,guide=guide,masterVisibility=row['master_initial'],
                          guideVisibility=row['guide_initial'],entry=prefix,folder=folder,
                          default=default if choices else '',roles=' '.join(available),choices=' '.join(sorted(choices))))
    actual={s for m in menus for s in m['choices'].split()}
    assert set(engines)==actual, set(engines)-actual
    # Preserve the current desktop's declaration order within each top-level menu.
    declarations={r['tag']:r for r in menu_rows}
    def position(m):
        source=declarations[m['tag']]['master_source']
        return (0,int(source.rsplit(':',1)[1])) if source else (1,menu_rows.index(declarations[m['tag']]))
    menus.sort(key=position)
    catalogue=dict(version=1,menus=menus,engines=list(engines.values()))
    files[OUT/'catalogue.json']=encode_catalogue(catalogue)
    files[ROOT/'migration/menu/MENUS.md']=menu_table(menus)
    # Each original registered role must be reachable through a concrete public file.
    for operation,roles in by_name.items():
        for role,row in roles.items():
            assert (ROOT/row['wrapper_path']).is_file(),row['wrapper_path']
            assert any(operation in m['choices'].split() and role in m['roles'].split()
                       and OUT/m['folder']/(m['entry']+'_'+role+'.m') in files for m in menus),(operation,role)
    return files,menus,by_name

def encode_catalogue(cat):
    def lines(rows):
        return ',\n'.join(json.dumps(row,ensure_ascii=False,separators=(',',':')) for row in rows)
    return '{"version":1,"menus":[\n'+lines(cat['menus'])+'],\n"engines":[\n'+lines(cat['engines'])+']}\n'

def menu_table(menus):
    out=['# 按 Acycle 菜单查找接口','','基于 master 的主窗口顺序；同一条目下的 GUIDE 选择值以 `_legacy` 结尾。表中 `X (两版)` 可展开为 `X` 和 `X_legacy`。只有某一版的选择逐字列出。前缀接 `_helper`、`_analyzer` 或 `_plotter`，具体角色见对应行。菜单标题只承担分组。验证脚本、核函数和输入示例列在对应菜单下，表示可独立调用的附属操作。','','[调用与复现示例](README.zh-CN.md) · [完整机器清单](../../code/interface/catalogue.json)','']
    sections=defaultdict(list)
    for m in menus:
        heading=(m['master'] or m['guide']).split(' > ')[0] if m['master'] else '仅 GUIDE 保留'
        sections[heading].append(m)
    for heading,items in sections.items():
        out+=['## '+heading,'','| 菜单路径及状态 | 公开函数前缀 / 角色 | 默认选择 | 全部 params.operation |','|---|---|---|---|']
        for m in items:
            path=(m['master'] or m['guide']).replace('|',r'\|')
            if m['masterVisibility']=='hidden': path+='（GUI 隐藏）'
            choices=set(m['choices'].split()); paired=sorted(x for x in choices if x+'_legacy' in choices)
            unique=choices-set(paired)-{x+'_legacy' for x in paired}
            items_text=', '.join(['`'+x+'` (两版)' for x in paired]+['`'+x+'`' for x in sorted(unique)])
            api=('`'+m['entry']+'` · '+m['roles'].replace(' ',' / ')) if m['entry'] else '菜单标题'
            out.append(f"| {path} | {api} | {m['default'] or '—'} | {items_text or '—'} |")
        out.append('')
    return '\n'.join(out).rstrip()+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write',action='store_true')
    args=p.parse_args()
    files,menus,old=build()
    for path,content in files.items():
        if args.write:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding='utf-8')
        elif not path.is_file() or path.read_text(encoding='utf-8')!=content:
            raise SystemExit(f'Outdated menu interface: {path}')
    actual=set(OUT.glob('**/acMenu*_*er.m'))
    assert actual=={p for p in files if p.suffix=='.m'}, actual.symmetric_difference(files)
    print(f'{len(menus)-1} menu tags + Mini-Robot; {sum(p.suffix=='.m' for p in files)} public role files; '
          f'{len(old)} versioned packages, {sum(map(len,old.values()))} original roles accounted for.')
