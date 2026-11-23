"""Verify all table defaults, surviving version-one queries, source paths, review records and HTTP exports."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer
from urllib.request import urlopen
import argparse,csv,gzip,io,json,sqlite3
from serve import Handler,endpoint

def read(path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt',newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def verify(root,allow_incomplete_sr=False):
    with sqlite3.connect((root/'Leg138.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        get=lambda endpoint_name,**q:endpoint(db,root,endpoint_name,{k:str(v) for k,v in q.items()})
        rows=get('ir-tables',limit=1000);assert len(rows)==259
        expected={r['item_id'] for r in read(root/'ir/core/table_coverage.csv')}
        assert {r['item_id'] for r in rows}==expected
        for r in rows:
            item=r['item_id'];first=get('rows',item=item,limit=1);last=get('item-rows',item=item,offset=r['named_rows']-1,limit=1)
            assert len(first)==len(last)==1 and first[0]['item_id']==item and first[0]['reading_status']
            assert last[0]['row_no']==r['named_rows'] and r['default_dataset'] in r['datasets']
            assert get('datasets',item=item,limit=1000)
        baseline=get('rows',dataset='IR11.T11.pilot',site='846',limit=1000);assert len(baseline)==62
        native=get('rows',dataset='IR06.T02.native.fields',limit=1)[0];assert 'site_846_sedimentation_rate' in native
        print_row=get('rows',dataset='IR02.T01.printcells.v2',limit=1)[0]
        assert 'sediment_class' in print_row['values'] and print_row['source_witness']['sha256']
        cells=get('print-cells',item='IR02.T01',row=1,limit=50);assert cells and all(r['review_status'] for r in cells)
        assert get('item-rows',item='IR06.T02',site=846,limit=1)
        assert len(get('sr-objects',limit=1000))==809 and len(get('sr-objects',status='rejected',limit=10))==3
        assert get('items',item='SR.C13.FIGURE12A')[0]['review_state']=='rejected'
        app=get('sr-apparatus',dataset='SR.C35.APPENDIXB',line=2065)[0]
        assert app['proposed_field_values']['opal_pct']=='18.86'
        old=get('rows',dataset='SR.C35.APPENDIXB',limit=1,offset=app['ordinal']-1)[0]
        assert old['values'] is None and old['editorial_review']['original_text']==app['original_text']
        assert get('sr-apparatus',site=677)[0]['dataset_id']=='SR.C15.TABLE9'
        assert len(get('rows',dataset='SR.C41.TABLE3.PRINT.E2',site=846))==1
        assert len(get('rotation-stages',site=846))==2 and len(get('rotation-stages',site=677))==2
        assert len(get('rotation-stages',limit=100))==30
        geo=get('geography',limit=1000)
        assert len(geo)==191 and sum(g['geometry'] is None for g in geo)==45
        assert len(get('geography',status='longitude_not_published',geometry='null',limit=1000))==36
        conflicts=get('geography',site=854,status='caption_site_conflict',geometry='null')
        assert len(conflicts)==9 and all(x['properties']['site'] is None for x in conflicts)
        lookup=get('geography',site=846,age=1,kind='published_paleoposition')
        assert lookup and all(r['properties']['age_Ma']==1 and r['properties']['site']==846 for r in lookup)
        sr_tables=get('sr-tables',limit=1000)
        if sr_tables or not allow_incomplete_sr:
            valid_tables={r['item_id'] for r in get('sr-objects',kind='table',limit=1000)}
            assert len(valid_tables)==230 and {r['item_id'] for r in sr_tables}==valid_tables
            assert sum(not bool(r['prior_dataset_ids']) for r in sr_tables)==177
            assert sum(int(r['segments']) for r in sr_tables)==306
            assert sum(int(r['body_cells']) for r in sr_tables)==88600
            assert len(get('rows',dataset='SR.C04.TABLE2.PRINT.RASTER_VERIFIED'))==7
            assert len(get('rows',dataset='SR.C21.TABLE2.PRINT.RASTER_VERIFIED'))==37
            assert len(get('rows',dataset='SR.C12.TABLE14.PRINT.PAGE29.MARKS'))==22
            for r in sr_tables:
                n=int(r['body_cells'])
                sq='SELECT COUNT(*) FROM sr_print_slots c JOIN sr_segments s USING(segment) WHERE s.item_id=? AND c.role=?'
                assert db.execute(sq,(r['item_id'],'body')).fetchone()[0]==n
                if n:
                    probed=get('sr-table-rows',item=r['item_id'],limit=1)
                    assert probed and probed[0]['cells'] and probed[0]['segment_review']
                    token=get('sr-table-cells',item=r['item_id'],limit=1)[0]
                    assert token['bbox'] and 'tokens' in token and 'header_candidate' in token and token['source_sha256']
                    assert get('rows',dataset=r['item_id']+'.PRINT.SLOTS.E2',limit=1)[0]['item_id']==r['item_id']
        rois=get('roi',site=844,core='844A1H',role='printed_ruler');assert len(rois)==1 and rois[0]['jpeg_sha256']
        assert get('rows',dataset='CD.E2.WATER',site=848,limit=1)[0]['directory_site']=='848'
        assert 'blue_pct' in get('rows',dataset='CD.E2.BINARY_COLOR844',site=844,limit=1)[0]
        assert get('rows',dataset='CD.E2.LOG.844.ACT_GST',site=844,limit=1)
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and not list(db.execute('PRAGMA foreign_key_check'))
        assert not list(db.execute('SELECT m.item_id FROM dataset_items m LEFT JOIN items i USING(item_id) WHERE i.item_id IS NULL'))
        totals={t:db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ['ir_table_review','ir_named','ir_print_cells','item_reviews','sr_apparatus','optical_roi','datasets','sr_print_review','sr_segments','sr_slot_fields','sr_print_slots','sr_slot_rows']}
    class Quiet(Handler):
        def log_message(self,*args):pass
    with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root))) as server:
        t=Thread(target=server.serve_forever,daemon=True);t.start()
        try:
            def remote(path):
                with urlopen(f'http://127.0.0.1:{server.server_port}/api/'+path) as stream:return stream.read().decode()
            assert json.loads(remote('ir-tables?item=IR02.T01'))['records'][0]['named_rows']==34
            assert len(json.loads(remote('sr-objects?status=rejected'))['records'])==3
            csv_row=next(csv.DictReader(io.StringIO(remote('item-rows?item=IR02.T01&limit=1&format=csv'))))
            assert csv_row['sediment_class'] and csv_row['reading_status']
            assert json.loads(remote('roi?core=844A1H&role=printed_ruler'))['count']==1
            geographically=json.loads(remote('geography?site=854&age=1&status=caption_site_conflict'))
            assert geographically['type']=='FeatureCollection' and geographically['features'][0]['geometry'] is None
            assert 'source_registry' in geographically
        finally:server.shutdown();t.join()
    return dict(checks='passed',table_counts=totals,ir_tables_with_named_rows_and_review_states=259,sr_accepted=809,sr_rejected_kept=3,rotation_stages=30,reported_geographical_features=191,missing_longitude_nulls=36,conflicting_caption_nulls=9,sr_effective_print_tables_indexed=len(sr_tables),sr_physical_print_body_cells=sum(int(r['body_cells']) for r in sr_tables),sr_position_candidates_separate_from_named_verified_scientific_rows=True,read_only_http_and_csv_verified=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--write',type=Path);p.add_argument('--allow-incomplete-sr',action='store_true',help='Only for testing before the SR print-slot package is present');a=p.parse_args()
    output=json.dumps(verify(a.root.resolve(),a.allow_incomplete_sr),ensure_ascii=False,indent=2)
    if a.write:a.write.write_text(output+'\n')
    print(output)
