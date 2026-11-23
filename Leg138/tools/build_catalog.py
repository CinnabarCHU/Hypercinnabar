"""Rebuild the Leg 138 catalogue from the supplied edition tables. Uses the Python standard library."""
import argparse
import csv
import gzip
import json
import re
import tempfile
import sqlite3
from pathlib import Path

def rows(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path,'rt',encoding='utf-8-sig',newline='') as stream:
        yield from csv.DictReader(stream)

def json_lines(path):
    with gzip.open(path,'rt',encoding='utf-8') as stream:
        for line in stream:
            yield json.loads(line)

def enc(obj):
    return json.dumps(obj,ensure_ascii=False,separators=(',',':'))

def ir_ch(ch):
    return f'IR.C{int(ch):02d}'

def sr_ch(ch):
    return f'SR.C{int(ch):02d}'

SCHEMA = """
CREATE TABLE documents(doc_id TEXT PRIMARY KEY,series TEXT,chapter TEXT,site TEXT,title TEXT,role TEXT,local_source TEXT,url TEXT,doi TEXT,pdf_pages INTEGER);
CREATE TABLE pages(id INTEGER PRIMARY KEY,doc_id TEXT REFERENCES documents(doc_id),pdf_page INTEGER,printed_page TEXT,basis TEXT,text TEXT,UNIQUE(doc_id,pdf_page));
CREATE VIRTUAL TABLE page_fts USING fts5(text,content=pages,content_rowid=id, tokenize="unicode61 remove_diacritics 2");
CREATE TABLE items(item_id TEXT PRIMARY KEY,doc_id TEXT REFERENCES documents(doc_id),kind TEXT,title TEXT,pdf_page INTEGER,last_page INTEGER,status TEXT,native_path TEXT);
CREATE TABLE evidence(id INTEGER PRIMARY KEY,site TEXT,doc_id TEXT REFERENCES documents(doc_id),item_id TEXT,role TEXT,source_path TEXT,pdf_page INTEGER,first_line INTEGER,last_line INTEGER,excerpt TEXT);
CREATE INDEX by_site ON evidence(site,role,doc_id,item_id);
CREATE INDEX by_item ON evidence(item_id,site);
CREATE INDEX by_doc ON evidence(doc_id,site);
CREATE INDEX by_source ON evidence(site,source_path);
CREATE TABLE plate_pages(id INTEGER PRIMARY KEY,local_source TEXT,url TEXT,site TEXT,kind TEXT,pdf_page INTEGER,text TEXT);
CREATE VIRTUAL TABLE plate_fts USING fts5(text,content=plate_pages,content_rowid=id);
CREATE TABLE dataset_items(dataset_id TEXT REFERENCES datasets(dataset_id),item_id TEXT,PRIMARY KEY(dataset_id,item_id));
CREATE TABLE sites(site TEXT PRIMARY KEY,proposed_site TEXT,status TEXT,record_json TEXT);
CREATE TABLE plans(proposed_site TEXT PRIMARY KEY,site TEXT,record_json TEXT);
CREATE TABLE assets(local_path TEXT PRIMARY KEY,series TEXT,role TEXT,site TEXT,bytes INTEGER,sha256 TEXT,url TEXT);
CREATE INDEX asset_site ON assets(site,series);
CREATE TABLE datasets(dataset_id TEXT PRIMARY KEY,item_id TEXT,series TEXT,description TEXT,storage TEXT,local_path TEXT,scope_site TEXT,records INTEGER,fields_json TEXT,source_path TEXT);
CREATE TABLE sr_rows(dataset_id TEXT REFERENCES datasets(dataset_id),record_no INTEGER,line_first INTEGER,line_last INTEGER,sites TEXT,values_json TEXT,raw_json TEXT,PRIMARY KEY(dataset_id,record_no)) WITHOUT ROWID;
CREATE TABLE field_notes(dataset_id TEXT,field TEXT,role TEXT,note TEXT,source TEXT);
CREATE INDEX fields_by_dataset ON field_notes(dataset_id);
CREATE TABLE native_ir(item_id TEXT,line_number INTEGER,source_path TEXT,raw_text TEXT,line_ending TEXT,tokens_with_positions TEXT,PRIMARY KEY(item_id,line_number)) WITHOUT ROWID;
"""
def build(root,edited,dest):
    dest=dest.resolve()
    with tempfile.NamedTemporaryFile(prefix=dest.stem+'.building-',suffix='.sqlite',dir=dest.parent,delete=False) as stream:
        tmp=Path(stream.name)
    db=sqlite3.connect(tmp)
    try:
        populate(root.resolve(),edited,db)
        db.commit()
        db.close()
        tmp.replace(dest)
    finally:
        db.close()
        tmp.unlink(missing_ok=True)

def populate(root,edited,db):
    db.execute('PRAGMA foreign_keys=ON');db.executescript(SCHEMA)
    mod=lambda name:root/name/'core'
    def add(table,*values):
        db.execute('INSERT INTO '+table+' VALUES ('+','.join('?' for _ in values)+')',values)
    def evidence(site,doc,item,role,path='',page='',lo='',hi='',excerpt=''):
        if site:
            add('evidence',None,str(site),doc,item or None,role,path or None,page or None,lo or None,hi or None,excerpt or None)
    for r in rows(edited/'data/documents.csv'):
        add('documents',*r.values())
    for r in json_lines(edited/'data/pages.jsonl.gz'):
        add('pages',None,r['doc_id'],r['pdf_page'],r['printed_page'],r['basis'],r['text'])
    dpaths={d[0]:d[1] for d in db.execute('SELECT doc_id,local_source FROM documents')}
    sp=mod('sppr')/'data'
    pairs=list(rows(sp/'site_crosswalk.csv'))
    known={r['proposed_site']:r['site'] for r in pairs if r['proposed_site']}
    for r in pairs:
        if r['site']:add('sites',r['site'],r['proposed_site'],r['status'],enc(r))
        if r['proposed_site']:add('plans',r['proposed_site'],r['site'],enc(r))
    for r in rows(sp/'report_items.csv'):
        key=r['item_id'];doc=r['doc_id']
        add('items',key,doc,r['kind'],r['title'],r['pdf_first'] or None,r['pdf_last'] or None,r['status'],None)
        sites=set(re.findall(r'(?<!\d)(84[4-9]|85[0-4])(?!\d)',r['scope']))
        for proposed in re.findall(r'\b[EW]EQ-\d+A?\b',r['scope']+' '+key):
            if known.get(proposed):sites.add(known[proposed])
        for site in sorted(sites):
            evidence(site,doc,key,'published_scope',dpaths[doc],r['pdf_first'])
    for r in rows(sp/'pr_coring.csv'):
        if r['row_kind']=='hole':
            evidence(r['site'],'PR','PR.T1','published_hole_row',dpaths['PR'],r['pdf_page'],excerpt=r['hole'])
    for r in rows(sp/'pr_site_figures.csv'):
        evidence(r['site'],'PR',r['item_id'],r['role'],dpaths['PR'],r['pdf_page'])
    for r in rows(mod('ir')/'chapter_items.csv'):
        doc=ir_ch(r['chapter']);key=r['item_id'];native=r['native_path']
        add('items',key,doc,r['kind'],r['title'],r['pdf_page'] or None,None,r['status'],'ir/primary/'+native if native else None)
        evidence(r['site'],doc,key,'site_chapter',dpaths[doc],r['pdf_page'])
    for r in rows(mod('sr')/'items.csv'):
        doc=sr_ch(r['chapter']);add('items',r['item_id'],doc,r['kind'],r['label'],r['pdf_page'] or None,None,r['status'],None)
    for r in rows(mod('sr')/'site_evidence.csv'):
        evidence(r['site'],sr_ch(r['chapter']),r['item_id'],r['evidence_role'],'sr/primary/'+r['source'],r['pdf_page'],excerpt=r['excerpt'])
    for r in rows(mod('sr')/'dataset_site_evidence.csv'):
        evidence(r['site'],sr_ch(r['chapter']),r['item_id'],r['evidence_role'],'sr/primary/'+r['source'],lo=r['first_line'],hi=r['last_line'],excerpt=r['dataset_id'])
    def asset(module,path,series,role,site,r):
        add('assets',module+'/primary/'+path,series,role,site or '',int(r['bytes']),r['sha256'],r['url'])
    for r in rows(sp/'source_manifest.csv'):asset('sppr',r['filename'],r['doc_id'],'report','',r)
    for r in rows(mod('ir')/'sources.csv'):
        p=r['path'];c=re.search(r'CHAP_(\d+)|ir138_(\d+)\.pdf',p)
        ch=int(next(v for v in c.groups() if v)) if c else 0
        asset('ir',p,'IR',r['role'],ch+835 if 9<=ch<=19 else '',r)
    backup=json.loads((edited/'data/source_package_checks.json').read_text())['archives']['SP_PR_IR']
    for entry in backup['separately_identified_directory_witnesses']:
        add('assets',entry['path'],'IR','distribution_directory','',entry['bytes'],entry['sha256'],'https://www-odp.tamu.edu/publications/138_IR/VOLUME/DATA/TABLES/')
    for r in rows(mod('sr')/'source_manifest.csv'):
        asset('sr',r['source'],'SR',r['channel']+'/'+r['kind'],'',r)
    for r in rows(mod('plates')/'data/plate_sources.csv'):
        asset('plates',r['source_path'],'PLATES',r['document_kind'],r['site'],r)
    plate_urls={r['source_path']:r['url'] for r in rows(mod('plates')/'data/plate_sources.csv')}
    for r in json_lines(mod('plates')/'data/plate_page_text.jsonl.gz'):
        add('plate_pages',None,'plates/primary/'+r['source_path'],plate_urls[r['source_path']],r['site'],r['document_kind'],r['pdf_page'],r['source_text_layer'])
    db.execute("INSERT INTO plate_fts(plate_fts) VALUES ('rebuild')")
    for r in rows(mod('plates')/'data/plate_directory_witness.csv'):
        asset('plates',r['source_path'],'PLATES','distribution_directory','',r)
    disc_index={r['path']:r for r in rows(mod('disc')/'file_index.csv.gz')}
    for r in rows(mod('disc')/'sources.csv'):
        entry=disc_index[r['path']]
        asset('disc',r['path'],'CD',entry['family']+'/'+entry['record_role'],entry['site'],r)
    for r in rows(mod('sr')/'datasets.csv'):
        add('datasets',r['dataset_id'],r['item_id'],'SR',r['description'],'sr_rows','sr/core/records.jsonl.gz','',int(r['records']),r['fields_json'],'sr/primary/'+r['source'])
    for r in json_lines(mod('sr')/'records.jsonl.gz'):
        add('sr_rows',r['d'],r['n'],r['lo'],r['hi'],'|'+ '|'.join(map(str,r['s']))+'|',enc(r.get('v')),enc({k:v for k,v in r.items() if k not in ['d','n','lo','hi','s','v']}) )
    for r in rows(mod('ir')/'native_lines.csv.gz'):
        add('native_ir',r['item_id'],r['line_number'],'ir/primary/'+r['source_path'],r['raw_text'],r['line_ending'],r['tokens_with_positions'])
    for r in rows(mod('ir')/'native_tables.csv'):
        add('datasets',r['item_id']+'.NATIVE',r['item_id'],'IR','Literal native lines and field positions','native_ir','ir/core/native_lines.csv.gz',r['site'],int(r['line_count']),None,'ir/primary/'+r['source_path'])
    def csv_set(key,item,series,desc,path,site='',source='',expected=None):
        file=(edited/path if path.startswith('data/') else root/path)
        it=rows(file);first=next(it,None)
        n=(1+sum(1 for _ in it)) if first else 0
        if expected is not None:assert n==int(expected),(key,n,expected)
        add('datasets',key,item,series,desc,'csv',path,site,n,enc(list(first or {})),source)
    for r in rows(mod('sr')/'print_datasets.csv'):
        scope=r['site'] if r['site'].isdigit() else ''
        csv_set(r['dataset_id'],r['item_id'],'SR',r['description'],'sr/core/'+r['file'],scope,'sr/primary/'+r['source'],r['records'])
        scope_sites={scope} if scope else {line.get('site','') for line in rows(mod('sr')/r['file'])}
        for station in sorted(scope_sites):
            if station.isdigit() and 844<=int(station)<=854:
                evidence(station,sr_ch(r['chapter']),r['item_id'],'transcribed_print_dataset','sr/primary/'+r['source'],r['source_pdf_page_from'],excerpt=r['dataset_id'])
    for key,item,series,desc,path in [
        ('IR.CARBON','', 'IR','Published chemistry fields. Empty cells and flags preserved.','ir/core/tables/carbons.csv'),
        ('IR.CORING','','IR','Cores and printed hole subtotals','ir/core/tables/coring.csv'),
        ('IR.COMPOSITE','','IR','Per-core published composite depth intervals','ir/core/tables/core_depths.csv'),
        ('IR.HOLE_HEADERS','','IR','Individual reported header fields with coordinates on the source page','data/ir_hole_headers.csv'),
        ('IR.ORGANIC_C','','IR','Organic carbon with published footnotes and native row locator','data/carbon_reported.csv'),
        ('IR.CARBON_WITNESSES','','IR','Comparison of the table and shipboard carbon file by unambiguous sample key','data/carbon_distribution_comparison.csv'),
        ('PR.CORING','PR.T1','PR','Holes, site subtotals and total','sppr/core/data/pr_coring.csv'),
        ('PR.IR.CORING','','PR/IR','Paired reported fields with kept differences','data/pr_ir_field_comparison.csv'),
        ('PR.RATE_CHECK','','PR/IR','Sedimentation rate comparisons by site','figures/core/data/pr_rate_summary.csv'),
        ('PR.F15.TRACE','PR.F15','PR','Graphic-derived Site 851 backtrack, not a digital plate model','sppr/core/data/pr_fig15_backtrack.csv'),
        ('SP.SITE_CARDS','','SP','Twelve proofread proposed site cards','sppr/core/data/sp_site_cards.csv'),
        ('CD.GRAPE_REPLAY','','CD','Individual published software replay stages','disc/core/replay/grape_replay.csv')]:
        csv_set(key,item,series,desc,path,site='851' if key=='PR.F15.TRACE' else '')
    for p in sorted((mod('ir')/'print_tables').glob('*.csv')):
        key=p.stem.replace('_','.');csv_set(key+'.PRINT',key,'IR','Transcribed from report with source locators','ir/core/print_tables/'+p.name,'847' if key.startswith('IR12.') else '')
    for p in sorted(mod('disc').glob('*.csv.gz')):
        csv_set('CD.'+p.name.removesuffix('.csv.gz').upper(),'','CD','Shipboard distribution, see field notes and original source row','disc/core/'+p.name)
    by_path={path:key for key,path in db.execute("SELECT dataset_id,local_path FROM datasets WHERE storage='csv' AND series='IR'")}
    by_native={item:key for key,item in db.execute("SELECT dataset_id,item_id FROM datasets WHERE storage='native_ir'")}
    aliases={}
    for r in rows(mod('ir')/'datasets.csv'):
        path='ir/core/'+r['data_path'];ident=r['dataset_id']
        if r['data_path']=='native_lines.csv.gz':key=by_native[r['source_items']]
        elif path in by_path:key=by_path[path]
        else:
            key=ident
            csv_set(key,r['source_items'] if '|' not in r['source_items'] else None,'IR',r['description'],path,r['scope'] if r['scope'].isdigit() else '',expected=r['row_count'])
        aliases[ident]=key
    db.execute("INSERT OR IGNORE INTO dataset_items SELECT dataset_id,item_id FROM datasets WHERE item_id IS NOT NULL AND item_id != ''")
    for r in rows(mod('ir')/'dataset_items.csv'):
        db.execute("INSERT OR IGNORE INTO dataset_items VALUES (?,?)",(aliases[r['dataset_id']],r['item_id']))
    csv_set('CD.GRAPE_SOURCE_ROWS','','CD','Published MCD row linked to the hole FIN source row','disc/core/replay/grape_source_lines.csv.gz')
    csv_set('CD.SPLICE_CHECK','','CD','Comparison of selected hole rows and distributed composite rows','disc/core/replay/splice_membership.csv')
    for key,series,path,desc in [
        ('IR.EDITORIAL_NOTES','IR','ir/core/editorial_notes.csv','Editorial comparisons between published witnesses and source arithmetic'),
        ('IR.DEPTH_CHECK','IR','data/ir_depth_checks.csv','Published rig-floor and sea-level depth arithmetic'),
        ('PR.RATE_INTERVAL','PR/IR','figures/core/data/pr_rate_check.csv','Every published rate interval and its graphic test status'),
        ('IR.MEAN_INTERVAL','IR','figures/core/data/ir_mean_intervals.csv','Native IR age, accumulation and sedimentation intervals'),
        ('PR.PLOT_MARKS','PR','figures/core/data/pr_printed_marks.csv','Graphic digitization of 44 organic-carbon marks'),
        ('PR.MAR_CHECK','PR/IR','figures/core/data/pr_mar_spotcheck.csv','Printed accumulation rate and published tabular comparison'),
        ('PR.PLOT_WORKFLOW','PR','sppr/core/data/pr_plot_workflows.csv','Shipboard processing statements in 22 plot captions'),
        ('SR.ERRATA','SR','sr/core/errata.csv','Original and replacement publication references'),
        ('PLATES.PHOTO','PLATES','plates/core/data/native_photo_catalog.csv','Original photograph objects and embedded JPEG hashes'),
        ('PLATES.OPTICAL','PLATES','plates/core/data/optical_regions.csv','Checked sediment and ruler windows in original JPEG coordinates'),
        ('PLATES.VCD','PLATES','plates/core/data/vcd_pages.csv','Visual core description leaves and marks'),
        ('PLATES.SMEAR','PLATES','plates/core/data/smear_pages.csv','Smear-slide leaves, source features and identity'),
        ('CD.REFLECTANCE_TEN','CD','disc/core/replay/reflectance_511_to_ten.csv','511 calibrated bands vs 10 distributed bands'),
        ('CD.REFLECTANCE_THREE','CD','disc/core/replay/reflectance_ten_to_three.csv','10 distributed bands vs 3 distributed bands')]:
        csv_set(key,None,series,desc,path)
    for r in rows(mod('sr')/'field_roles.csv'):
        add('field_notes',r['dataset_id'],r['field'],r['descriptive_role'],'','sr/core/field_roles.csv')
    for r in rows(mod('disc')/'field_notes.csv'):
        for field in r['fields'].split(';'):
            add('field_notes','CD.FAMILY.'+r['family'].upper(),field,r['record_role'],r['interpretation'],'disc/core/field_notes.csv')
    for field,role in [('run_1_carbonate_pct','first_published_run'),('run_2_carbonate_pct','second_published_run'),('run_3_carbonate_pct','third_published_run_when_present'),('published_absolute_difference_pct','published_summary_statistic')]:
        add('field_notes','IR.carbonate_repeat_samples',field,role,'Values retained as published','ir/core/carbonate_repeat_sources.csv')
    from catalog_edition2 import install
    install(db,root,aliases,csv_set)
    db.execute("INSERT INTO page_fts(page_fts) VALUES ('rebuild')")
    assert db.execute('PRAGMA integrity_check').fetchone()==('ok',)
    assert not list(db.execute('PRAGMA foreign_key_check'))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    default=Path(__file__).resolve().parents[1]
    parser.add_argument('--root',type=Path,default=default,help='Edition directory containing the modules')
    parser.add_argument('--edited',type=Path,default=default,help='Directory containing data/documents.csv')
    parser.add_argument('--out',type=Path,default=default/'Leg138.sqlite')
    a=parser.parse_args();build(a.root,a.edited,a.out)
