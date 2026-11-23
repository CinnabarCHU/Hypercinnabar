"""Collect prior editions and source-native tables without conflating their publication status."""
from collections import defaultdict
from pathlib import Path
import csv, gzip, hashlib, json, re, shutil

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as stream:return list(csv.DictReader(stream))

def write(path, rows):
    with path.open('w',encoding='utf-8',newline='') as stream:
        out=csv.DictWriter(stream,fieldnames=list(rows[0]));out.writeheader();out.writerows(rows)

def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def prepare(root,out,selected):
    folder=out/'resources';folder.mkdir(exist_ok=True)
    assets=[]; used={}
    def add(doc,page,item,label,source,typ='file',rows=None,columns=None,asset_page=1,locator='item_anchor',representation='',note=''):
        if doc not in selected:return
        if not source.is_file():raise FileNotFoundError(source)
        ext='.csv' if rows is not None else source.suffix.lower()
        if ext not in ('.gz','.csv','.pdf','.png','.svg','.tsv','.txt'):ext='.txt'
        filename=re.sub(r'[^\w.-]+','_',item+'_'+label,flags=re.ASCII).strip('_')+ext
        path=folder/filename
        signature=(filename,str(source),item,label)
        if filename in used and used[filename]!=signature:raise ValueError(filename)
        used[filename]=signature
        if rows is None:shutil.copyfile(source,path)
        else:write(path,rows)
        assets.append(dict(doc_id=doc,source_page=page or 1,item_id=item,label=label,kind=typ,
                           page_relation=locator if page else 'chapter_entry_only',
                           file='resources/'+filename,asset_page=asset_page,
                           source_path=str(source.relative_to(root)),sha256=digest(path),
                           display_columns=columns or [],representation=representation,editorial_note=note))
    sp=root/'sppr/core/data'
    sp_items={r['item_id']:r for r in read(sp/'report_items.csv')}
    for name in ('sp_time','sp_totals','sp_transit','sp_logging','pr_coring','pr_operations','pr_lab','pr_time_chart'):
        path=sp/(name+'.csv'); rows=read(path)
        for item in sorted({r['item_id'] for r in rows}):
            it=sp_items[item];rr=[r for r in rows if r['item_id']==item]
            add(it['doc_id'],int(it['pdf_first']),item,name,path,'table',rr,[k for k in rr[0] if k not in ('item_id','pdf_page')])
    for idx,r in enumerate(read(sp/'sp_site_cards.csv')):
        add('SP',int(r['pdf_page']),r['item_id'],'collated site card',root/'sppr/core/publication/Leg138_SP_Proposed_Sites.pdf','card',asset_page=3*idx+1)
    for r in read(root/'figures/core/data/figure_index.csv'):
        n=int(r['pr_pdf_page']);id='PR.F'+r['pr_figure'];stem=root/'figures/core'/r['svg']
        add('PR',n,id,'reconstructed rate panels',stem.with_suffix('.pdf'),'figure')
        add('PR',n,id,'vector panels',stem,'svg')
    add('PR',50,'PR.F15','graphic coordinate check',root/'sppr/core/figures/pr_fig15_graphic_check.pdf','figure')
    add('PR',50,'PR.F15','digitized published symbols',sp/'pr_fig15_backtrack.csv','table',columns=['age_ma','latitude_deg_approx','longitude_deg_approx'])
    ir=root/'ir/core'
    items={r['item_id']:r for r in read(ir/'chapter_items.csv')}
    def irloc(item):
        i=items[item];return 'IR.C'+i['chapter'].zfill(2),int(i['pdf_page'] or 0)
    for r in read(ir/'native_tables.csv'):
        d,p=irloc(r['item_id']);add(d,p,r['item_id'],'native electronic table',root/'ir/primary'/r['source_path'])
    for p in sorted((ir/'print_tables').glob('*.csv')):
        ident=p.stem.replace('_','.');d,n=irloc(ident);rs=read(p)
        cols=[k for k in rs[0] if k not in ('pdf_page','print_row','printed_page')]
        page=int(rs[0].get('pdf_page') or n)
        add(d,page,ident,'collated print table',p,'table',columns=cols)
    for p in sorted((ir/'site846_prior').glob('table-*.csv')):
        id='IR11.T'+p.stem.split('-')[-1];d,n=irloc(id)
        add(d,n,id,'prior Site 846 table transcription',p,'csv')
    for p in sorted((ir/'tables').glob('*.csv')):
        byid=defaultdict(list)
        for r in read(p):byid[r['item_id']].append(r)
        for id,rs in byid.items():
            d,n=irloc(id);add(d,n,id,'fielded '+p.stem,p,'csv',rs)
    samples=read(ir/'carbonate_repeat_samples.csv')
    for r in read(ir/'carbonate_repeat_sources.csv'):
        item=r['item_id'];d,n=irloc(item);pg=int(r['chapter_pdf_page']);rs=[v for v in samples if v['item_id']==item]
        add(d,pg,item,'carbonate replicate measurements',ir/'carbonate_repeat_samples.csv','table',rs,
            ['reported_hole','sample_label','depth_mbsf','depth_mcd','run_1_carbonate_pct','run_2_carbonate_pct','run_3_carbonate_pct','published_absolute_difference_pct'],
            locator=r['chapter_locator_role'])
    sr=root/'sr/core'
    sri={r['item_id']:r for r in read(sr/'edition2/data/objects.csv') if r['status']=='accepted'}
    for i,r in enumerate(read(sr/'datasets.csv')):
        item=r['item_id'];p=int(sri.get(item,{}).get('pdf_page') or 0);doc='SR.C'+r['chapter'].zfill(2)
        add(doc,p,item,'electronic '+r['dataset_id'],root/'sr/primary'/r['source'])
    for r in read(sr/'print_datasets.csv'):
        p=sr/r['file'];rs=read(p)
        add('SR.C'+r['chapter'].zfill(2),int(r['source_pdf_page_from']),r['item_id'],'print transcription '+r['dataset_id'],p,'table',
            columns=[k for k in rs[0] if k not in ('page','source_page','pdf_page','printed_page','printed_row')])
    for id,rel in [('SR.C06.FIGURE11','figures/SR06_Figure11_comparison.pdf'),('SR.C27.FIGURE3','verified846/proofs/Chapter27_Figure3_Comparison.pdf')]:
        r=sri[id]
        add('SR.C'+r['chapter'].zfill(2),int(r['pdf_page']),id,'reconstruction and source comparison',sr/rel,'figure')
    # The individual station cards share a single typeset PDF: keep one physical file.
    shared=folder/'SP_collated_site_cards.pdf'
    for a in assets:
        if a['kind']=='card':
            old=out/a['file']
            if not shared.exists():shutil.copyfile(old,shared)
            old.unlink();a['file']='resources/'+shared.name
    from structured_updates import attach
    attach(root,items,add)
    return assets
