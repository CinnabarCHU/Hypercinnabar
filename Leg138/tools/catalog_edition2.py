"""Import reviewed publication objects, named IR rows, editorial apparatus and source-linked ROI geometry."""
import csv
import gzip
import json
import re
from collections import defaultdict
from itertools import chain
from pathlib import Path

DDL = """
CREATE TABLE item_reviews(item_id TEXT PRIMARY KEY REFERENCES items(item_id), state TEXT NOT NULL, review_basis TEXT, source_path TEXT, detail_json TEXT NOT NULL);
CREATE INDEX reviews_by_state ON item_reviews(state,item_id);
CREATE TABLE ir_table_review(item_id TEXT PRIMARY KEY REFERENCES items(item_id), site TEXT, default_dataset TEXT REFERENCES datasets(dataset_id), representation TEXT, quality TEXT, named_rows INTEGER NOT NULL, detail_json TEXT NOT NULL);
CREATE TABLE ir_named(item_id TEXT REFERENCES ir_table_review(item_id), row_no INTEGER, sites TEXT, reading_status TEXT NOT NULL, record_json TEXT NOT NULL, PRIMARY KEY(item_id,row_no)) WITHOUT ROWID;
CREATE TABLE ir_print_cells(item_id TEXT REFERENCES items(item_id), row_no INTEGER, field TEXT, status TEXT, record_json TEXT NOT NULL, PRIMARY KEY(item_id,row_no,field)) WITHOUT ROWID;
CREATE TABLE sr_apparatus(dataset_id TEXT, record_no INTEGER, line_first INTEGER, record_json TEXT NOT NULL, PRIMARY KEY(dataset_id,record_no), FOREIGN KEY(dataset_id,record_no) REFERENCES sr_rows(dataset_id,record_no)) WITHOUT ROWID;
CREATE TABLE optical_roi(roi_id TEXT PRIMARY KEY, core_id TEXT, site TEXT, role TEXT, source_path TEXT, record_json TEXT NOT NULL);
CREATE INDEX roi_filters ON optical_roi(site,core_id,role);
CREATE INDEX roi_cores ON optical_roi(core_id,role);
"""
def records(path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt',newline='',encoding='utf-8-sig') as f:
        yield from csv.DictReader(f)
def enc(v):
    return json.dumps(v,ensure_ascii=False,separators=(',',':'))
def manifest_rows(path):return list(records(path))
def table_id(path):return path.name.split('.csv')[0].upper()
def site_tags(row,scope=''):
    sites=set()
    if scope:sites.update(k for k in re.split(r'[|, ]+',scope) if k.isdigit())
    for key in ('site','directory_site','site_number','source_row_label','site_or_summary_printed','sites','printed_site_group','reported_hole','hole','station'):
        for k in re.findall(r'(?<!\d)(?:84[4-9]|85[0-4]|677)(?=[A-E]?\b)',str(row.get(key,'') or '')):
            sites.add(k)
    if 'printed_site_group' in row:
        sites.update(s for s in str(row['printed_site_group']).split('|') if s.isdigit())
    for key in row:
        m=re.match(r'^site[_ ]?(84[4-9]|85[0-4])(?:_|$)',key,re.I)
        if m:sites.add(m[1])
    return '|'+ '|'.join(sorted(sites))+'|'
def import_ir(db,root,aliases,csv_set):
    base=root/'ir/core'
    native={r['source_items']:r for r in records(base/'edition2_native/datasets.csv')}
    ncoverage={r['item_id']:r for r in records(base/'edition2_native/coverage.csv')}
    printed={r['item_id']:r for r in records(base/'edition2_print/data/datasets.csv')}
    if native.keys()&printed.keys():raise ValueError('A table has two second-edition defaults')
    previous={r['dataset_id']:r for r in records(base/'datasets.csv')}
    linked=defaultdict(list)
    for mapping in records(base/'dataset_items.csv'):linked[mapping['item_id']].append(previous[mapping['dataset_id']])
    print_rows=defaultdict(list)
    for r in records(base/'edition2_print/data/print_rows.csv.gz'):
        r['values']=json.loads(r.pop('cell_readings_json'));print_rows[r['item_id']].append(r)
    def preference(r):
        role=r['representation']
        if r['dataset_id']=='IR.carbonate_repeat_samples':return 0
        order=['scan_collated_print_transcription','site846_previous_print_transcription','named_fields_from_distributed_tables','site846_previous_native_table','named_fields_mixed_witness_per_table']
        return 1+order.index(role) if role in order else 100
    previous_files={}
    for item in records(base/'table_coverage.csv'):
        key,site=item['item_id'],item['site']
        if key in native:
            d=native[key];dsid=d['dataset_id'];coverage=ncoverage[key]
            path='ir/core/'+d['data_path'];source='ir/primary/'+coverage['source_path']
            csv_set(dsid,key,'IR',d['description'],path,site,source,expected=d['row_count'])
            values=list(records(root/path));quality=coverage['quality'];detail=coverage
        elif key in printed:
            d=printed[key];dsid=d['dataset_id'];source='ir/primary/'+d['source_pdf_path']
            values=print_rows[key]
            named=list(dict.fromkeys(k for row in values for k in row['values']))
            db.execute('INSERT INTO datasets VALUES (?,?,?,?,?,?,?,?,?,?)',(dsid,key,'IR',d['title_as_indexed'],'ir_print_rows','ir/core/'+d['data_path'],site,int(d['row_count']),enc(named),source))
            quality='print_with_cell_reviews' if int(d['review_cells']) else 'print_collated';detail=d
        else:
            options=sorted(linked[key],key=preference)
            if not options or preference(options[0])>=100:raise ValueError(f'{key} has no named representation')
            d=options[0];dsid=aliases[d['dataset_id']];path='ir/core/'+d['data_path']
            if path not in previous_files:previous_files[path]=list(records(root/path))
            values=previous_files[path]
            if '|' in d['source_items']:
                if not values or 'item_id' not in values[0]:raise ValueError(f'Missing row/item locator in {path}')
                values=[r for r in values if r['item_id']==key]
            quality='previous_named_representation';detail={'coverage':item,'inherited_dataset':d}
        if not values:raise ValueError(f'No named rows for {key}')
        if key in native or key in printed:
            if len(values)!=int(d['row_count']):raise ValueError(f'{key}: row count differs from manifest')
            db.execute('INSERT OR IGNORE INTO dataset_items VALUES (?,?)',(dsid,key))
        representation=d['representation']
        db.execute('INSERT INTO ir_table_review VALUES (?,?,?,?,?,?,?)',(key,site,dsid,representation,quality,len(values),enc(detail)))
        data=[]
        for n,row in enumerate(values,1):
            state=row.get('reading_status') or row.get('verification_flags') or quality
            copy=dict(row)
            if key in native and not row.get('verification_flags'):state='native_named_no_row_flag'
            if key in printed and int(row['print_row'])!=n:raise ValueError(f'{key} source row order changed')
            data.append((key,n,site_tags(row.get('values',row),site),state,enc(copy)))
        db.executemany('INSERT INTO ir_named VALUES (?,?,?,?,?)',data)
    db.executemany('INSERT INTO ir_print_cells VALUES (?,?,?,?,?)',
        ((r['item_id'],int(r['print_row']),r['field'],r['review_status'],enc(r)) for r in records(base/'edition2_print/data/print_cells.csv.gz')))
def import_sr(db,root,csv_set):
    base=root/'sr/core/edition2'
    for r in records(base/'data/objects.csv'):
        key=r['item_id'];doc=f"SR.C{int(r['chapter']):02d}";source='sr/primary/'+r['source'];loc=int(r['pdf_page'])
        old=db.execute('SELECT 1 FROM items WHERE item_id=?',(key,)).fetchone()
        if old:
            db.execute('UPDATE items SET pdf_page=?,title=? WHERE item_id=?',(loc,r['caption_or_heading_first_line'] or key,key))
        else:
            db.execute('INSERT INTO items VALUES (?,?,?,?,?,?,?,?)',(key,doc,r['kind'],r['caption_or_heading_first_line'],loc,None,'edition2_print_locator',None))
        db.execute('INSERT INTO item_reviews VALUES (?,?,?,?,?)',(key,r['status'],r['layout_basis'],source,enc(r)))
    with (base/'data/row_apparatus.jsonl').open() as f:
        for line in f:
            r=json.loads(line);db.execute('INSERT INTO sr_apparatus VALUES (?,?,?,?)',(r['dataset_id'],r['ordinal'],r['source_first_line'],enc(r)))
    for d in records(base/'data/print_datasets.csv'):
        source='sr/primary/'+d['source'];ds=d['dataset_id'];key=d['item_id'];path='sr/core/edition2/'+d['file']
        csv_set(ds,key,'SR',d['role']+' — '+d['editorial_note'],path,'',source,expected=d['records'])
        db.execute('INSERT OR IGNORE INTO dataset_items VALUES (?,?)',(ds,key))
        doc=f"SR.C{int(d['chapter']):02d}"
        for r in records(root/path):
            for site in filter(None,site_tags(r).split('|')):
                db.execute('INSERT INTO evidence VALUES (NULL,?,?,?,?,?,?,?,?,?)',(site,doc,key,'edition2_print_transcription',source,d['pdf_page'],None,None,ds+'#'+r['table_row']))
def register_files(db,root,csv_set):
    def register(key,series,path,description,site='',item=None,source='',expected=None):
        rel=str(path.relative_to(root))
        csv_set(key,item,series,description,rel,site,source,expected)
        if item:db.execute('INSERT OR IGNORE INTO dataset_items VALUES (?,?)',(key,item))
    sr=root/'sr/core/edition2/data'
    for name in ('historical_rotation_stages','ch23_depth_crosschecks','row_witness_lines','witnesses','changes','chapter_coverage'):
        item={'historical_rotation_stages':'SR.C01.TABLE1','ch23_depth_crosschecks':'SR.C23.TABLE3'}.get(name)
        register('SR.E2.'+name.upper(),'SR',sr/(name+'.csv'),name.replace('_',' '),item=item)
    disc=root/'disc/core/edition2'
    for path in sorted(chain(disc.glob('*.csv'),disc.glob('*.csv.gz'))):
        if path.name=='release_files.csv':continue
        name=table_id(path);site=''
        if name.startswith('BINARY_') or name in ('SPLICE844_OVERLAP','WATER_PRINT_DEPTHS844'):site='844'
        elif name in ('SPECTRUM849_IDENTITY_HYPOTHESIS','SPECTRUM854_VARIANT_ROWS','WATER_PRINT_ONLY848'):site={'SPECTRUM849_IDENTITY_HYPOTHESIS':'849','SPECTRUM854_VARIANT_ROWS':'854','WATER_PRINT_ONLY848':'848'}[name]
        register('CD.E2.'+name,'CD',path,name.replace('_',' '),site)
    for d in records(disc/'log_sources.csv'):
        s=d['directory_site'];name=d['file_series'];file=disc/d['extract_path']
        register(f'CD.E2.LOG.{s}.{name}','CD',file,f'Published {name} logging values at Site {s}; see CD.E2.LOG_DICTIONARY',s,
            source='disc/primary/'+d['source_file'],expected=d['data_records'])
    plates=root/'plates/core/edition2/data'
    for path in sorted(chain(plates.glob('*.csv'),plates.glob('*.csv.gz'))):
        name=table_id(path)
        register('PLATES.E2.'+name,'PLATES',path,name.replace('_',' '))
    photos={r['core_id']:r for r in records(plates/'photos.csv')}
    hashes={r['roi_id']:r['native_decoded_rgb_sha256'] for r in records(plates/'roi_rgb_checksums.csv.gz')}
    for r in records(plates/'regions.csv'):
        p=photos[r['core_id']];path='plates/primary/'+p['source_path']
        details={**r,'source_path':path,'source_url':p['source_url'],'jpeg_sha256':p['jpeg_sha256'],'pdf_sha256':p['pdf_sha256'],'pdf_image_xref':p['pdf_image_xref'],
            'native_image_width_px':p['width_px'],'native_image_height_px':p['height_px'],'human_review':p['human_review'],'native_decoded_rgb_sha256':hashes.get(r['roi_id'])}
        db.execute('INSERT INTO optical_roi VALUES (?,?,?,?,?,?)',(r['roi_id'],r['core_id'],r['site'],r['role'],path,enc(details)))
def install(db,root,aliases,csv_set):
    db.executescript(DDL)
    import_ir(db,root,aliases,csv_set)
    import_sr(db,root,csv_set)
    register_files(db,root,csv_set)
    import_geography(db,root)
    import_sr_print_slots(db,root,csv_set)

def import_geography(db,root):
    gpath=root/'ir/core/edition2_print/data/leg138_geography.geojson'
    features=json.loads(gpath.read_text())
    db.execute('CREATE TABLE geography_metadata(metadata_json TEXT NOT NULL)')
    db.execute('CREATE TABLE geographic_features(feature_id TEXT PRIMARY KEY, site INTEGER, chapter_site INTEGER, caption_site INTEGER, age_ma REAL, kind TEXT NOT NULL, position_status TEXT, has_geometry INTEGER NOT NULL, feature_json TEXT NOT NULL)')
    db.execute('CREATE INDEX geographic_age_site ON geographic_features(age_ma,site)')
    db.execute('INSERT INTO geography_metadata VALUES (?)',(enc({k:v for k,v in features.items() if k!='features'}),))
    for feature in features['features']:
        v=feature['properties']
        db.execute('INSERT INTO geographic_features VALUES (?,?,?,?,?,?,?,?,?)',(feature['id'],v.get('site'),v.get('chapter_site'),v.get('printed_caption_site'),v.get('age_Ma'),v['kind'],v.get('position_status'),int(feature['geometry'] is not None),enc(feature)))
def import_sr_print_slots(db,root,csv_set):
    base=root/'sr/core/edition2_print'
    db.executescript("""
    CREATE TABLE sr_print_review(item_id TEXT PRIMARY KEY REFERENCES items(item_id),prior_datasets TEXT,new_geometry_priority TEXT,status TEXT,review TEXT,details TEXT NOT NULL);
    CREATE TABLE sr_segments(segment TEXT PRIMARY KEY,item_id TEXT REFERENCES sr_print_review(item_id),page INTEGER,status TEXT,review TEXT,details TEXT NOT NULL);
    CREATE INDEX sr_segments_by_item ON sr_segments(item_id,page,segment);
    CREATE TABLE sr_slot_fields(segment TEXT REFERENCES sr_segments(segment),col INTEGER,field_header TEXT,status TEXT,PRIMARY KEY(segment,col)) WITHOUT ROWID;
    CREATE TABLE sr_print_slots(segment TEXT REFERENCES sr_segments(segment),role TEXT,row_no INTEGER,col INTEGER,record_json TEXT NOT NULL,PRIMARY KEY(segment,role,row_no,col)) WITHOUT ROWID;
    CREATE TABLE sr_slot_rows(item_id TEXT REFERENCES sr_print_review(item_id),segment TEXT REFERENCES sr_segments(segment),role TEXT,row_no INTEGER,PRIMARY KEY(item_id,segment,role,row_no)) WITHOUT ROWID;
    """)
    if not (base/'coverage.csv').exists():return
    coverage=list(records(base/'coverage.csv'))
    complete={r[0] for r in db.execute("SELECT i.item_id FROM items i JOIN item_reviews v USING(item_id) WHERE i.kind='table' AND v.state='accepted'")}
    if complete!={r['item_id'] for r in coverage}:raise ValueError('SR print coverage is incomplete for the approved table roster')
    for r in coverage:
        db.execute('INSERT INTO sr_print_review VALUES (?,?,?,?,?,?)',(r['item_id'],r['prior_dataset_ids'],r['new_geometry_priority'],r['status'],r['review'],enc(r)))
    db.executemany('INSERT INTO sr_segments VALUES (?,?,?,?,?,?)',((r['segment'],r['item_id'],r['pdf_page'],r['status'],r['review'],enc(r)) for r in records(base/'segments.csv')))
    db.executemany('INSERT INTO sr_slot_fields VALUES (?,?,?,?)',((r['segment'],int(r['col']),r['header_as_located'],r['status']) for r in records(base/'field_dictionary.csv.gz')))
    with gzip.open(base/'cells.jsonl.gz','rt') as f:
        db.executemany('INSERT INTO sr_print_slots VALUES (?,?,?,?,?)',((r['segment'],r['role'],int(r['row']),int(r['col']),enc(r)) for r in map(json.loads,f)))
    db.execute("""INSERT INTO sr_slot_rows SELECT s.item_id,c.segment,c.role,c.row_no FROM sr_print_slots c JOIN sr_segments s USING(segment) GROUP BY c.segment,c.role,c.row_no""")
    for r in coverage:
        key=r['item_id'];body=db.execute("SELECT COUNT(*) FROM sr_slot_rows WHERE item_id=? AND role='body'",(key,)).fetchone()[0]
        if not body:continue
        ds=key+'.PRINT.SLOTS.E2'
        db.execute('INSERT INTO datasets VALUES (?,?,?,?,?,?,?,?,?,?)',(ds,key,'SR','Positional cells in the print layout; candidate headers and editorial assessment are retained','sr_print_slots','sr/core/edition2_print/cells.jsonl.gz','',body,enc(['segment','pdf_page','row','cells']),'sr/primary/'+r['source']))
        db.execute('INSERT INTO dataset_items VALUES (?,?)',(ds,key))

    for p in sorted(base.glob('verified_*.csv')):
        file_rows=list(records(p))
        if not file_rows or 'item_id' not in file_rows[0]:continue
        keys={r['item_id'] for r in file_rows}
        if len(keys)!=1 or not keys<=complete:raise ValueError(f'Invalid item links in {p.name}')
        key=next(iter(keys));source='sr/primary/'+file_rows[0]['source']
        if p.name=='verified_c12_table14_p29_marks.csv':
            ds=key+'.PRINT.PAGE29.MARKS'
            desc='22 visible marks, each bound to one of four printed columns; sample identities cannot be assigned from this continuation panel.'
        else:
            ds=key+'.PRINT.RASTER_VERIFIED'
            desc='Named values visually read against the printed table; source page and row bounds retained.'
        csv_set(ds,key,'SR',desc,str(p.relative_to(root)),'',source,len(file_rows))
        db.execute('INSERT INTO dataset_items VALUES (?,?)',(ds,key))
        for r in file_rows:
            for site in filter(None,site_tags(r).split('|')):
                db.execute('INSERT INTO evidence VALUES (NULL,?,?,?,?,?,?,?,?,?)',(site,key.rsplit('.',1)[0],key,'edition2_print_transcription',source,r['pdf_page'],None,None,ds+'#'+str(r.get('row',''))))
