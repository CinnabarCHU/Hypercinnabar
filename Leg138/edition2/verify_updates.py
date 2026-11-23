"""Check rendered native/print fields, individual OCR decisions, SR identities, and Site 853's corrected plot."""
import argparse,csv,gzip,hashlib,json
from collections import Counter
from pathlib import Path
import fitz
from companions import read,digest
from structured_updates import STATUS

def verify(root,out):
    assets=read(out/'resources.csv');byrep={}
    for asset in assets:byrep.setdefault(asset['representation'],[]).append(asset)
    expected={'named_native':92,'print_cells':63,'print_cell_evidence':63,'sr_reviewer_print':7,'sr_object_register':47}
    for k,n in expected.items():assert len(byrep[k])==n,(k,len(byrep[k]))
    mapped={(r['doc_id'],r['source_page']):r for r in read(out/'pages.csv')}
    native_rows=0;flags=0;print_rows=0;cell_statuses=Counter();sr_rows=0;checks=0
    grouped={}
    for k in ('named_native','print_cells','sr_reviewer_print'):
        for a in byrep[k]:
            rr=read(out/a['file'])
            grouped.setdefault(a['doc_id'],[]).append(a)
            if k=='named_native':
                assert rr==read(root/a['source_path'])
                native_rows+=len(rr);flags+=sum(bool(r['verification_flags']) for r in rr)
                if a['item_id']=='IR18.T12':
                    ir59=next(r for r in rr if r['source_line']=='59')
                    assert ir59['Corg_MAR']=='0.14' and ir59['non_CaCO3_MAR']==''
            elif k=='print_cells':
                print_rows+=len(rr)
                cell_statuses.update(s for r in rr for key,s in r.items() if key.endswith('__status') and s)
            else:sr_rows+=len(rr)
    for d,doc_assets in grouped.items():
        with fitz.open(out/'pdf'/(d+'.pdf')) as pdf:
            for a in doc_assets:
                pg=mapped[(d,str(a['source_page']))];start=int(pg['edition_first'])-1;end=int(pg['edition_reading_last'])
                text_pages=[' '.join(pdf[n].get_text().split()) for n in range(start,end)]
                content=' '.join(t for t in text_pages if 'Structured evidence' in t)
                needle=a['item_id']+' · '+a['label']
                assert needle in content,(a['item_id'],'missing rendered table heading')
                if a['representation']=='print_cells':
                    assert 'Cell marks:' in content and a['label'] in content
                elif a['representation']=='named_native':
                    assert 'native named fields' in content
                elif a['representation']=='sr_reviewer_print':
                    assert 'print transcription' in content
                checks+=1
    evidence_slots=0;observed=Counter()
    for a in byrep['print_cell_evidence']:
        rs=read(out/a['file']);evidence_slots+=len(rs);observed.update(r['review_status'] for r in rs)
        assert all(r['pdf_page'] and r['cell_bbox_pt'] for r in rs)
    assert observed==cell_statuses and set(observed)==set(STATUS)
    decisions=[r for a in byrep['sr_object_register'] for r in read(out/a['file'])]
    assert len(decisions)==len({r['item_id'] for r in decisions})==812
    objstats=Counter(r['status'] for r in decisions)
    assert objstats=={'accepted':809,'rejected':3}
    region_rows=read(out/'source_regions.csv')
    opening={r['item_id'] for r in region_rows if r['region_role'].startswith('verified_object_heading_')}
    withdrawn={r['item_id'] for r in region_rows if r['region_role']=='withdrawn_running_text_reference'}
    assert opening=={r['item_id'] for r in decisions if r['status']=='accepted'}
    assert withdrawn=={r['item_id'] for r in decisions if r['status']=='rejected'} and not(opening&withdrawn)
    # The page graft in PR must match the current corrected module vector exactly.
    mod=root/'figures/core/vector/Site853_intervals.pdf'
    item=next(r for r in read(root/'figures/core/data/figure_index.csv') if r['site']=='853')
    src_page=str(item['pr_pdf_page'])
    art=next(a for a in assets if a['doc_id']=='PR' and a['source_page']==src_page and a['kind']=='figure')
    assert art['sha256']==digest(mod)==digest(out/art['file'])
    spg=mapped[('PR',src_page)]
    with fitz.open(mod) as source,fitz.open(out/'pdf/PR.pdf') as new:
        page_index=int(spg['edition_reading_last'])
        p1=source[0].get_pixmap(matrix=fitz.Matrix(.7,.7));p2=new[page_index].get_pixmap(matrix=fitz.Matrix(.7,.7))
        assert p1.digest==p2.digest
    svg=next(a for a in assets if a['doc_id']=='PR' and a['source_page']==src_page and a['kind']=='svg')
    assert svg['sha256']==digest(mod.with_suffix('.svg'))
    lineage=next(r for r in read(out/'rate_plot_lineage.csv') if r['site']=='853')
    assert lineage['figure_pdf_sha256']==art['sha256'] and lineage['figure_svg_sha256']==svg['sha256']
    assert lineage['matrix_sha256']==digest(out/lineage['matrix'])==digest(root/'figures/core/data/ir_mean_intervals.csv')
    assert lineage['renderer_sha256']==digest(out/lineage['renderer'])
    assert (native_rows,flags,print_rows,evidence_slots,sr_rows,checks)==(2726,116,1516,6273,70,162)
    return dict(named_native_tables=92,named_native_rows=native_rows,native_rows_with_flags=flags,
                ir_print_tables=63,ir_print_rows=print_rows,ir_cell_slots=evidence_slots,cell_statuses=dict(cell_statuses),
                provisional_ir_print_cells=sum(n for k,n in cell_statuses.items() if STATUS[k].startswith('?')),
                sr_new_print_tables=7,sr_new_print_rows=sr_rows,sr_accepted_objects=809,sr_withdrawn_running_references=3,
                new_tables_confirmed_in_chapter_pdfs=checks,corrected_site853_source_item=art['item_id'],corrected_site853_source_page=src_page,
                corrected_site853_pdf_sha256=art['sha256'],corrected_site853_svg_sha256=svg['sha256'],
                corrected_site853_vector_page_in_PR=page_index+1,corrected_site853_rate_matrix_sha256=lineage['matrix_sha256'])
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    results=verify(a.root,a.output);(a.output/'table_and_object_checks.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
