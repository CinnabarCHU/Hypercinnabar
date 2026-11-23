"""Verify all SR appendix items, candidate tokens, eligibility rules, chapter leaves, and local links."""
from collections import defaultdict,Counter
from pathlib import Path
from urllib.parse import unquote,urlsplit
import argparse,csv,gzip,json
import fitz
from companions import read,digest
from verify_edition import Links

def verify(root,out):
    src=root/'sr/core/edition2_print';tables=read(out/'sr_table_catalog.csv');segments=read(out/'sr_table_annex.csv')
    coverage={r['item_id']:r for r in read(src/'coverage.csv') if r['new_geometry_priority']=='previously_unstructured'}
    assert len(coverage)==len(tables)==177 and set(coverage)=={r['item_id'] for r in tables}
    native=defaultdict(list)
    with gzip.open(src/'cells.jsonl.gz','rt') as inp:
        for line in inp:
            r=json.loads(line)
            if r['item_id'] in coverage:native[r['item_id']].append(r)
    official_segments={r['segment']:r for r in read(src/'segments.csv') if r['item_id'] in coverage}
    observed={r['segment']:r for r in segments};assert set(official_segments)==set(observed)
    bounds=read(out/'pages.csv');source_map={(r['doc_id'],int(r['source_page'])):r for r in bounds}
    docs={r['doc_id']:r for r in read(out/'documents.csv')}
    body=header=links=verified=crops=0;ck={};sources={}
    for r in tables:
        item=r['item_id']
        with gzip.open(out/r['positioned_cells'],'rt') as f:raw=list(map(json.loads,f))
        assert raw==native[item],item
        for cell in raw:
            assert len(cell['bbox'])==4 and all(len(token)==5 for token in cell['tokens']),item
            if cell['role']=='body':body+=1
            else:header+=1
        file=out/r['html'];parser=Links();parser.feed(file.read_text())
        for link in parser.paths:
            pp=unquote(urlsplit(link).path);assert not pp or (file.parent/pp).is_file(),(item,link);links+=1
    for seg,rec in observed.items():
        upstream=official_segments[seg];doc=rec['doc_id'];pg=int(rec['source_pdf_page']);ref=source_map[(doc,pg)]
        assert rec['geometry_review']==upstream['review'] and rec['geometry_status']==upstream['status']
        assert rec['body_box_pt']==upstream['body_bbox_pt'] and rec['source_witness_page']==ref['edition_witness']
        assert int(rec['candidate_cell_slots'])==int(upstream['body_cells'])
        if rec['checked_source_crop']:
            assert upstream['review']=='sample_geometry_checked'
            path=root/'sr/primary'/upstream['source']
            if path not in sources:sources[path]=fitz.open(path)
            p=sources[path][pg-1];rect=fitz.Rect(json.loads(upstream['body_bbox_pt'])) & p.rect
            expected=p.get_pixmap(clip=rect,matrix=fitz.Matrix(1.5,1.5),annots=False)
            written=fitz.Pixmap(str(out/rec['checked_source_crop']))
            assert written.width==expected.width and written.height==expected.height and written.samples==expected.samples,(seg,'crop')
            crops+=1
        named=int(rec['named_rows']);eligible=(named>0 or int(rec['unassigned_marks'])>0 or (upstream['review']=='sample_geometry_checked' and bool(json.loads(upstream['body_bbox_pt'])) and int(upstream['physical_body_rows'])>0))
        assert bool(rec['pdf_appendix_first'])==eligible,(seg,named,upstream['review'])
        if eligible:
            if doc not in ck:ck[doc]=fitz.open(out/docs[doc]['pdf'])
            pdf=ck[doc];start=int(rec['pdf_appendix_first']);last=int(rec['pdf_appendix_last']);assert last<=len(pdf)
            words=' '.join(' '.join(pdf[i-1].get_text().split()) for i in range(start,last+1))
            assert rec['item_id'] in words
            if named:assert 'visually read and field-mapped' in words
            if int(rec['unassigned_marks']):assert 'visible marks, sample identity unresolved' in words
            if upstream['review']=='sample_geometry_checked':assert 'unproofed OCR' in words
            for idx in range(start-1,last):assert any(x.get('page')==int(rec['source_witness_page'])-1 for x in pdf[idx].get_links())
            verified+=1
    for p in [*ck.values(),*sources.values()]:p.close()
    assert body==sum(int(r['body_cells']) for r in tables)
    st=json.loads((out/'sr_table_annex_checks.json').read_text())
    for file,sha in st['input_digests'].items():assert digest(src/file)==sha,file
    return dict(annex_tables_checked=len(tables),all_source_segments_checked=len(segments),body_cell_records_identical_to_source=body,header_cell_records_identical_to_source=header,
                chapter_supplements_checked=verified,verified_original_segment_crops=crops,annex_local_links_checked=links,named_print_rows_verified=sum(int(r['named_rows']) for r in segments),unassigned_marks_verified=sum(int(r['unassigned_marks']) for r in segments),input_hashes_verified=len(st['input_digests']))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=verify(a.root,a.output);(a.output/'sr_table_annex_verified.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
