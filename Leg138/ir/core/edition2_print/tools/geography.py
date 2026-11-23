"""Export published Leg 138 hole locations and the eleven chapter-level backtrack tables."""
from collections import Counter,defaultdict
from pathlib import Path
import argparse,csv,hashlib,json,re
from build import DATA, ROOT, load, save

GLOBAL_SOURCE='https://www-odp.tamu.edu/publications/138_IR/'

def dms(value):
    match=re.fullmatch(r'(\d+)°\s*(\d+(?:\.\d+)?)\s*[′\']([NSWE])',value)
    if not match:raise ValueError(value)
    d,m,sign=match.groups()
    result=int(d)+float(m)/60
    return round(result*(-1 if sign in 'SW' else 1),7)

def feature(key,coordinates,properties):
    return dict(type='Feature',id=key,
                geometry=dict(type='Point',coordinates=coordinates) if coordinates is not None else None,
                properties=properties)

def build(ir_primary,sppr_core):
    chapter_items={r['item_id']:r for r in load(ROOT.parent/'chapter_items.csv')}
    dataset_index={r['item_id']:r for r in load(DATA/'datasets.csv')}
    poles={r['item_id']:r for r in load(DATA/'pole_notes.csv')}
    print_rows=load(DATA/'print_rows.csv.gz')
    typed=defaultdict(list)
    for row in print_rows:typed[row['item_id']].append(row)
    tableids=sorted([*poles,'IR11.T21'])
    features=[];sources={};catalog=[]
    pr=next(r for r in load(sppr_core/'data/source_manifest.csv') if r['doc_id']=='PR')
    pr_id='PR.T1';prrows=load(sppr_core/'data/pr_coring.csv')
    sources[pr_id]=dict(report='Preliminary Report',published_title='Summary of coring operations on Leg 138',
          pdf_url=pr['url'],pdf_pages=[29,30],source_sha256=pr['sha256'],
          data_path='sppr/core/data/pr_coring.csv',role='reported drilling position for an individual hole')
    for lineno,r in enumerate(prrows,2):
        if r['row_kind']!='hole':continue
        lat,lon=dms(r['latitude']),dms(r['longitude'])
        site,hole=int(r['site']),r['hole']
        features.append(feature('PR.T1.'+hole,[lon,lat],dict(kind='reported_hole_location',source_id=pr_id,
           site=site,hole=hole,pdf_page=int(r['pdf_page']),csv_line=lineno,
           latitude_print=r['latitude'],longitude_print=r['longitude'],
           latitude_deg_n=lat,longitude_deg_e=lon,default_map_eligible=True)))
    for table in tableids:
        ref=chapter_items[table];site=int(ref['site']);pg=int(ref['pdf_page']);printed=int(ref['printed_page'])
        scope_status='printed_caption_conflicts_with_chapter' if table=='IR19.T15' else 'chapter_and_caption_agree'
        caption_site=851 if table=='IR19.T15' else site
        caption='Table 21. Paleolatitudes for Site 846.' if table=='IR11.T21' else dataset_index[table]['caption_text_layer']
        sha=hashlib.sha256((ir_primary/ref['pdf_path']).read_bytes()).hexdigest()
        source=dict(report='Initial Reports',published_title=caption,chapter=int(ref['chapter']),chapter_site=site,
          printed_caption_site=caption_site,attribution=scope_status,
          pdf_url=GLOBAL_SOURCE+ref['pdf_path'],pdf_page=pg,printed_page=printed,source_sha256=sha)
        if table=='IR11.T21':
            source['data_path']='ir/core/site846_prior/table-21.csv'
            source['pole_parameters']=[
                dict(age_range_Ma='0–12',pole_latitude_N=71.5,pole_longitude_W=86.8,angular_velocity_deg_Myr=-0.75),
                dict(age_range_Ma='12–17',pole_latitude_N=67.2,pole_longitude_W=102.2,angular_velocity_deg_Myr=-0.83)]
            source['pole_note_status']='published_below_body'
            arr=[(int(r['table_row']),r['age_ma'],r['latitude_deg_s'],r['longitude_deg_w'],None) for r in load(ROOT.parent/'site846_prior/table-21.csv')]
            latfield='latitude_S'
        else:
            source['data_path']='ir/core/edition2_print/data/print_rows.csv.gz'
            pole=poles[table];source['pole_note_status']=pole['note_position']
            source['pole_parameters']=[] if not pole['pole_latitude_N'] else [dict(
                age_range_Ma=pole['age_range_Ma'] or None,
                pole_latitude_N=float(pole['pole_latitude_N']),pole_longitude_W=float(pole['pole_longitude_W']),
                angular_velocity_deg_Myr=float(pole['angular_velocity_deg_Myr']))]
            arr=[]
            for row in typed[table]:
                v=json.loads(row['cell_readings_json']);latfield=next(k for k in v if k.startswith('latitude'))
                arr.append((int(row['print_row']),v['age_Ma'],v[latfield],v.get('longitude_W'),float(row['row_y_pt'])))
        source['printed_latitude_convention']=latfield
        source['printed_longitude_convention']='west_positive' if any(r[3] is not None for r in arr) else 'not_published'
        source['role']='published paleogeographic reconstruction'
        sources[table]=source
        geo_count=0
        for number,age,raw_lat,raw_lon,y in arr:
            lat=float(raw_lat)*(-1 if latfield=='latitude_S' else 1)
            lon=-float(raw_lon) if raw_lon is not None else None
            geo=lon is not None and scope_status=='chapter_and_caption_agree'
            geo_count+=int(geo)
            status='caption_site_conflict' if scope_status!='chapter_and_caption_agree' else 'longitude_not_published' if lon is None else 'ready'
            props=dict(kind='published_paleoposition',age_Ma=float(age),source_id=table,print_row=number,
                       site=site if scope_status=='chapter_and_caption_agree' else None,chapter_site=site,printed_caption_site=caption_site,
                       row_y_pt=y,latitude_print=raw_lat,longitude_print=raw_lon,
                       latitude_deg_n=lat,longitude_deg_e=lon,position_status=status,default_map_eligible=geo)
            features.append(feature(f'{table}.r{number}',[lon,lat] if geo else None,props))
        catalog.append(dict(source_id=table,chapter_site=site,printed_caption_site=caption_site,confirmed_site=site if scope_status=='chapter_and_caption_agree' else '',
                printed_title=caption,age_rows=len(arr),default_paleopoints=geo_count,published_latitude_convention=latfield,
                published_longitude_convention=source['printed_longitude_convention'],attribution=scope_status,
                pdf_page=pg,printed_page=printed,source_pdf=source['pdf_url'],source_sha256=sha))
    bundle=dict(type='FeatureCollection',name='Leg 138 published hole coordinates and paleogeographic positions',
      source_registry=sources,geographic_units='decimal degrees; Point coordinates are [longitude_east, latitude_north]',
      feature_kinds=['reported_hole_location','published_paleoposition'],features=features)
    hole=[f for f in features if f['properties']['kind']=='reported_hole_location']
    pale=[f for f in features if f['properties']['kind']=='published_paleoposition']
    assert len(hole)==42 and len({f['properties']['hole'] for f in hole})==42
    assert {f['properties']['site'] for f in hole}==set(range(844,855))
    assert len(pale)==149 and len({x['chapter_site'] for x in catalog})==11
    assert Counter(f['properties']['position_status'] for f in pale)=={'ready':104,'longitude_not_published':36,'caption_site_conflict':9}
    for f in features:
        props=f['properties']
        assert props['source_id'] in sources and -90<=props['latitude_deg_n']<=90
        if f['geometry'] is None:assert not props['default_map_eligible']
        else:assert f['geometry']['coordinates']==[props['longitude_deg_e'],props['latitude_deg_n']]
        if props.get('position_status')=='caption_site_conflict':
            assert props['site'] is None and props['chapter_site']==854 and props['printed_caption_site']==851
    dest=DATA/'leg138_geography.geojson'
    dest.write_text(json.dumps(bundle,ensure_ascii=False,separators=(',',':'))+'\n')
    save(DATA/'geography_sources.csv',catalog)
    print(f'{dest.name} | 42 holes, 149 age rows, 104 default paleopoints, 36 latitude only, 9 disputed rows | {dest.stat().st_size} bytes')

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('ir_primary',type=Path);a.add_argument('sppr_core',type=Path)
    args=a.parse_args();build(args.ir_primary,args.sppr_core)
