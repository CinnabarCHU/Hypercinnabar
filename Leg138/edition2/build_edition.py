"""Build all Leg 138 paired PDF/HTML readers, or selected documents, from a merged archive."""
import argparse,csv,gzip,html,io,json,os,shutil,sys
import filecmp
import tempfile
from uuid import uuid4
from contextlib import contextmanager
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import fitz
from companions import read,write,prepare,digest
from modern_pdf import Reader,merge
from page_text import runs,reflow
from revisions import readings, reader_blocks, styled_text, checked_lines, partially_collated, page_blocks
from structured_updates import value

E=html.escape
SERIES_ORDER={'SP':0,'PR':1,'IR':2,'SR':3}
TITLES={'IR.138ir':'Initial Reports · front matter and contents','IR.ir138_panels':'Initial Reports · advisory panels',
'IR.ir138_policy':'Initial Reports · sample-distribution policy','SR.138sr':'Scientific Results · front matter and contents',
'SR.138_corx':'Scientific Results · published corrections','SR.sr138_f21':'Scientific Results · separately distributed foldout',
'SR.138NDX':'Scientific Results · volume index'}
CSS="""*{box-sizing:border-box}body{margin:0;color:#233937;background:#f9faf5;font:16px/1.57 system-ui,sans-serif}main{max-width:990px;margin:auto;padding:28px 32px 80px}h1,h2,h3{font-family:Georgia,serif;line-height:1.24;color:#174e46}h1{font-size:clamp(32px,5vw,57px);margin:14px 0 10px}h2{font-size:30px;margin:18px 0 10px}h3{font-size:19px;margin:12px 0 8px}a{color:#206858;text-underline-offset:3px}p{margin:.46em 0}section{background:white;border-top:2px solid #92b2a3;padding:14px 21px 20px;margin:22px 0}small,.meta,figcaption{font:13px/1.45 system-ui,sans-serif;color:#506b63}.article p{font:18px/1.55 Georgia,serif;max-width:80ch}.article p.caption{font:14px/1.48 system-ui;color:#335b4d}.bar,summary{color:#296656;font-weight:600}.bar a{margin-right:15px}details{margin:8px 0}summary{cursor:pointer}table{width:100%;text-align:left;border-collapse:collapse;font-size:13px}tr{border-bottom:1px solid #d9e4da}td,th{padding:5px 7px;vertical-align:top}th{background:#eef3eb;position:sticky;top:0}.scroll{overflow:auto;max-height:450px}figure{margin:15px 0}figure img{max-width:100%;max-height:560px}iframe{width:100%;height:75vh;border:1px solid #a9b7ad}header{border-bottom:1px solid #a9b7ad;padding-bottom:14px}.folio{margin-bottom:12px}.list{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}code{font-size:12px;overflow-wrap:anywhere}@media(max-width:700px){main{padding:16px}section{padding:12px}.scroll{max-width:100%}}"""
CSS += '.script-pair{display:inline-grid;grid-template-columns:max-content;vertical-align:-.22em;line-height:.78;align-items:start;text-align:left}.script-pair>sup,.script-pair>sub{font-size:.68em;position:static;vertical-align:baseline;line-height:1;grid-column:1}.script-pair>sup{grid-row:1}.script-pair>sub{grid-row:2}'
CSS += '.table-scroll{overflow-x:auto}.collated-table{width:auto;max-width:100%;margin:.7em 0 1em;font-variant-numeric:tabular-nums}.collated-table caption{text-align:left;padding:0 0 .5em;font-weight:600;color:#335b4d}.collated-table th{position:static;text-align:center}.collated-table td,.collated-table th{white-space:nowrap}.collated-table td{text-align:center}.collated-table td:first-child,.collated-table th:first-child,.collated-table[data-columns="4"] :is(td,th):nth-child(2){text-align:left}.collated-table th[colspan]{border-bottom:1px solid #a2b5a9}'
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
def printed_table_rows(blocks):
    """Split addressed print readings into cells without discarding empty fields."""
    rows=[]
    alignments=blocks[0].get('column_alignments')
    for block in blocks:
        fields=block['text'].split('\t')
        # The printed 41 k.y. heading and its rule also span the Interval column.
        spans=(1,3,2,2) if block['id']=='SR.C15.p018.b005' else [1]*len(fields)
        if len(spans)!=len(fields):raise ValueError(block['id'])
        cells=[];offset=0
        for field,span in zip(fields,spans):
            end=offset+len(field)
            marks=[dict(style=x['style'],begin=max(offset,x['begin'])-offset,end=min(end,x['end'])-offset)
                   for x in block.get('inline_styles',[]) if max(offset,x['begin'])<min(end,x['end'])]
            cell=dict(id=block['id'],text=field,inline_styles=marks)
            cells.append(dict(text=field,span=span,pdf=styled_text(cell),html=styled_text(cell,html=True)))
            if alignments:
                cells[-1]['align']=alignments[len(cells)-1]
            offset=end+1
        rows.append((block['role']=='table_header',cells))
    if len({sum(cell['span'] for cell in row) for _,row in rows})!=1:
        raise ValueError('Inconsistent printed table column counts')
    return rows


def printed_table_html(caption,rows,labelled_by=None):
    columns=sum(cell['span'] for cell in rows[0][1])
    label=f' aria-labelledby="{E(labelled_by,quote=True)}"' if labelled_by else ''
    parts=[f'<div class="table-scroll"><table class="collated-table" data-columns="{columns}"{label}>']
    if caption:
        parts.extend(['<caption>',styled_text(caption,html=True),'</caption>'])
    parts.append('<thead>')
    header=True
    for is_header,cells in rows:
        if header and not is_header:
            parts.append('</thead><tbody>');header=False
        opening='th' if is_header else 'td'
        columns=[]
        for cell in cells:
            span=cell['span'];attrs=(f' colspan="{span}"' if span>1 else '')
            if is_header:attrs+=(' scope="colgroup"' if span>1 else ' scope="col"')
            if cell.get('align'):attrs+=f' style="text-align:{cell["align"]}"'
            columns.append(f'<{opening}{attrs}>{cell["html"]}</{opening}>')
        # Whitespace between cells also preserves the addressed tab-delimited reading.
        parts.append('<tr>'+'\t'.join(columns)+'</tr>')
    parts.append(('</thead>' if header else '</tbody>')+'</table></div>')
    return ''.join(parts)


def build_document(job):
    root,out,record,folios,assets,cards,fonts=job;docid=record['doc_id'];title=record['title'] or TITLES.get(docid,docid)
    source_path=root/record['local_source'];source=fitz.open(source_path)
    if len(source)!=int(record['pdf_pages']):raise ValueError(docid)
    proof=readings(root,docid);line_checks=checked_lines(root,docid);source_hash=digest(source_path)
    if any(k[1]<1 or k[1]>len(source) or v['witness_sha256']!=source_hash for k,v in proof.items()):
        raise ValueError(f'Witness differs from the collated source: {docid}')
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
            collated=proof.get((docid,src))
            field_checks=line_checks.get((docid,src),{})
            if field_checks:
                reading=partially_collated(packets,field_checks,source_hash)
                mode=f'{len(field_checks)} visually checked hole-header lines (operations, coordinates, depths and recovery). Other text uses the publisher OCR.'
            if collated:
                visible=page_blocks(collated,packets,field_checks)
                reading=reader_blocks({'blocks':visible})
                mode='Visually collated against the source scan. '+collated['review_scope']
            reader.header(src,folio,url)
            start=reader.num
            reader.paragraph('Collated site-card fields. The original page follows the reading text.' if iscard else (mode if collated or field_checks else NOTICE),'notice')
            if not reading:reader.paragraph(NOPROSE,'notice')
            chunks=[];j=0
            while j<len(reading):
                k,t=reading[j]
                captioned=collated and k=='caption' and j+1<len(visible) and visible[j+1]['role']=='table_header'
                if collated and (captioned or visible[j]['role']=='table_header'):
                    first=j+1 if captioned else j
                    end=first
                    while end<len(visible) and visible[end]['role'] in ('table_header','table_row'):end+=1
                    rows=printed_table_rows(visible[first:end])
                    caption=visible[j] if captioned else None
                    intro=visible[j-1]['id'] if j and visible[j-1].get('introduces_table') else None
                    reader.printed_table(styled_text(caption) if caption else None,rows,fonts)
                    chunks.append(printed_table_html(caption,rows,intro))
                    j=end
                    continue
                if collated and visible[j].get('inline_styles'):
                    reader.styled_paragraph(styled_text(visible[j]),k,fonts)
                else:reader.paragraph(t,k)
                tag='h3' if k=='heading' else 'p'
                content=styled_text(visible[j],html=True) if collated else E(t)
                anchor=f' id="{E(visible[j]["id"],quote=True)}"' if collated and visible[j].get('introduces_table') else ''
                chunks.append(f'<{tag} class="{k}"{anchor}>{content}</{tag}>')
                j+=1
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
            ledger.write(json.dumps(dict(doc_id=docid,source_page=src,status=mode,gutter_pt=r['assigned_gutter_pt'],packets=packets,**({'visual_collation':collated} if collated else {}),**({'line_collations':list(field_checks.values())} if field_checks else {})),ensure_ascii=False,separators=(',',':'))+'\n')
            pageindex.append(r)
    outpdf=out/'pdf'/(docid+'.pdf');merge(reader.finish(),source,outpdf,pageindex,out)
    hr=[header(title),'<header>'+link('../index.html','Leg 138 · catalogue')+'<h1>'+E(title)+'</h1><p>'+E(docid)+' · '+link('../pdf/'+docid+'.pdf','Paired PDF edition')+' · '+link(record['url'],'Publisher PDF')+' · '+link('../audit/'+docid+'.jsonl.gz','Positioned source text (JSONL.gz)')+'</p>'+note('Visual collations are marked on individual pages. Other reading pages use the publisher text layer.')+'</header>']
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

def build(a,root,out):
    datadir=root/'data' if (root/'data/documents.csv').exists() else root/'integration/core/data'
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

def check_destination(out):
    """Only replace a previous paired edition or an empty directory."""
    if out.is_symlink() or (out.exists() and not out.is_dir()):
        raise ValueError(f'Output must be a real directory: {out}')
    if not out.exists() or not any(out.iterdir()):
        return
    try:
        verification=json.loads((out/'verification.json').read_text(encoding='utf8'))
        documents=read(out/'documents.csv')
        if (verification['documents']==len(documents) and documents and
                {'doc_id','source_pdf_sha256','edition_pdf_sha256'}<=documents[0].keys() and
                all((out/k).is_dir() for k in ('pdf','html','audit','resources'))):
            return
    except (OSError,KeyError,ValueError):
        pass
    raise ValueError(f'Directory contains files outside a recognizable paired edition: {out}')


@contextmanager
def publish_lock(out):
    """Serialize the short recover/swap step across builders sharing one output."""
    name=out.parent/f'.{out.name}.edition.lock'
    with name.open('a+b') as lock:
        if os.name=='nt':
            import msvcrt
            if lock.tell()==0:
                lock.write(b'0');lock.flush()
            lock.seek(0)
            msvcrt.locking(lock.fileno(),msvcrt.LK_LOCK,1)
        else:
            import fcntl
            fcntl.flock(lock,fcntl.LOCK_EX)
        # Closing the descriptor releases either OS lock, including after a crash.
        yield


def same_files(previous,out):
    paths={p.relative_to(previous) for p in previous.rglob('*')}
    if paths!={p.relative_to(out) for p in out.rglob('*')}:
        return False
    for rel in paths:
        old,new=previous/rel,out/rel
        if old.is_symlink() or new.is_symlink():return False
        if old.is_dir() and new.is_dir():continue
        if not (old.is_file() and new.is_file() and filecmp.cmp(old,new,shallow=False)):
            return False
    return True


def recover_previous(out,previous):
    if not previous.exists():
        return
    check_destination(previous)
    if not out.exists():
        previous.rename(out)
    elif not any(previous.iterdir()):
        previous.rmdir()
    elif same_files(previous,out):
        # Once deletion starts this copy can no longer restore an edition.
        # Rename it first so a killed cleanup cannot block the next build.
        obsolete=out.with_name(f'.{out.name}.edition-discard-{uuid4().hex}')
        previous.rename(obsolete)
        try:
            shutil.rmtree(obsolete)
        except OSError as error:
            print(f'Edition published; identical old copy remains at {obsolete}: {error}',file=sys.stderr)
    else:
        backup=out.with_name(f'{out.name}.previous-{uuid4().hex}')
        previous.rename(backup)
        print(f'Previous edition and additional files retained at {backup}',flush=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('root',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--doc',action='append')
    ap.add_argument('--workers',type=int,default=3);ap.add_argument('--fonts',type=Path,default=Path('/usr/share/fonts/truetype/dejavu'))
    a=ap.parse_args();root=a.root.resolve()
    if a.output.is_symlink():
        raise ValueError(f'Output cannot be a symlink: {a.output}')
    out=a.output.resolve()
    if out==root or out in root.parents:
        raise ValueError('An edition output cannot contain its source directory')
    out.parent.mkdir(parents=True,exist_ok=True)
    previous=out.with_name(f'.{out.name}.edition-previous')
    with publish_lock(out):
        recover_previous(out,previous)
        check_destination(out)
    with tempfile.TemporaryDirectory(prefix=f'.{out.name}.building-',dir=out.parent) as work:
        staged=Path(work)/'edition'
        staged.mkdir()
        build(a,root,staged)
        with publish_lock(out):
            recover_previous(out,previous)
            check_destination(out)
            if out.exists():
                staged.chmod(out.stat().st_mode & 0o7777)
                out.rename(previous)
            try:
                staged.rename(out)
            except BaseException:
                recover_previous(out,previous)
                raise
            recover_previous(out,previous)


if __name__=='__main__':main()
