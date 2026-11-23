"""Index the official Scientific Results volume. Physical PDF leaves and evidence roles remain distinct."""
from pathlib import Path
import csv,json,gzip,re,os,collections,html
from lxml import html as lh
import fitz
C=Path(__file__).resolve().parents[1];R=C.parent;P=R/'primary'
def norm(s):return ' '.join(s.split())
def write(name,fields,rows):
    with (C/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def site_matches(s):
    # Qualifying a site requires a printed identifier, e.g. Site 846, Holes 851A–C, or 138-846B-.
    # A bare integer in a plot or geological age is never a site identifier.
    station=r'(?:84[4-9]|85[0-4])'
    term=station+r'[A-E]?';sep=r'(?:\s*(?:,|;|\band\b|\bor\b|\bto\b|\bthrough\b|[-–—])\s*)'
    result={}
    for m in re.finditer(r'\b(?:ODP\s+)?(?:Sites?|Holes?)\s+('+term+r'(?:'+sep+term+r')*)(?!\d)',s,re.I):
        g=m[1]
        for q in re.finditer(station,g):
            result.setdefault(int(q[0]),(m[0],m.start(),'explicit_identifier'))
        for q in re.finditer('('+station+r')[A-E]?\s*(?:[-–—]|\bto\b|\bthrough\b)\s*('+station+')',g,re.I):
            if int(q[1])<=int(q[2]):
                for x in range(int(q[1])+1,int(q[2])):result.setdefault(x,(m[0],m.start(),'range_member'))
    for m in re.finditer(r'(?<!\d)138[-–]('+station+r')[A-E](?:[-–]|\b)',s,re.I):result.setdefault(int(m[1]),(m[0],m.start(),'sample_identifier'))
    return result
def extract():
    gate=catalogue=list(csv.DictReader((C/'source_manifest.csv').open()))
    toc=lh.fromstring((P/'official/main.htm').read_bytes())
    authors={}
    for a in toc.xpath('//a[@href]'):
        t=norm(a.text_content());m=re.match(r'^(\d{1,2})\.\s',t)
        if not m:continue
        br=a.xpath('following::br[1]')
        authors[int(m[1])]=norm(br[0].tail or '') if br else ''
    cite=norm(lh.fromstring((P/'official/citations/cite138.html').read_bytes()).text_content())
    span={doi:(int(lo),int(hi)) for lo,hi,doi in re.findall(r'(\d+)\s*[-–—\x96]\s*(\d+)\.\s*doi:(10\.2973/odp\.proc\.sr\.138\.\d+\.1995)',cite)}
    headings=re.compile(r'^(Figure|FIGURE|Table|TABLE|Plate\.?|PLATE\.?|Fig\.?|FIG\.?)\s+([1-9]\d?[a-dA-D]?|[lI][a-dA-D]?)(?:\s*[.:]\s*|\s+\((?:cont|continued))')
    ca=[];pages=[];anchors=[];site_ev=[];newitems={};eps=[]
    def siteadd(ch,item,role,source,pdf,txt,explicit_only=False):
        for site,(mt,idx,method) in site_matches(txt).items():
            clip=norm(txt[max(0,idx-35):idx+max(len(mt),35)+65])
            site_ev.append([ch,item,site,role,method,source,pdf,clip])
    for row in catalogue:
        if row['kind'] not in ('chapter','chapter_reprint','front_matter','volume_index','ch21_fig17_foldout','erratum_ch01_caption'):continue
        ch=int(row['chapter'] or 0);doc=fitz.open(P/row['source']);num_pages=len(doc)
        if row['kind'] in ('chapter','chapter_reprint'):
            title=row['title'];lo,hi=span.get(row['doi'], (911,930) if ch==47 else (0,0))
            siteadd(ch,'','title',row['source'],1,title)
            ca.append(dict(chapter=ch,kind=row['kind'],title=title,authors=authors[ch],doi=row['doi'],source=row['source'],url=row['url'],pdf_pages=num_pages,print_page_first=lo or '',print_page_last=hi or ''))
        else:lo=0;hi=0
        for i,pg in enumerate(doc,1):
            raw=pg.get_text()
            cand=[(w[1],w[4]) for w in pg.get_text('words') if w[1]>.86*pg.rect.height and (w[0]<pg.rect.width*.19 or w[2]>pg.rect.width*.80) and re.fullmatch(r'\d{1,4}',w[4]) and (not lo or lo<=int(w[4])<=hi)]
            cand.sort(reverse=True)
            folio=cand[0][1] if cand and row['kind'] in ('chapter','chapter_reprint') else None
            basis='outer_foot_text_layer' if folio else 'unassigned'
            if not folio and lo and hi-lo+1==num_pages:folio=str(lo+i-1);basis='inferred_from_citation_and_leaf_count'
            pages.append(dict(chapter=ch,source=row['source'],pdf_page=i,printed_page=folio,folio_basis=basis,width_pt=round(pg.rect.width,2),height_pt=round(pg.rect.height,2),text_status='official_pdf_text_layer_unproofed',text=raw))
            if row['kind'] not in ('chapter','chapter_reprint'):continue
            if i==1:
                m=re.search(r'\bABSTRACT\b(.*?)(?:\n(?:INTRODUCTION|BACKGROUND|OBJECTIVES|METHODS)\b)',raw,re.S)
                if m:siteadd(ch,'','abstract',row['source'],i,norm(m[1]))
            siteadd(ch,'','page_mention',row['source'],i,norm(raw))
            for block in pg.get_text('blocks'):
                if len(block)<7 or block[6]!=0:continue
                lines=[norm(v) for v in block[4].splitlines() if v.strip()]
                for j,line in enumerate(lines):
                    m=headings.match(line)
                    if not m:continue
                    name=m[1].lower().rstrip('.');kind='figure' if name=='fig' else name;no=m[2].lower()
                    if no[0] in ('i','l'): no='1'+no[1:]
                    key=f'SR.C{ch:02d}.{kind.upper()}{no.upper()}'
                    # Several captions can share one text block. Stop before the next caption.
                    tail=[]
                    for part in lines[j+1:j+6]:
                        if headings.match(part):break
                        tail.append(part)
                    caption=' '.join([line,*tail])[:800]
                    anchors.append(dict(item_id=key,chapter=ch,kind=kind,number=no,source=row['source'],pdf_page=i,print_page=folio,bbox_pt=json.dumps([round(v,2) for v in block[:4]]),caption_text=caption,anchor_basis='pdf_caption_candidate'))
                    if key not in newitems or (len(newitems[key]['label'])<=12 and len(caption)>18):newitems[key]=dict(item_id=key,chapter=ch,kind=kind,number=no,source=row['source'],pdf_page=i,print_page=folio,label=caption[:230],status='pdf_caption_candidate')
                    siteadd(ch,key,'caption_candidate',row['source'],i,caption)
        doc.close()
    by_chapter={r['chapter']:r for r in ca}
    # Edition-specific and manual evidence supplements deterministic PDF caption detection.
    def overlay(ch,kind,number,source,pdf,folio,title,basis):
        key=f'SR.C{ch:02d}.{kind.upper()}{number}'
        anchors.append(dict(item_id=key,chapter=ch,kind=kind,number=number,source=source,pdf_page=pdf,print_page=folio,bbox_pt='',caption_text=title,anchor_basis=basis))
        newitems[key]=dict(item_id=key,chapter=ch,kind=kind,number=number,source=source,pdf_page=pdf,print_page=folio,label=title,status=basis)
        return key
    for ch,leaf,folio,title in [(31,5,651,'Table 1. Classification of the laminae.'),(37,2,770,'Table 1. Chemical composition of sedimentary formations.'),(41,2,814,'Table 1. Summary of Leg 138 sites and Sr-isotope reversals.')]:
        overlay(ch,'table','1',by_chapter[ch]['source'],leaf,folio,title,'scan_located_rotated_caption')
    for legacy in csv.DictReader((C/'verified846/items.csv').open()):
        ch=int(legacy['chapter']);kind=legacy['kind'];n=legacy['number'];title=legacy['title']
        if kind=='appendix':n='1' if ch==3 else n.removeprefix('app').upper()
        else:n=n[1:].upper()
        key=f'SR.C{ch:02d}.{kind.upper()}{n}';pdf=legacy['pdf_page_from'];folio=legacy['page_from']
        ref=by_chapter[ch]['source']
        basis='site846_reviewed_print_location'
        # Keep published wording when the earlier checked leaf agrees with the caption.
        if key in newitems and str(newitems[key]['pdf_page'])==pdf:
            title=newitems[key]['label']
        overlay(ch,kind,n,ref,pdf,folio,title,basis)
        site_ev.append([ch,key,846,'site846_editorial_selection','prior_item_review',ref,int(pdf),legacy['title']])
    assets=[]
    for s in catalogue:
        kind=s['kind'];src=s['source'];key=''
        if kind in ('cd_data','erratum_ch39_table2'):
            from build_tables import table_meta
            ch,term,key,_=table_meta(src)
            if key not in newitems:
                k='table' if term.startswith('TABLE') else 'appendix'
                overlay(ch,k,term.removeprefix(k.upper()),src,'','',term,'publisher_companion_only')
            assets.append([key,ch,src,'corrected_electronic_table' if kind.startswith('erratum') else 'cd_electronic_table'])
        elif kind=='quicktime_panel':
            assets.append(['SR.C01.FIGURE7',1,src,'movie_panel_'+Path(src).stem[-1]])
        elif kind=='ch21_fig17_foldout':
            overlay(21,'figure','17',src,1,'','Figure 17. Chapter 21 foldout.','publisher_foldout_pdf')
            assets.append(['SR.C21.FIGURE17',21,src,'foldout'])
        elif kind in ('erratum_ch01_caption','erratum_ch39_notice'):
            assets.append(['SR.C01.FIGURE7' if kind=='erratum_ch01_caption' else 'SR.C39.TABLE2',1 if kind=='erratum_ch01_caption' else 39,src,'erratum_notice'])
    for s in csv.DictReader((C/'print_datasets.csv').open()):
        ch=int(s['chapter']);key=s['item_id'];src=s['source'];pdf=int(s['source_pdf_page_from'])
        assets.append([key,ch,s['file'],'edited_print_transcription'])
        if ch==41:
            for record in csv.DictReader((C/s['file']).open()):
                site_ev.append([ch,key,int(record['site']),'verified_print_row','table_row',src,pdf,'Table 1, row '+record['printed_row']+', '+record['location_as_printed']])
    with (C/'assets.csv').open('w',newline='') as o:
        w=csv.writer(o);w.writerow(['item_id','chapter','source_or_edited_path','relation']);w.writerows(assets)
    eps.extend([
        dict(id='SR.ERRATUM1',chapter=1,item_id='SR.C01.FIGURE7',effect='CD-ROM contents caption corrected; six Site 846 QuickTime panels retained',notice='official/VOLUME/CHAPTERS/138_corx.pdf',original='official/VOLUME/CHAPTERS/138sr.pdf',replacement='',date=''),
        dict(id='SR.ERRATUM39',chapter=39,item_id='SR.C39.TABLE2',effect='Separately published replacement of CD Table 2; retain both row populations',notice='official/index.html',original='official/VOLUME/DATA/CHAP39/138150T2.TXT',replacement='official/39_02.txt',date='2000-03-29')])
    def write_jsongz(file,rows):
        with (C/file).open('wb') as f,gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:
            for v in rows:z.write((json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n').encode())
    write('chapters.csv',ca[0].keys(),sorted(ca,key=lambda x:x['chapter']))
    write('caption_anchors.csv',anchors[0].keys(),anchors)
    write('items.csv',list(next(iter(newitems.values()))),sorted(newitems.values(),key=lambda r:(r['chapter'],r['kind'],int(m[0]) if (m:=re.match(r'\d+',r['number'])) else 0,r['number'])))
    write('errata.csv',eps[0].keys(),eps)
    with (C/'site_evidence.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow('chapter item_id site evidence_role match_method source pdf_page excerpt'.split());w.writerows(sorted(set(tuple(r) for r in site_ev)))
    write_jsongz('pages.jsonl.gz',pages)
    print('chapters, pages, anchors, items, site evidence',len(ca),len(pages),len(anchors),len(newitems),len(site_ev),'spans',len(span))
if __name__=='__main__':extract()
