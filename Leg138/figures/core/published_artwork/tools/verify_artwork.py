"""Check page accounting, native source geometry and exact ink-render alignment for all approved traces."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
import csv
import gc
import json
from pathlib import Path

import fitz

from export_artwork import BASE,box,digest_file,image_description,region,rows,sha,trace
from find_artwork import save


def checks(primary, data):
    items=rows(data/'artwork_pages.csv')
    registry=defaultdict(list);sources=defaultdict(list)
    for r in items:
        registry[r['item_id']].append(r);sources[r['source_path']].append(r)
        assert (r['body_evidence']=='page_only')==(not r['body_bbox_pt'])
        if r['trace_ok']=='1':
            assert r['body_evidence']=='visual_confirmed' and 'mask_caption_in_body' not in r['reason']
    assert len(items)==len({(r['item_id'],r['source_pdf_page']) for r in items})==1289
    summary=[]
    for key,rr in registry.items():
        confirmed=[r for r in rr if r['body_evidence']=='visual_confirmed']
        candidate=[r for r in rr if r['body_evidence']=='machine_candidate']
        status='complete_confirmed' if len(confirmed)==len(rr) else 'partial_confirmed' if confirmed else 'candidates_only' if candidate else 'source_pages_only'
        summary.append(dict(item_id=key,series=rr[0]['series'],doc_id=rr[0]['doc_id'],site=rr[0]['site'],
                            source_path=rr[0]['source_path'],source_url=rr[0]['source_url'],figure_status=status,
                            pdf_pages='|'.join(x['source_pdf_page'] for x in rr),
                            visual_confirmed_pages='|'.join(x['source_pdf_page'] for x in confirmed),
                            machine_proposed_pages='|'.join(x['source_pdf_page'] for x in candidate),
                            trace_approved_pages='|'.join(x['source_pdf_page'] for x in rr if x['trace_ok']=='1')))
    save(data/'artwork_figures.csv',summary)
    verified=[]
    for source,tasks in sources.items():
        path=primary/source
        assert digest_file(path)==tasks[0]['source_sha256'],source
        approved=[r for r in tasks if r['trace_ok']=='1']
        if not approved:continue
        with fitz.open(path) as doc:
            cache={};last_page=None
            for r in approved:
                n=int(r['source_pdf_page']);page=doc[n-1]
                if n!=last_page:cache.clear()
                mode,info=image_description(page)
                assert mode=='native_raster'
                crop,origin=region(doc,page,info,box(r['body_bbox_pt']),cache)
                svg,evidence=trace(crop)
                verified.append(dict(item_id=r['item_id'],source_pdf_page=n,decoded_crop_sha256=sha(crop.tobytes()),
                                     source_pixel_bbox=','.join(map(str,origin['source_pixel_bbox'])),**evidence))
                del crop,svg
                print(f"{r['item_id']}:{n} {evidence['pixel_width']}x{evidence['pixel_height']}, {evidence['mismatch_pixels']} mismatches",flush=True)
                last_page=n
        del cache
        fitz.TOOLS.store_shrink(100);gc.collect()
    save(data/'trace_checks.csv',verified)
    report=dict(figures=len(summary),figure_leaves=len(items),unique_source_leaves=len({(r['source_path'],r['source_pdf_page']) for r in items}),
                checked_source_pdfs=len(sources),figure_statuses=dict(Counter(r['figure_status'] for r in summary)),
                leaf_statuses=dict(Counter(r['body_evidence'] for r in items)),native_source_image_leaves=sum(r['source_image_mode']=='native_raster' for r in items),
                trace_approved_leaves=sum(r['trace_ok']=='1' for r in items),native_trace_renders_checked=len(verified),
                native_trace_render_mismatch_pixels=sum(r['mismatch_pixels'] for r in verified),embedded_caption_masks=sum('mask_caption_in_body' in r['reason'] for r in items))
    (data/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    p=ArgumentParser(description=__doc__);p.add_argument('primary',type=Path);p.add_argument('--data',type=Path,default=BASE/'data')
    a=p.parse_args();checks(a.primary,a.data)
