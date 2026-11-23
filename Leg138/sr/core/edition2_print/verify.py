"""Validate accepted objects, coordinates, counts, and the independent manual field tables."""
import argparse,csv,gzip,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
import fitz
from build import csvrows,writecsv
def main():
    p=argparse.ArgumentParser();p.add_argument('core',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    objects={r['item_id'] for r in csvrows(a.core/'edition2/data/objects.csv') if r['status']=='accepted' and r['kind']=='table'}
    coverage={r['item_id']:r for r in csvrows(a.out/'coverage.csv')};assert set(coverage)==objects and len(objects)==230
    segments={r['segment']:r for r in csvrows(a.out/'segments.csv')}
    sources={};pagebounds={}
    for r in segments.values():
        src=r['source'];path=a.core.parent/'primary'/src
        if src not in sources:
            doc=fitz.open(path);sources[src]=(len(doc),hashlib.sha256(path.read_bytes()).hexdigest());pagebounds[src]=[(page.rect.width,page.rect.height) for page in doc]
        pn=int(r['pdf_page']);W,H=pagebounds[src][pn-1]
        for k in ['caption_bbox_pt','body_bbox_pt','header_bbox_pt']:
            bb=json.loads(r[k])
            if bb:assert 0<=bb[0]<bb[2]<=W+1 and 0<=bb[1]<bb[3]<=H+1,(r['segment'],k,bb,W,H)
        assert int(r['body_cells'])>0,('No mapped body cells',r['segment'])
    cc=Counter();tokens=Counter();cspan=Counter();seen=set();origins=Counter();allc=0
    with gzip.open(a.out/'cells.jsonl.gz','rt') as inp:
        for line in inp:
            rr=json.loads(line);k=rr['segment'];r=segments[k]
            assert rr['item_id']==r['item_id'] and rr['pdf_page']==int(r['pdf_page'])
            uid=(k,rr['role'],rr['row'],rr['col']);assert uid not in seen;seen.add(uid);allc+=1
            b=rr['bbox'];W,H=pagebounds[r['source']][int(r['pdf_page'])-1];assert 0<=b[0]<b[2]<=W+1 and 0<=b[1]<b[3]<=H+1,(uid,b)
            assert rr['col_first']<=rr['col']<=rr['col_last']<=int(r['position_columns'])
            assert rr['text']==' '.join(v[0] for v in rr['tokens'])
            if rr['role']=='body':cc[k]+=1;tokens[k]+=len(rr['tokens'])
            if rr['col_last']>rr['col_first']:cspan[k]+=1
            origins[rr['token_basis']]+=1
    for k,v in segments.items():
        assert cc[k]==int(v['body_cells']) and tokens[k]==int(v['body_words']) and cspan[k]==int(v['cells_crossing_gutter'])
    cells_by_table=Counter()
    for k,r in segments.items():cells_by_table[r['item_id']]+=cc[k]
    assert all(cells_by_table[k]==int(r['body_cells']) for k,r in coverage.items())
    manual={};partial={}
    for file,expected in [('verified_c04_table2.csv',7),('verified_c21_table2.csv',37),('verified_c12_table14_p29_marks.csv',22)]:
        rows=csvrows(a.out/file);assert len(rows)==expected
        bucket=partial if 'marks' in file else manual
        bucket[file]=expected
    sources_rows=[dict(source=k,pdf_pages=v[0],sha256=v[1]) for k,v in sorted(sources.items())]
    writecsv(a.out/'pdf_sources.csv',sources_rows[0].keys(),sources_rows)
    prior=[r for r in coverage.values() if r['prior_dataset_ids']];new=[r for r in coverage.values() if not r['prior_dataset_ids']]
    report={'active_tables':len(coverage),'tables_with_prior_datasets':len(prior),'previously_unstructured_tables':len(new),'all_anchored_segments':len(segments),'identified_continuation_segments':sum(r['part']=='continued' for r in segments.values()),'segments_with_actual_body_cells':len(cc),'previously_unstructured_with_body_cells':sum(int(r['body_cells'])>0 for r in new),'addressed_body_cells':sum(cc.values()),'body_source_tokens':sum(tokens.values()),'physical_body_baselines':sum(int(r['physical_body_rows']) for r in segments.values()),'header_plus_body_cells':allc,'position_columns_spanned_by_glyph_extents':sum(cspan.values()),'source_pdfs':len(sources),'source_basis_counts_header_and_body':dict(origins),'segment_review':dict(Counter(r['review'] for r in segments.values())),'named_fully_read_datasets':manual,'named_partial_printed_mark_datasets':partial}
    if (a.out/'vertical_header_candidates.csv.gz').exists():
        with gzip.open(a.out/'vertical_header_candidates.csv.gz','rt') as inp:
            vh=list(csv.DictReader(inp))
        assert all(r['segment'] in segments for r in vh)
        report['vertical_header_candidate_readings']=len(vh)
        report['segments_with_vertical_readings']=len({r['segment'] for r in vh})
    for file,kind in [('grid_rulings.csv.gz','matrix_ruling_candidates'),('row_span_candidates.csv.gz','matrix_row_span_candidates')]:
        with gzip.open(a.out/file,'rt') as inp:
            located=list(csv.DictReader(inp))
        assert all(r['segment'] in segments for r in located)
        report[kind]=len(located)
    (a.out/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
