"""Build all Leg 138 paired PDF/HTML readers, or selected documents, from a merged archive."""
import argparse,csv,gzip,html,io,json,os,shutil,sys
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import fitz
from companions import read,write,prepare,digest
from modern_pdf import Reader,merge
from page_text import runs,reflow
from structured_updates import value

E=html.escape
SERIES_ORDER={'SP':0,'PR':1,'IR':2,'SR':3}
TITLES={'IR.138ir':'Initial Reports · front matter and contents','IR.ir138_panels':'Initial Reports · advisory panels',
'IR.ir138_policy':'Initial Reports · sample-distribution policy','SR.138sr':'Scientific Results · front matter and contents',
'SR.138_corx':'Scientific Results · published corrections','SR.sr138_f21':'Scientific Results · separately distributed foldout',
'SR.138NDX':'Scientific Results · volume index'}
CSS="""*{box-sizing:border-box}body{margin:0;color:#233937;background:#f9faf5;font:16px/1.57 system-ui,sans-serif}main{max-width:990px;margin:auto;padding:28px 32px 80px}h1,h2,h3{font-family:Georgia,serif;line-height:1.24;color:#174e46}h1{font-size:clamp(32px,5vw,57px);margin:14px 0 10px}h2{font-size:30px;margin:18px 0 10px}h3{font-size:19px;margin:12px 0 8px}a{color:#206858;text-underline-offset:3px}p{margin:.46em 0}section{background:white;border-top:2px solid #92b2a3;padding:14px 21px 20px;margin:22px 0}small,.meta,figcaption{font:13px/1.45 system-ui,sans-serif;color:#506b63}.article p{font:18px/1.55 Georgia,serif;max-width:80ch}.article p.caption{font:14px/1.48 system-ui;color:#335b4d}.bar,summary{color:#296656;font-weight:600}.bar a{margin-right:15px}details{margin:8px 0}summary{cursor:pointer}table{width:100%;text-align:left;border-collapse:collapse;font-size:13px}tr{border-bottom:1px solid #d9e4da}td,th{padding:5px 7px;vertical-align:top}th{background:#eef3eb;position:sticky;top:0}.scroll{overflow:auto;max-height:450px}figure{margin:15px 0}figure img{max-width:100%;max-height:560px}iframe{width:100%;height:75vh;border:1px solid #a9b7ad}header{border-bottom:1px solid #a9b7ad;padding-bottom:14px}.folio{margin-bottom:12px}.list{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}code{font-size:12px;overflow-wrap:anywhere}@media(max-width:700px){main{padding:16px}section{padding:12px}.scroll{max-width:100%}}"""
def link(url,label):return f'<a href="{E(str(url),quote=True)}">{E(str(label))}</a>'
def header(title):
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+E(title)+'</title><style>'+CSS+'</style><body><main>'
def note(x):return '<p class="meta">'+E(x)+'</p>'

NOTICE='Unproofed publisher text layer. Physical lines are grouped by source block, column and full-width bands. For figures, tables, type emphasis, formulae, symbols and photographs, use the original-page witness.'
NOPROSE='No narrative was confidently identified on this page. The original witness and the complete positioned text layer follow.'
SCRIPT="""<script>document.querySelectorAll('details.pageview').forEach(d=>d.addEventListener('toggle',()=>{const f=d.querySelector('iframe');if(d.open&&!f){const i=document.createElement('iframe');i.title='Original report page';i.src=d.dataset.url;d.append(i)}}))</script>"""
def card_content(r):
    keys=[('Priority','priority'),('Position','position_printed'),('Water depth','water_depth_printed'),('Seismic record','seismic_record'),('Primary site','primary_site'),('Crossing','crossing'),('Secondary site','secondary_site'),('Sediment record','sediment_record'),('Sediment thickness','sediment_thickness_printed'),('Proposed drilling program','proposed_drilling_program'),('Logging','logging'),('Objectives','objectives'),('Anticipated sediment/rocks','anticipated_sediment_rocks')]
    return [('heading',r['proposed_site'])]+[('body',title+'  ·  '+r[k]) for title,k in keys if r[k]]
def html_assets(resources,out):
    chunks=[]
    for a in resources:
        name=a['label'];rel='../'+a['file'];title=a['item_id']+' · '+name
        if a['kind']=='svg':
            chunks.append('<figure><img loading="lazy" alt="'+E(title)+'" src="'+E(rel)+'"><figcaption>'+link(rel,title)+'</figcaption></figure>');continue
        if a['kind'] in ('figure','card'):rel+='#page='+str(a['asset_page'])
        flag=' (chapter-level evidence)' if a['page_relation']=='chapter_entry_only' else ''
        if a['page_relation']=='narrative_reference_to_cd_rom':flag=' (chapter reference to CD-ROM)'
        chunks.append('<p class="meta">'+link(rel,title)+E(flag)+'</p>')
        if a['editorial_note']:chunks.append(note(a['editorial_note']))
        if a['kind']=='table':
            rows=read(out/a['file']);cols=a['display_columns'] or list(rows[0]);cols=[k for k in cols if k in rows[0]]
            chunks.append('<details><summary>Read '+str(len(rows))+' data rows</summary><div class="scroll"><table><thead><tr><th>Row</th>'+''.join('<th>'+E(k)+'</th>' for k in cols)+'</tr></thead><tbody>')
            for i,r in enumerate(rows,1):chunks.append('<tr><td>'+str(i)+'</td>'+''.join('<td>'+E(value(r,k))+'</td>' for k in cols)+'</tr>')
            chunks.append('</tbody></table></div></details>')
    return ''.join(chunks)
def build_document(job):
    root,out,record,folios,assets,cards,fonts=job;docid=record['doc_id'];title=record['title'] or TITLES.get(docid,docid)
    source_path=root/record['local_source'];source=fitz.open(source_path)
    if len(source)!=int(record['pdf_pages']):raise ValueError(docid)
    reader=Reader(docid,title,fonts);sections=[];pageindex=[]
    grouped=defaultdict(list)
    for a in assets:grouped[a['source_page']].append(a)
    outline=[]
    with (out/'audit'/f'{docid}.jsonl.gz').open('wb') as raw_ledger, \
            gzip.GzipFile(filename='',mode='wb',fileobj=raw_ledger,mtime=0) as gz_ledger, \
            io.TextIOWrapper(gz_ledger,encoding='utf-8') as ledger:
        for src,p in enumerate(source,1):
            seam,packets=runs(p);folio=folios.get(src);url=record['url']+'#page='+str(src)
            reading=[(pk['role'],reflow(pk)) for pk in packets if pk['role']!='positioned']
            iscard=(docid=='SP' and src in cards)
            if iscard:reading=card_content(cards[src])
            part=grouped[src];mode='collated prospectus site card' if iscard else 'publisher OCR; reading order inferred'
            reader.header(src,folio,url)
            start=reader.num
            reader.paragraph('Collated site-card fields. The original page follows the reading text.' if iscard else NOTICE,'notice')
            if not reading:reader.paragraph(NOPROSE,'notice')
            for k,t in reading:reader.paragraph(t,k)
            if part:
                reader.paragraph('Page-linked data and editorial comparisons','heading')
                for a in part:
                    relation=' | chapter-level location' if a['page_relation']=='chapter_entry_only' else ''
                    reader.paragraph(a['item_id']+' | '+a['label']+relation,'notice')
                for a in part:
                    if a['kind']=='table':
                        reader.end();reader.header(src,folio,url,'Structured evidence')
                        reader.table(a,read(out/a['file']))
            last=reader.num;reader.end()
            chunks=[]
            for k,t in reading:
                tag='h3' if k=='heading' else 'p';chunks.append(f'<{tag} class="{k}">{E(t)}</{tag}>')
            if not reading:chunks.append(note(NOPROSE))
            positioned=[(pk,ln) for pk in packets if pk['role']=='positioned' for ln in pk['lines']]
            if positioned:
                chunks.append('<details><summary>Other positioned source text ('+str(len(positioned))+' line segments)</summary><div class="scroll"><table><thead><tr><th>Block / line / segment</th><th>Source box (PDF pt)</th><th>Publisher OCR</th></tr></thead><tbody>')
                for pk,ln in positioned:
                    anchor=f"{ln['block']} / {ln['line']} / {ln['part']}"
                    chunks.append('<tr><td>'+anchor+'</td><td>'+', '.join(map(str,ln['bbox']))+'</td><td>'+E(ln['raw'])+'</td></tr>')
                chunks.append('</tbody></table></div></details>')
            sections.append((''.join(chunks),html_assets(part,out)))
            lines=sum(len(pk['lines']) for pk in packets)
            r=dict(doc_id=docid,source_page=src,printed_page=folio,reader_first=start,reader_last=last,
                   assigned_gutter_pt=round(seam,2) if seam else None,column_mode='two_column_bands' if seam else 'single_or_unresolved',
                   source_line_segments=lines,reading_packets=len(reading),positioned_packets=sum(pk['role']=='positioned' for pk in packets),
                   source_width_pt=p.rect.width,source_height_pt=p.rect.height,reading_text_status=mode,
                   graphics=[a for a in part if a['kind'] in ('figure','card')],pdf_table_assets=sum(a['kind']=='table' for a in part))
            ledger.write(json.dumps(dict(doc_id=docid,source_page=src,status=mode,gutter_pt=r['assigned_gutter_pt'],packets=packets),ensure_ascii=False,separators=(',',':'))+'\n')
            pageindex.append(r)
    outpdf=out/'pdf'/(docid+'.pdf');merge(reader.finish(),source,outpdf,pageindex,out)
    hr=[header(title),'<header>'+link('../index.html','Leg 138 · catalogue')+'<h1>'+E(title)+'</h1><p>'+E(docid)+' · '+link('../pdf/'+docid+'.pdf','Paired PDF edition')+' · '+link(record['url'],'Publisher PDF')+' · '+link('../audit/'+docid+'.jsonl.gz','Positioned source text (JSONL.gz)')+'</p>'+note(NOTICE)+'</header>']
    hr.append('<details><summary>Browse '+str(len(pageindex))+' source pages</summary><p>'+ ' · '.join(link('#p'+str(i),i) for i in range(1,len(pageindex)+1))+'</p></details>')
    target=fitz.open(outpdf)
    sample_pages={1,(len(source)+1)//2,len(source)}
    for r,(rd,companions) in zip(pageindex,sections):
        n=r['source_page'];ew=r['edition_witness'];desc='Source PDF page '+str(n)+(f" · printed {r['printed_page']}" if r['printed_page'] else '')
        r['graphics_count']=len(r.pop('graphics'))
        path='../pdf/'+docid+'.pdf#page='+str(ew)
        hr.extend(['<section id="p'+str(n)+'"><h2>'+desc+'</h2><p class="bar">'+link(path,'Original page in paired PDF')+link(record['url']+'#page='+str(n),'Publisher page')+link('../pdf/'+docid+'.pdf#page='+str(r['edition_first']),'Typeset PDF')+'</p>',note(r['reading_text_status']),
                   '<div class="article">'+rd+'</div>',companions,'<details class="pageview" data-url="'+E(path)+'"><summary>View the complete source-page layout</summary></details></section>'])
        # Compare the actual document rendering, including graphics and all labels, for every original page.
        src=source[n-1];wit=target[ew-1]
        if src.rect!=wit.rect:raise ValueError((docid,n,'witness geometry changed'))
        scale=.36
        img1=src.get_pixmap(matrix=fitz.Matrix(scale,scale),annots=False,colorspace=fitz.csRGB)
        img2=wit.get_pixmap(matrix=fitz.Matrix(scale,scale),annots=False,colorspace=fitz.csRGB)
        if img1.digest!=img2.digest:raise ValueError((docid,n,'witness rendering differs'))
        r['render_check_dpi']=round(scale*72,2);r['witness_render_md5']=img1.digest.hex()
        if not any(l.get('page')==ew-1 for l in target[r['edition_first']-1].get_links()):raise ValueError((docid,n,'missing witness link'))
        if n in sample_pages and not target[r['edition_first']-1].get_text().strip():raise ValueError((docid,n,'empty typeset page'))
    hr+=[SCRIPT,'</main></body></html>'];htmlfile=out/'html'/(docid+'.html');htmlfile.write_text(''.join(hr))
    summary=dict(doc_id=docid,series=record['series'],chapter=record['chapter'],title=title,source_pdf_pages=len(source),
                 edition_pdf_pages=len(target),typeset_pages=sum(r['reader_last']-r['reader_first']+1 for r in pageindex),
                 graphical_comparison_or_card_leaves=sum(r['graphics_count'] for r in pageindex),column_profile_pages=sum(bool(r['assigned_gutter_pt']) for r in pageindex),
                 witness_pages_checked=len(pageindex),source_pdf_sha256=digest(source_path),edition_pdf_sha256=digest(outpdf),
                 pdf='pdf/'+docid+'.pdf',html='html/'+docid+'.html',source_url=record['url'],source_local=record['local_source'])
    target.close();source.close()
    return summary,pageindex

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('root',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--doc',action='append')
    ap.add_argument('--workers',type=int,default=3);ap.add_argument('--fonts',type=Path,default=Path('/usr/share/fonts/truetype/dejavu'))
    a=ap.parse_args();root=a.root.resolve();out=a.output.resolve();datadir=root/'data' if (root/'data/documents.csv').exists() else root/'integration/core/data'
    docs=read(datadir/'documents.csv');selected={r['doc_id'] for r in docs} if not a.doc else set(a.doc)
    if selected-{r['doc_id'] for r in docs}:raise ValueError('Unknown document ID')
    for name in ('pdf','html','audit','resources'): (out/name).mkdir(parents=True,exist_ok=True)
    assets=prepare(root,out,selected);folios=defaultdict(dict)
    with gzip.open(datadir/'pages.jsonl.gz','rt') as f:
        for l in f:
            r=json.loads(l)
            if r['doc_id'] in selected:folios[r['doc_id']][r['pdf_page']]=r['printed_page']
    cards={int(r['pdf_page']):r for r in read(root/'sppr/core/data/sp_site_cards.csv')}
    jobs=[(root,out,d,folios[d['doc_id']],[r for r in assets if r['doc_id']==d['doc_id']],cards,a.fonts) for d in docs if d['doc_id'] in selected]
    records=[];page_rows=[]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        for doc,pages in pool.map(build_document,jobs):
            records.append(doc);page_rows+=pages;print(doc['doc_id'],doc['source_pdf_pages'],doc['edition_pdf_pages'],flush=True)
    write(out/'documents.csv',records);write(out/'pages.csv',page_rows)
    for asset in assets:asset['display_columns']='|'.join(asset['display_columns'])
    write(out/'resources.csv',assets)
    ix=[header('Leg 138 · 全卷逐页校读版'),'<header><small>OCEAN DRILLING PROGRAM · LEG 138</small><h1>全卷逐页校读版</h1><p>逐章阅读重排的英文正文、结构化资料与刊载原页。每一原页都有独立的来源页号、文字坐标与核对位置。</p>',note('原文一般采用出版方 OCR；栏序采用可复建的几何判断，科学公式、数字表、图件和照片请对看原版。航前站卡、精校数据表和实际重绘图各自标出。'),'<p>'+link('documents.csv','分册明细')+' · '+link('pages.csv','逐页定位与核验')+' · '+link('resources.csv','数据与图件来源')+'</p></header>']
    for series in sorted(SERIES_ORDER,key=SERIES_ORDER.get):
        rec=[r for r in records if r['series']==series]
        if not rec:continue
        ix+=['<section><h2>'+series+'</h2><table><thead><tr><th>文献</th><th>来源页</th><th>阅读／核对</th></tr></thead><tbody>']
        for r in rec:ix.append('<tr><td>'+E(r['doc_id'])+' · '+E(r['title'])+'</td><td>'+str(r['source_pdf_pages'])+'</td><td>'+link(r['html'],'HTML')+' · '+link(r['pdf'],'PDF')+'</td></tr>')
        ix+=['</tbody></table></section>']
    (out/'index.html').write_text(''.join(ix)+'</main></body></html>')
    audit=dict(documents=len(records),source_pages=len(page_rows),typeset_pages=sum(r['typeset_pages'] for r in records),
               paired_pdf_pages=sum(r['edition_pdf_pages'] for r in records),witness_pages_checked=len(page_rows),
               column_profile_pages=sum(r['column_profile_pages'] for r in records),cards_and_figure_comparisons=sum(r['graphical_comparison_or_card_leaves'] for r in records),
               source_line_segments=sum(r['source_line_segments'] for r in page_rows),resource_relations=len(assets),resource_kinds=dict(Counter(v['kind'] for v in assets)))
    (out/'verification.json').write_text(json.dumps(audit,indent=2)+'\n')
    from source_regions import add_regions
    add_regions(root,out)
    from plot_lineage import publish
    publish(root,out)
    from sr_annex import publish as add_sr_table_annex
    add_sr_table_annex(root,out,a.fonts)
    from composite_companion import add as add_composite
    composite=add_composite(root,out)
    if composite:(out/'composite_companion_checks.json').write_text(json.dumps(composite,indent=2)+'\n')

if __name__=='__main__':main()
