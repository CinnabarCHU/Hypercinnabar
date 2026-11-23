"""Publish stand-off SR table evidence and append only reviewed table bodies to their chapters."""
import argparse,csv,gzip,html,io,json,re,shutil
from collections import Counter,defaultdict
from pathlib import Path
import fitz
from companions import read,write,digest
from modern_pdf import Reader,W,H
from build_edition import header,link,note
E=html.escape

def compress_records(path,records):
    with path.open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz,io.TextIOWrapper(gz,encoding='utf-8') as stream:
        for r in records:stream.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')

def coordinates(records,count):
    body=defaultdict(list)
    for c in records:
        if c['role']=='body':body[c['row']].append(c)
    cols=['row']+[f'P{x:02}' for x in range(1,count+1)]
    if any(c['col_first']!=c['col_last'] for ls in body.values() for c in ls):cols.append('spanning')
    out=[]
    for ix,ls in sorted(body.items()):
        parts=defaultdict(list)
        for c in ls:
            key=f"P{c['col']:02}" if c['col_first']==c['col_last'] else 'spanning'
            parts[key].append(c['text'] if key!='spanning' else f"P{c['col_first']:02}–P{c['col_last']:02}: {c['text']}")
        row={key:(' | '.join(parts[key]) if key!='row' else str(ix)) for key in cols}
        out.append(row)
    return cols,out

def grid(cols,rows):
    return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+E(k)+'</th>' for k in cols)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(str(r.get(k,'')))+'</td>' for k in cols)+'</tr>' for r in rows)+'</tbody></table></div>'

def publish(root,out,fonts):
    package=root/'sr/core/edition2_print';deps=[package/n for n in ('coverage.csv','segments.csv','cells.jsonl.gz','field_dictionary.csv.gz')]
    for p in deps:
        if not p.is_file():raise FileNotFoundError(p)
    coverage=read(deps[0]);docs={r['doc_id']:r for r in read(out/'documents.csv')}
    selected={r['item_id']:r for r in coverage if r['new_geometry_priority']=='previously_unstructured' and 'SR.C'+r['chapter'].zfill(2) in docs}
    if not selected:return
    if (out/'sr_table_annex.csv').exists():raise ValueError('SR annex already applied; build a clean edition or a copy of its pre-annex release')
    summaries={};byseg=defaultdict(list);byitem=defaultdict(list)
    for r in read(deps[1]):
        if r['item_id'] in selected:byitem[r['item_id']].append(r);summaries[r['segment']]=r
    with gzip.open(deps[2],'rt') as inp:
        for line in inp:
            r=json.loads(line)
            if r['item_id'] in selected:byseg[r['segment']].append(r)
    fields=defaultdict(list)
    with gzip.open(deps[3],'rt') as inp:
        for r in csv.DictReader(inp):
            if r['item_id'] in selected:fields[r['segment']].append(r)
    vertical=defaultdict(list);vsource=package/'vertical_header_candidates.csv.gz'
    if vsource.is_file():
        with gzip.open(vsource,'rt') as inp:
            for r in csv.DictReader(inp):
                if r['item_id'] in selected:vertical[r['segment']].append(r)
    curated=defaultdict(list)
    for f in sorted(package.glob('verified_*.csv')):
        rows=read(f)
        if not rows or 'item_id' not in rows[0] or 'pdf_page' not in rows[0]:continue
        groups=defaultdict(list)
        for row in rows:
            if row['item_id'] in selected:groups[(row['item_id'],int(row['pdf_page']))].append(row)
        for key,rs in groups.items():curated[key].append((f,rs))
    dst=out/'sr_tables';dst.mkdir(exist_ok=True)
    links=defaultdict(lambda:defaultdict(list));footlinks=defaultdict(dict);doc_pdf=defaultdict(list)
    pages={(r['doc_id'],int(r['source_page'])):r for r in read(out/'pages.csv')}
    outputs=[];catalog=[];source_docs={}
    for item in sorted(selected,key=lambda s:(int(selected[s]['chapter']),int(selected[s]['start_pdf_page']),int(re.search(r'TABLE(\d+)',s)[1]),s)):
        table=selected[item];doc='SR.C'+table['chapter'].zfill(2)
        leaf=dst/(item+'.html');raw_file=dst/(item+'.jsonl.gz')
        all_cells=[c for seg in byitem[item] for c in byseg[seg['segment']]]
        compress_records(raw_file,all_cells)
        itemfields=[f for seg in byitem[item] for f in fields[seg['segment']]]
        dictfile=dst/(item+'_columns.csv')
        if itemfields:write(dictfile,itemfields)
        vfile=dst/(item+'_vertical_readings.csv');vertical_terms=[v for seg in byitem[item] for v in vertical[seg['segment']]]
        if vertical_terms:write(vfile,vertical_terms)
        text=[header(item+' · SR table source evidence'),'<header>'+link('../html/'+doc+'.html','Chapter reader')+' · '+link('../index.html','Leg 138 catalogue')+'<h1>'+E(item)+'</h1><p>'+E(table['caption'])+'</p>',
              note('Unproofed positional OCR is indexed separately from visually field-mapped readings. P01, P02, etc. identify positions in an individual page segment. The readings, column intervals and orientation may change across a continuation. A gap in this display has no scientific zero or absence interpretation.'),
              '<p>'+link(raw_file.name,'Source token records with page boxes (JSONL.gz)')+(' · '+link(dictfile.name,'Positional header candidates (CSV)') if itemfields else '')+(' · '+link(vfile.name,'Independent vertical header candidates (CSV)') if vertical_terms else '')+'</p></header>']
        seen_named=set()
        for seg in byitem[item]:
            key=seg['segment'];pg=int(seg['pdf_page']);base=pages[(doc,pg)];w=int(base['edition_witness'])
            physical=byseg[key];cols,rows=coordinates(physical,int(seg['position_columns']))
            bodybox=json.loads(seg['body_bbox_pt']);pagebox=fitz.Rect(0,0,float(base['source_width_pt']),float(base['source_height_pt']))
            outside=bool(bodybox) and (fitz.Rect(bodybox)&pagebox).is_empty
            pdf_ok=(not outside and seg['review']=='sample_geometry_checked' and bool(json.loads(seg['body_bbox_pt'])) and rows)
            named=curated[(item,pg)] if (item,pg) not in seen_named else [];seen_named.add((item,pg))
            marked=[(f,rs) for f,rs in named if 'sample_assignment' in rs[0]]
            fully_named=[(f,rs) for f,rs in named if 'sample_assignment' not in rs[0]]
            flag='visually_mapped_named_rows' if fully_named else 'visible_marks_without_sample_assignment' if marked else ('reviewed_geometry_with_candidate_readings' if pdf_ok else ('raster_body_only' if seg['status']=='raster_body_only' else ('unlocated_body' if not json.loads(seg['body_bbox_pt']) else 'unverified_positional_ocr')))
            if not named and seg['review']=='matrix_region_checked_column_headings_need_review':flag='checked_matrix_geometry_unresolved_column_meaning'
            if not named and seg['review']=='formula_layout_checked_semantics_pending':flag='checked_formula_layout_unresolved_semantics'
            if outside:flag='source_body_box_outside_page'
            show_rows=rows if not outside and json.loads(seg['body_bbox_pt']) and seg['review'] not in ('rejected','region_rejected','wrong_body_region') else []
            text.extend([f'<section id="{E(key)}"><h2>Source PDF {pg} · {E(seg["part"])}</h2>','<p class="bar">'+link('../pdf/'+doc+'.pdf#page='+str(w),'Complete source witness')+link(docs[doc]['source_url']+'#page='+str(pg),'Publisher page')+'</p>',
                         note('Geometry status: '+seg['status']+' · review: '+seg['review']+' · orientation: '+seg['reading_orientation_deg']+'°.'),note(seg.get('notes',''))])
            crop=''
            if pdf_ok:
                sourcefile=root/'sr/primary'/seg['source']
                if sourcefile not in source_docs:source_docs[sourcefile]=fitz.open(sourcefile)
                srcpage=source_docs[sourcefile][pg-1];clip=fitz.Rect(json.loads(seg['body_bbox_pt'])) & srcpage.rect
                if not clip.is_empty:
                    crop='sr_tables/checked_regions/'+key+'.png';op=out/crop;op.parent.mkdir(exist_ok=True)
                    srcpage.get_pixmap(clip=clip,matrix=fitz.Matrix(1.5,1.5),annots=False).save(op)
                    text.append('<details><summary>Visually checked geometry · publisher crop</summary><figure><img loading="lazy" alt="Original table source segment" src="checked_regions/'+key+'.png"></figure></details>')
            for f,rs in named:
                namedfile=dst/f.name
                shutil.copyfile(f,namedfile)
                preview=f.with_suffix('.png')
                if not preview.is_file() and f.stem.endswith('_marks'):preview=f.with_name(f.stem[:-6]+'.png')
                if preview.is_file():
                    shutil.copyfile(preview,dst/preview.name)
                    text.append('<p>'+link(preview.name,'Source-image check for the named transcription')+'</p>')
                disp=[k for k in rs[0] if k not in ('item_id','source','pdf_page','print_page','row_bbox_pt','status')]
                title='Visible symbols and printed column labels; sample identity unresolved' if 'sample_assignment' in rs[0] else 'Visually read and field-mapped'
                text+=['<h3>'+title+'</h3>',link(namedfile.name,'Source values and coordinates (CSV)'),grid(disp,rs)]
            hs=fields[key]
            if vertical[key]:
                text.extend(['<details><summary>Vertical heading candidates (independent readings)</summary>'+note('These text and rotation records are independent of the horizontal cell positions. No taxon-to-sample assignment follows from this display.')+grid(['reading_source','native_baseline_deg','text_candidate','mean_ocr_confidence','bbox_pt'],vertical[key])+'</details>'])
            if hs:
                text.extend(['<details><summary>Positional header evidence</summary>'+grid(['col','header_as_located','reading_x_interval_pt','status'],hs)+'</details>'])
            if show_rows:
                text.append('<details><summary>Positional OCR by physical row · '+str(len(show_rows))+' rows</summary>'+grid(cols,show_rows)+'</details>')
                text.append(note('Tokens spanning position boundaries are shown in the separate spanning column. A pipe separates multiple fragments assigned to one position; their original boxes remain in the token file.'))
            else:
                reason='The printed table body is visible as a raster; no readable positional rows were established.' if seg['status']=='raster_body_only' else 'No body-row display is authorized for this source segment.'
                text.append(note(reason+' Consult the complete page and the registered opening or continuation caption.'))
            text.append('</section>')
            record=dict(item_id=item,doc_id=doc,segment=key,source_pdf_page=pg,source_print_page=seg['print_page'],source_witness_page=w,
                        state=flag,geometry_status=seg['status'],geometry_review=seg['review'],orientation_deg=seg['reading_orientation_deg'],
                        caption_box_pt=seg['caption_bbox_pt'],header_box_pt=seg['header_bbox_pt'],body_box_pt=seg['body_bbox_pt'],
                        physical_rows=seg['physical_body_rows'],candidate_cell_slots=seg['body_cells'],html='sr_tables/'+leaf.name+'#'+key,
                        vertical_header_records=len(vertical[key]),vertical_readings_csv='sr_tables/'+vfile.name if vertical[key] else '',checked_source_crop=crop,positioned_records='sr_tables/'+raw_file.name,header_dictionary='sr_tables/'+dictfile.name if hs else '',
                        pdf_appendix_first='',pdf_appendix_last='',named_rows=sum(len(rs) for f,rs in fully_named),unassigned_marks=sum(len(rs) for f,rs in marked),named_fields_csv='|'.join('sr_tables/'+f.name for f,rs in fully_named),mark_readings_csv='|'.join('sr_tables/'+f.name for f,rs in marked))
            outputs.append(record);links[doc][pg].append(record)
            if named or pdf_ok:
                doc_pdf[doc].append((record,named,(cols,show_rows) if pdf_ok else None,hs,seg['notes']))
        leaf.write_text(''.join(text)+'</main></body></html>')
        catalog.append(dict(item_id=item,doc_id=doc,start_source_page=table['start_pdf_page'],title=table['caption'],segments=table['segments'],
                            located_segments=table['located_segments'],geometric_status=table['status'],visual_review=table['review'],
                            original_pdf_pages=table['pdf_pages'],html='sr_tables/'+leaf.name,positioned_cells='sr_tables/'+raw_file.name,
                            physical_rows=table['physical_body_rows'],body_cells=table['body_cells']))
    for f in source_docs.values():f.close()
    for doc,entries in doc_pdf.items():
        path=out/docs[doc]['pdf'];source=fitz.open(path);before=len(source)
        r=Reader(doc,'SR table evidence supplement',fonts);toc=source.get_toc();toc.append([1,'Additional print-table evidence',before+1])
        for rec,named,position,hs,notes in entries:
            pg=rec['source_pdf_page'];item=rec['item_id'];url=docs[doc]['source_url']+'#page='+str(pg)
            r.header(pg,rec['source_print_page'],url,'Print-table supplement');start=r.num
            if named:
                for f,rs in named:
                    disp=[k for k in rs[0] if k not in ('item_id','source','pdf_page','print_page','row_bbox_pt','status')]
                    ismark='sample_assignment' in rs[0]
                    label='visible marks, sample identity unresolved' if ismark else 'visually read and field-mapped'
                    reason='Each record identifies a visible symbol, its printed taxon column, and source box. The lateral continuation does not establish the biological sample identity.' if ismark else 'Values and source row positions were collated with the published table. Full provenance fields accompany this transcript.'
                    if item=='SR.C04.TABLE2' and not ismark:reason+=' Slope and intercept retain their separately printed plus/minus magnitudes.'
                    if item=='SR.C21.TABLE2' and not ismark:reason+=' Horizon number, taxon and source-defined event code remain separate fields.'
                    r.table({'item_id':item,'label':label,'display_columns':disp,'editorial_note':reason},rs)
            if position:
                cols,rows=position
                r.paragraph(item+'  ·  physical position reading','heading')
                r.paragraph('The page segment was visually checked for geometry. Text, numerals and positional headings remain OCR candidates. Empty positions have no inferred values. Spanning tokens state their position range. The digital companion contains both original word and cell boxes.','notice')
                if notes:r.paragraph(notes,'notice')
                if hs:r.paragraph('Positional header candidates: '+'; '.join('P'+str(h['col']).zfill(2)+' '+h['header_as_located'] for h in hs),'notice')
                r.table({'item_id':item,'label':'column-position transcript · unproofed OCR','display_columns':cols},rows)
            rec['pdf_appendix_first']=before+start;rec['pdf_appendix_last']=before+r.num;r.end()
            toc.append([2,item+' · source '+str(pg),rec['pdf_appendix_first']])
        annex=fitz.open(stream=r.finish(),filetype='pdf');source.insert_pdf(annex);source.set_toc(toc)
        for rec,named,position,hs,notes in entries:
            pg=rec['source_pdf_page'];main=pages[(doc,pg)];first=int(main['edition_first'])-1
            for n in range(int(rec['pdf_appendix_first'])-1,int(rec['pdf_appendix_last'])):
                source[n].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(192,H-40,325,H-22),'page':rec['source_witness_page']-1,'to':fitz.Point(0,0)})
            if first not in footlinks[doc]:
                leaf=source[first];leaf.insert_text((343,H-29),'Print-table supplement',fontsize=8,fontname='helv',color=(.15,.37,.32))
                leaf.insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(341,H-40,454,H-22),'page':rec['pdf_appendix_first']-1,'to':fitz.Point(0,0)})
                footlinks[doc][first]=rec['pdf_appendix_first']
            hp=out/('sr_tables/'+rec['item_id']+'.html');html_doc=hp.read_text();key='<section id="'+rec['segment']+'">'
            hlink=link('../pdf/'+doc+'.pdf#page='+str(rec['pdf_appendix_first']),'Typeset evidence supplement · chapter PDF '+str(rec['pdf_appendix_first']))
            hp.write_text(html_doc.replace(key,key+'<p class="meta">'+hlink+'</p>',1))
        tmp=path.with_suffix('.new.pdf');source.save(tmp,garbage=3,deflate=True,no_new_id=True);new_count=len(source);source.close();annex.close();tmp.replace(path)
        docs[doc]['edition_pdf_pages']=str(new_count);docs[doc]['typeset_pages']=str(int(docs[doc]['typeset_pages'])+new_count-before);docs[doc]['edition_pdf_sha256']=digest(path)
        docs[doc]['sr_table_appendix_pages']=new_count-before
    for d in docs:docs[d].setdefault('sr_table_appendix_pages',0)
    for d,perpage in links.items():
        docfile=out/docs[d]['html'];text=docfile.read_text()
        for pg,rels in perpage.items():
            marker=f'<section id="p{pg}">';buttons=' · '.join(link('../'+rec['html'],rec['item_id']+' ('+rec['state'].replace('_',' ')+')') for rec in rels)
            text=text.replace(marker,marker+'<p class="meta">SR print-table annex · '+buttons+'</p>',1)
        docfile.write_text(text)
    write(out/'documents.csv',list(docs.values()));write(out/'sr_table_annex.csv',outputs);write(out/'sr_table_catalog.csv',catalog)
    viewed=Counter(v['state'] for v in outputs)
    stats=dict(items=len(catalog),segments=len(outputs),geometry_status_counts=dict(viewed),items_with_positional_cells=sum(int(r['body_cells'])>0 for r in catalog),
               candidate_body_cells=sum(int(r['body_cells']) for r in catalog),physical_body_rows=sum(int(r['physical_rows']) for r in catalog),
               independent_vertical_header_candidates=sum(v['vertical_header_records'] for v in outputs),field_mapped_named_rows=sum(r['named_rows'] for r in outputs),separately_transcribed_unassigned_marks=sum(r['unassigned_marks'] for r in outputs),items_with_field_mapped_named_rows=len({r['item_id'] for r in outputs if r['named_rows']}),
               segments_in_typeset_evidence_supplement=sum(bool(r['pdf_appendix_first']) for r in outputs),new_chapter_pdf_pages=sum(v['sr_table_appendix_pages'] for v in docs.values()),
               input_digests={p.name:digest(p) for p in deps + sorted(package.glob('verified_*.csv')) + [package/'visual_regions.csv',vsource] if p.exists()})
    (out/'sr_table_annex_checks.json').write_text(json.dumps(stats,indent=2)+'\n')
    core=out/'verification.json';counts=json.loads(core.read_text());counts['typeset_pages']+=stats['new_chapter_pdf_pages'];counts['paired_pdf_pages']+=stats['new_chapter_pdf_pages'];counts['sr_print_annex_pages']=stats['new_chapter_pdf_pages'];core.write_text(json.dumps(counts,indent=2)+'\n')
    book=out/'index.html';book.write_text(book.read_text().replace('</header>','<p>'+link('sr_tables/index.html','SR 印表逐项坐标附表')+' · '+link('sr_table_annex.csv','数据状态与来源页')+'</p></header>',1))
    listing=[header('SR print-table annex'),link('../index.html','Leg 138 catalogue'),'<h1>SR 印表 · 来源与位置读数</h1>',note(str(len(catalog))+' 张原先无具名数据的印表逐项保留页码。先读经原图确认的字段，再查看标有证据状态的候选位置。'),'<div class="scroll" style="max-height:none"><table><thead><tr><th>Table</th><th>Chapter PDF pages</th><th>Geometry state</th><th>Physical rows</th></tr></thead><tbody>']
    for c in catalog:listing.append('<tr><td>'+link(Path(c['html']).name,c['item_id'])+'</td><td>'+E(c['original_pdf_pages'])+'</td><td>'+E(c['geometric_status'])+'</td><td>'+E(c['physical_rows'])+'</td></tr>')
    (dst/'index.html').write_text(''.join(listing)+'</tbody></table></div></main></body></html>')
    return stats
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('output',type=Path);p.add_argument('--fonts',type=Path,default=Path('/usr/share/fonts/truetype/dejavu'))
    a=p.parse_args();print(json.dumps(publish(a.root,a.output,a.fonts),indent=2))
