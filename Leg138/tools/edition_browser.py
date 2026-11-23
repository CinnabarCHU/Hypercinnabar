"""Build the offline expedition catalogue and station-scoped, on-demand CSV/geometry payloads."""
from collections import defaultdict
import csv
import gzip
import json
from pathlib import Path


def records(path):
    op=gzip.open if path.suffix=='.gz' else open
    with op(path,'rt',encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def compact(value):
    return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')


def build_portal(root,output_dir):
    read=lambda name:records(root/name)
    books=read('edition2/documents.csv')
    doc_meta={r['doc_id']:r for r in read('data/documents.csv')}
    reading={r['doc_id']:r for r in read('publication/chapters/catalog.csv')}
    site_ids=[str(x) for x in range(844,855)]
    public={'books':[],'ir':[],'sr':[],'photos':[],'smear':[]}
    shards={s:{'tables':{},'regions':defaultdict(list),'smear':defaultdict(list)} for s in ['all',*site_ids]}
    for b in books:
        ref=doc_meta.get(b['doc_id'],{})
        public['books'].append([b['doc_id'],b['title'],ref.get('site',''),b['series'],b['source_url'],
                     int(b['source_pdf_pages']),int(b['edition_pdf_pages']),int(reading[b['doc_id']]['reading_pages'])])
    print_ds={r['item_id']:r for r in read('ir/core/edition2_print/data/datasets.csv')}
    by_item=defaultdict(list)
    for path in ['ir/core/edition2_native/datasets.csv','ir/core/datasets.csv']:
        for r in read(path):
            if r['representation'] in {'source_lines_and_token_positions','evidence_directory'}:continue
            for key in r['source_items'].split('|'):by_item[key].append(r)
    # Cache shared files once. For aggregate datasets select the exact publication item from its own field.
    cache={}
    def source_rows(path):
        if path not in cache:cache[path]=read(path)
        return cache[path]
    for obj in read('ir/core/chapter_items.csv'):
        key=obj['item_id'];site=obj['site'];resource=[];role='';named=[];source_file=''
        for d in by_item[key]:
            lp='ir/core/'+d['data_path']
            resource.append([d['dataset_id'],lp])
        if key in print_ds:
            d=print_ds[key];source_file='ir/core/'+d['data_path']
            for r in source_rows(source_file):
                if r['item_id']==key:
                    values=json.loads(r['cell_readings_json'])
                    named.append(dict(item_id=key,print_row=r['print_row'],pdf_page=r['pdf_page'],printed_page=r['printed_page'],
                              reading_status=r['reading_status'],**values))
            resource.extend([[d['dataset_id'],source_file],['印格与判读状态','ir/core/'+d['cell_data_path']]])
            role='扫描印表'
        elif resource:
            # For a series with separate sample and run datasets show the sample view; both originals remain linked.
            rank=lambda d:0 if 'edition2_native/' in d['data_path'] else 1 if 'carbonate_repeat_samples' in d['dataset_id'] else 2 if 'tables/' in d['data_path'] else 3
            chosen=min(by_item[key],key=rank);source_file='ir/core/'+chosen['data_path']
            for r in source_rows(source_file):
                if 'item_id' not in r or not r['item_id'] or r['item_id']==key:
                    named.append(r)
            role='随盘电子表' if obj['native_path'] else '印表转录'
        if obj['kind']=='table':
            if not named:raise ValueError(f'No named rows for {key}')
            headers=list(dict.fromkeys(k for r in named for k in r))
            shards[site or 'all']['tables'][key]=[headers,[[r.get(k,'') for k in headers] for r in named]]
        src='https://www-odp.tamu.edu/publications/138_IR/'+obj['pdf_path']
        if obj['pdf_page']:src+='#page='+obj['pdf_page']
        public['ir'].append([key,obj['title'],site,obj['kind'],src,obj['printed_page'],len(named),resource,role,obj['chapter'],
                             'https://www-odp.tamu.edu/publications/138_IR/'+obj['native_path'] if obj['native_path'] else ''])
    tags=defaultdict(lambda:defaultdict(set))
    for r in read('sr/core/site_evidence.csv'):
        if r['site'] and r['item_id']:tags[r['item_id']][r['site']].add(r['evidence_role'])
    for r in read('sr/core/dataset_site_evidence.csv'):
        tags[r['item_id']][r['site']].add('source_table_rows')
    print_sr={r['item_id']:r for r in read('sr/core/edition2/data/print_datasets.csv')}
    sr_data=defaultdict(list)
    sr_sources={r['source']:r['url'] for r in read('sr/core/source_manifest.csv')}
    for ds in read('sr/core/datasets.csv'):
        sr_data[ds['item_id']].append([ds['dataset_id'],int(ds['records']),sr_sources.get(ds['source'],'')])

    chapters={r['chapter']:r for r in read('sr/core/chapters.csv')}
    for r in read('sr/core/edition2/data/objects.csv'):
        if r['status']!='accepted':continue
        key=r['item_id'];ch=r['chapter']
        srtags={s:sorted(e) for s,e in tags.get(key,{}).items() if s in site_ids}
        cap=r['caption_or_heading_first_line']; pr=print_sr.get(key)
        public['sr'].append([key,cap,','.join(sorted(srtags)),r['kind'],chapters[ch]['url']+'#page='+r['pdf_page'],
                            r['print_page'],r['pdf_page'],srtags,'sr/core/edition2/'+r['proof'] if r['proof'] else '',
                            'sr/core/edition2/'+pr['file'] if pr else '',ch,r['editorial_note'],sr_data.get(key,[])])
    counts=read('plates/core/edition2/data/photos.csv')
    reviewed={r['core_id']:r for r in read('plates/core/edition2/data/qa.csv')}
    for r in counts:
        cid=r['core_id'];q=reviewed.get(cid,{})
        public['photos'].append([cid,cid,r['site'],'photo',r['source_url'],int(r['liner_rois']),int(r['material_rois']),
                         r['geometric_status'],int(r['width_px']),int(r['height_px']),r['jpeg_sha256'],q.get('review_scope',''),q.get('note','')])
    for r in read('plates/core/edition2/data/regions.csv'):
        shards[r['site']]['regions'][r['core_id']].append([r['roi_id'],int(r['lane_ordinal']),r['role'],
            *[int(r[k]) for k in ('left_px','top_px','right_px_exclusive','bottom_px_exclusive')]])
    pg={(r['site'],r['pdf_page']):r for r in read('plates/core/edition2/data/smear_grid_pages.csv')}
    for r in read('plates/core/edition2/data/smear_rows.csv'):
        witness=pg[(r['site'],r['pdf_page'])]
        public['smear'].append([r['row_id'],r['sample_edition_literal'],r['site'],'smear',witness['source_url'],
                        r['printed_page'],r['depth_edition_literal'],r['lithology_edition_literal']])
    dictionary=defaultdict(dict)
    for r in read('plates/core/edition2/data/smear_field_dictionary.csv'):
        dictionary[r['site']][r['field_key']]=' · '.join(v for v in [r['printed_group'],r['printed_label']] if v)
    for r in read('plates/core/edition2/data/smear_cells.csv.gz'):
        shards[r['site']]['smear'][r['row_id']].append([r['field_key'],r['edition_reading'],r['source_ocr_literal'],
             r['status'],r['reading_evidence'],*[float(r[k]) for k in ('x0_pt','y0_pt','x1_pt','y1_pt')]])
    assert [len(x) for x in public.values()]==[76,911,809,593,1156]
    assert sum(len(x['tables']) for x in shards.values())==259
    assert sum(len(v) for s in shards.values() for v in s['regions'].values())==12989
    assert sum(len(v) for s in shards.values() for v in s['smear'].values())==25194
    geo_path=root/'ir/core/edition2_print/data/leg138_geography.geojson'
    geo_features=json.loads(geo_path.read_text())['features']
    sources={row[0]:row[4] for row in public['ir']}
    public['geo']=[]
    for f in geo_features:
        p=f['properties'];modern=p['kind']=='reported_hole_location'
        scope=p.get('chapter_site') or p.get('site')
        status=p.get('position_status','modern')
        url='https://www-odp.tamu.edu/publications/prelim/138PREL.PDF#page='+str(p['pdf_page']) if modern else sources[p['source_id']]
        desc=p.get('hole','') if modern else p['source_id']+' · '+str(p['age_Ma'])+' Ma'
        public['geo'].append([f['id'],desc,str(scope),status,url,p.get('age_Ma',-1),
                    p.get('latitude_deg_n'),p.get('longitude_deg_e'),p.get('latitude_print'),p.get('longitude_print'),
                    p.get('printed_caption_site'),p.get('chapter_site'),p['source_id'],p['default_map_eligible']])
    assert len(public['geo'])==191
    dest=output_dir/'browse-data';dest.mkdir(exist_ok=True)
    for s,contents in shards.items():
        # JSON arrays in a script load under file:// in Chromium, Firefox and Safari without fetch or an API.
        contents['smearLabels']=dictionary[s]
        (dest/(s+'.js')).write_text('window.registerStation('+compact(s)+','+compact(contents)+');\n',encoding='utf-8')
    template=Path(__file__).with_name('catalog_template.html').read_text()
    (output_dir/'catalog.html').write_text(template.replace('@CATALOG@',compact(public)),encoding='utf-8')
    return public
