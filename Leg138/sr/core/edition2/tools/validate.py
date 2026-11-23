"""Check provenance, coverage, critical corrections, the additional print datasets and HTTP entry points."""
from pathlib import Path
from collections import Counter
from threading import Thread
from http.server import ThreadingHTTPServer
from urllib.request import urlopen
from urllib.error import HTTPError
from decimal import Decimal
import csv,gzip,hashlib,json
from api import Handler
E=Path(__file__).resolve().parents[1];C=E.parent;P=C.parent/'primary'
def tab(p):
    with p.open() as f:return list(csv.DictReader(f))
def run():
    old={x['item_id']:x for x in tab(C/'items.csv')};objects=tab(E/'data/objects.csv');keys={x['item_id']:x for x in objects};chapters=tab(C/'chapters.csv')
    assert len(keys)==len(objects) and set(old)<=set(keys)
    assert {int(r['chapter']) for r in objects}==set(range(1,48))
    source={r['source']:r for r in tab(C/'source_manifest.csv')}
    for f in {r['source'] for r in objects}:
        assert (P/f).is_file()
        assert hashlib.sha256((P/f).read_bytes()).hexdigest()==source[f]['sha256']
    for r in objects:
        assert (E/r['proof']).is_file() and int(r['pdf_page'])>0
        b=json.loads(r['source_bbox_pt']);assert len(b)==4 and b[2]>b[0] and b[3]>b[1]
    candidates=[r for r in objects if r['previous_status']=='pdf_caption_candidate']
    assert len(candidates)==721 and sum(r['status']=='rejected' for r in candidates)==3
    assert {r['item_id'] for r in candidates if r['status']=='rejected'}=={'SR.C13.FIGURE12A','SR.C17.FIGURE15A','SR.C47.TABLE1'}
    assert len({r['item_id'] for r in objects if r['change']=='added'})==21
    tables=tab(E/'data/print_datasets.csv');proofs={r['dataset_id']:r for r in tab(E/'data/print_proofs.csv')}
    for t in tables:
        assert t['item_id'] in keys and t['source']==keys[t['item_id']]['source'] and int(t['pdf_page'])==int(keys[t['item_id']]['pdf_page'])
        rr=tab(E/t['file']);assert len(rr)==int(t['records']) and all(int(r['table_row'])==i+1 for i,r in enumerate(rr))
        assert (E/proofs[t['dataset_id']]['witness_png']).exists()
    euler=tab(E/'print/SR.C01.TABLE1.csv');ss={i for r in euler for i in map(int,r['printed_site_group'].split('|'))};assert ss==set(range(844,855))|{84,495,503,677}
    stages=tab(E/'data/historical_rotation_stages.csv')
    assert len(stages)==30 and sum(v['part_of_leg138']=='1' for v in stages)==22
    assert all(-180<=float(v['pole_longitude_deg_E'])<0 and 0<float(v['pole_latitude_deg_N'])<=90 for v in stages)
    rows=[json.loads(l) for l in (E/'data/row_apparatus.jsonl').read_text().splitlines()]
    old_uncertain=tab(C/'unresolved_records.csv')
    assert {(x['dataset_id'],int(x['first_line']),int(x['last_line']),x['original_text']) for x in old_uncertain}=={(x['dataset_id'],x['source_first_line'],x['source_last_line'],x['original_text']) for x in rows}
    for x in rows:
        original=(P/x['source']).read_bytes().decode('latin1').splitlines()
        assert '\n'.join(original[x['source_first_line']-1:x['source_last_line']])==x['original_text']
    wk=tab(E/'data/witnesses.csv')
    for q in wk:
        b=gzip.decompress((E/q['compressed_file']).read_bytes());assert len(b)==int(q['original_bytes']) and hashlib.sha256(b).hexdigest()==q['original_sha256']
    cross=tab(E/'data/ch23_depth_crosschecks.csv');assert len(cross)==25
    status=Counter(x['comparison'] for x in cross)
    out=dict(original_object_ids=len(old),original_candidates_reviewed=len(candidates),original_candidates_verified=len(candidates)-3,
             selected_caption_or_supplement_proofs=len(objects),chapters_covered=len(chapters),original_chapter_leaves=sum(int(x['pdf_pages']) for x in chapters),
             distinct_chapter_authoritative_sources_checked=len({r['source'] for r in objects}),active_objects=sum(r['status']=='accepted' for r in objects),
             rejected_ids=sum(r['status']=='rejected' for r in objects),new_appendices=sum(r['change']=='added' for r in objects),
             opening_leaf_corrections=sum(r['change']=='opening_page_corrected' for r in objects),previous_chapter_page_sources=47,
             new_print_tables=len(tables),new_transcribed_rows=sum(int(x['records']) for x in tables),new_separate_repository_witnesses=len(wk),
             full_cd_exception_rows_reassessed=len(rows),two_fully_field_mapped_appendix_b_rows=2,ch23_field_aligned_rows_with_orphan_token=5,
             site677_partial_row=1,ch23_witness_pairs=dict(status),complete_caption_text_proofread=False,
             limitation='The scan audits confirm object identity and opening locator. Figure contents, continuation folios, full caption text and every visible mark on each leaf have not been exhaustively collated.')
    (E/'data/verification.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    with ThreadingHTTPServer(('127.0.0.1',0),Handler) as http:
        thread=Thread(target=http.serve_forever,daemon=True);thread.start()
        def get(path):
            with urlopen(f'http://127.0.0.1:{http.server_port}{path}') as res:return json.load(res)
        try:
            assert len(get('/objects?status=rejected'))==3
            assert get('/objects/SR.C17.APPENDIXF')['pdf_page']=='42'
            assert get('/coverage/36')['chapter']=='36'
            assert len(get('/print/SR.C03.TABLE6.PRINT.E2')['rows'])==21
            assert get('/row-apparatus/SR.C35.APPENDIXB?line=2065')[0]['proposed_field_values']['opal_pct']=='18.86'
            try:get('/objects/not-a-key')
            except HTTPError as err:assert err.code==404
            else:raise AssertionError('Unknown key must fail')
        finally:http.shutdown();thread.join()
    print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':run()
