"""Publish actual source-caption blocks, documented PR plot bounds and full-page anchors."""
import argparse,html,json,re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote
import fitz
from companions import read,write
E=html.escape
def add_regions(root,out):
    docs={r['doc_id']:r for r in read(out/'documents.csv')};page_index={(r['doc_id'],int(r['source_page'])):int(r['edition_witness']) for r in read(out/'pages.csv')}
    target=out/'regions';pic=target/'crops';pic.mkdir(parents=True,exist_ok=True)
    rows=[]
    def add(doc,item,p,role,box,desc,url=None):
        if doc not in docs:return
        rows.append(dict(doc_id=doc,item_id=item,pdf_page=int(p) if p else '',region_role=role,
                         source_box_pt=','.join(f'{x:.2f}' for x in box) if box else '',
                         source_label=desc,source_url=url or (docs[doc]['source_url']+('#page='+str(p) if p else '')),
                         paired_witness_page=page_index.get((doc,int(p)), '') if p else '',preview_file=''))
    ir=root/'ir/core'
    for r in read(ir/'chapter_item_locations.csv'):
        ident=r['item_id'];d='IR.C'+ident[2:4];box=[float(x) for x in r['caption_bbox_xyxy_pt'].split(',')] if r['caption_bbox_xyxy_pt'] else []
        if d not in docs:continue
        if r['pdf_path'] and docs[d]['source_local'].endswith(r['pdf_path']):
            add(d,ident,r['pdf_page'],r['anchor_kind'],box,r['source_caption_head'])
        elif r['pdf_path']:
            add(d,ident,None,'external_foldout_container',[],r['source_caption_head'],'https://www-odp.tamu.edu/publications/138_IR/'+r['pdf_path'])
    source_docs={v['source_local'].split('/',2)[-1]:k for k,v in docs.items() if v['series']=='SR'}
    decisions=read(root/'sr/core/edition2/data/objects.csv')
    sr_decisions={r['item_id']:r for r in decisions}
    for r in decisions:
        d=source_docs.get(r['source']);bbox=json.loads(r['source_bbox_pt']) if r['source_bbox_pt'] else []
        role=('verified_object_heading_'+r['layout_basis']) if r['status']=='accepted' else 'withdrawn_running_text_reference'
        if d:add(d,r['item_id'],r['pdf_page'],role,bbox,' · '.join(filter(None,(r['caption_or_heading_first_line'],r['editorial_note']))))
    for r in read(root/'sr/core/caption_anchors.csv'):
        prior=sr_decisions.get(r['item_id']);d=source_docs.get(r['source'])
        if not d or not prior or prior['status']!='accepted' or (r['pdf_page']==prior['pdf_page'] and r['source']==prior['source']):continue
        role='superseded_opening_location' if r['pdf_page']==prior['previous_pdf_page'] else 'historical_additional_ocr_locator'
        add(d,r['item_id'],r['pdf_page'],role,json.loads(r['bbox_pt']) if r['bbox_pt'] else [],r['caption_text'])
    for r in read(root/'ir/core/edition2_print/data/regions.csv'):
        add('IR.C'+r['item_id'][2:4],r['item_id'],r['pdf_page'],'documented_print_table_body',
            [float(v) for v in r['body_bbox'].split(',')],r['caption_text_layer'])
    print_meta={r['dataset_id']:r for r in read(root/'sr/core/edition2/data/print_datasets.csv')}
    for r in read(root/'sr/core/edition2/data/print_proofs.csv'):
        meta=print_meta[r['dataset_id']];d=source_docs.get(r['source'])
        if d:add(d,meta['item_id'],r['pdf_page'],'collated_print_table_window',json.loads(r['bbox_pt']),meta['editorial_note'])
    for r in read(root/'sppr/core/data/report_items.csv'):
        if r['kind'] in ('figure','table','chart','map','seismic image','site sheet'):
            for p in range(int(r['pdf_first']),int(r['pdf_last'])+1):
                add(r['doc_id'],r['item_id'],p,'indexed_source_page',[],r['title'])
    for r in read(root/'figures/core/data/figure_index.csv'):
        add('PR','PR.F'+r['pr_figure'],r['pr_pdf_page'],'collated_figure_window',
            [float(r['source_crop_'+v]) for v in ('left','top','right','bottom')],'Rate panels and caption · Site '+r['site'])
    for r in read(root/'figures/core/data/pr_panel_axes.csv'):
        add('PR','PR.F'+r['pr_figure'],r['pr_pdf_page'],'calibrated_panel_axes',
            [float(r[v+'_pt']) for v in ('left','top','right','bottom')],r['quantity']+' · '+r['unit'])
    groups=defaultdict(list)
    for i,r in enumerate(rows,1):groups[r['doc_id']].append((i,r))
    for d,items in groups.items():
        source=fitz.open(root/docs[d]['source_local']);pieces=[]
        for i,r in sorted(items,key=lambda v:(int(v[1]['pdf_page'] or 0),v[0])):
            if r['pdf_page'] and r['source_box_pt']:
                p=source[r['pdf_page']-1];rect=fitz.Rect([float(v) for v in r['source_box_pt'].split(',')]) & p.rect
                if not rect.is_empty:
                    file=f'regions/crops/{d}-{i:04d}.png'
                    p.get_pixmap(clip=rect,matrix=fitz.Matrix(1.4,1.4),annots=False).save(out/file)
                    r['preview_file']=file
            pg=r['pdf_page'];wit=r['paired_witness_page'];desc=E(r['source_label'])
            pieces.append((pg,'<article><h3>'+E(r['item_id'])+'</h3><p>'+E(r['region_role'])+' · '+(f'<a href="../pdf/{d}.pdf#page={wit}">full witness</a> · ' if wit else '')+f'<a href="{E(r["source_url"])}">publisher source</a></p>'+
                (f'<img loading="lazy" src="{E(r["preview_file"].replace("regions/","",1))}" alt="{E(r["item_id"])} source crop"><p>Source rectangle (PDF pt): '+r['source_box_pt']+'</p>' if r['preview_file'] else '')+
                (f'<details><summary>Index text</summary><p>{desc}</p></details>' if desc else '')+'</article>'))
        source.close()
        text=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(d)+' · source regions</title><style>body{font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:26px auto;padding:0 18px;color:#253b39}a{color:#186453}h1,h2,h3{font-family:Georgia,serif}article{border-top:1px solid #cbd9cd;padding:10px 0}img{display:block;max-width:100%;border:1px solid #e6eae5}article p{font-size:12px;color:#516a60}</style><a href="../html/'+d+'.html">Chapter reader</a><h1>'+E(d)+' · source regions</h1><p>Caption-block crops retain the bounds of the source index, which may include neighbouring text. Calibrated plot windows are identified separately. Page-only records retain the full witness.</p>']
        previous=None
        for pg,part in pieces:
            if pg!=previous:text.append(f'<h2 id="p{pg or 0}">Source PDF {pg or "external container"}</h2>');previous=pg
            text.append(part)
        (target/(d+'.html')).write_text(''.join(text)+'</html>')
        chapter=out/'html'/(d+'.html');txt=chapter.read_text()
        insert='<p class="meta"><a href="../regions/'+d+'.html">Browse original caption, figure and table locations</a></p>'
        if insert not in txt:txt=txt.replace('</header>',insert+'</header>',1)
        for pg in {x[0] for x in pieces if x[0]}:
            marker=f'<section id="p{pg}">'
            label=f'<p class="meta"><a href="../regions/{d}.html#p{pg}">Source item locations on this page</a></p>'
            if label not in txt:txt=txt.replace(marker,marker+label,1)
        chapter.write_text(txt)
    write(out/'source_regions.csv',rows)
    index=out/'index.html';txt=index.read_text();label='<p><a href="source_regions.csv">图表及图注的来源区域 CSV</a></p>'
    if label not in txt:index.write_text(txt.replace('</header>',label+'</header>',1))
    info=dict(item_location_records=len(rows),crop_pngs=sum(bool(r['preview_file']) for r in rows),
              calibrated_panel_windows=sum(r['region_role']=='calibrated_panel_axes' for r in rows),
              collated_figure_windows=sum(r['region_role']=='collated_figure_window' for r in rows),
              print_table_window_crops=sum(bool(r['preview_file']) and r['region_role'] in ('documented_print_table_body','collated_print_table_window') for r in rows),
              heading_and_other_locator_crops=sum(bool(r['preview_file']) and r['region_role'] not in ('calibrated_panel_axes','collated_figure_window','documented_print_table_body','collated_print_table_window') for r in rows),
              sr_authoritative_opening_locations=sum(r['region_role'].startswith('verified_object_heading_') for r in rows),
              sr_rejected_running_references=sum(r['region_role']=='withdrawn_running_text_reference' for r in rows))
    (out/'region_checks.json').write_text(json.dumps(info,indent=2)+'\n')
    return info
if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('root',type=Path);a.add_argument('output',type=Path)
    args=a.parse_args();print(json.dumps(add_regions(args.root,args.output),indent=2))
