"""Index IR's printed chapter catalogue, numbered figures, tables, candidate captions and original PDF page text."""
from pathlib import Path
from collections import defaultdict
import re,csv,json,gzip,fitz
from lxml import html
from native import ROOT,P,C,ident,member,write
FIRST=[5,13,43,67,79,87,93,101,119,189,265,335,677,735,809,891,967,1023,1063,1095]
PROSE={(3,'F',1,1),(9,'T',12,40),(10,'T',10,42),(10,'T',10,43),(11,'T',8,33),(11,'F',22,30),(12,'T',8,25),(12,'T',13,25),(12,'F',16,13),(13,'F',25,22),(14,'T',8,40),(15,'T',24,41),(16,'T',10,45),(17,'T',11,30),(18,'T',5,16),(18,'T',5,17),(18,'T',5,18),(18,'T',8,24),(19,'T',7,21)}
EXTRA={(9,'F',16):(22,'Biostratigraphy of Site 844; descriptive editorial title (the printed caption on this page consists of the figure number)'),(9,'F',4):(6,'Seismic profile of proposed Site EEQ-2'),(11,'F',4):(7,'Seismic Line G, proposed Site EEQ-4'),(12,'F',4):(6,'Seismic profile of proposed Site EEQ-3'),(12,'F',15):(18,'Pyritized Chondrites burrow'),(13,'F',4):(7,'Seismic profile of proposed Site WEQ-5'),(17,'F',4):(6,'Seismic profile of proposed Site WEQ-3'),(18,'F',30):(33,'Grain density vs. depth, Holes 853B and 853C')}
def offlist():
 d=fitz.open(P/'VOLUME/CHAPTERS/138ir.pdf')
 records={};ch=None
 for pn in (14,15,16,21,22,23,24):
  lines=d[pn-1].get_text().splitlines()
  if pn in (14,21):
   i=next(i for i,s in enumerate(lines) if s.startswith('CD-ROM Tables'))
   lines=lines[i:]
  for i,s in enumerate(lines):
   if m:=re.match(r'^Chapter\s+(\d+)[.:]\s*$',s.strip()):ch=int(m[1]);continue
   if ch and (m:=re.match(r'^Table\s*(\d+)\.\s*(.*)',s.strip())):
    title=m[2].strip()
    for ss in lines[i+1:]:
     ss=ss.strip()
     if not ss or ss.startswith(('Table','Chapter','*')) or title.endswith('.'):break
     title+=' '+ss
    records[(ch,int(m[1]))]=(pn,title.rstrip('.'))
 return records
def foldouts(tree):
 ext={}
 for a in tree.xpath('//a[contains(@href,"ir138_f")]'):
  block=a.xpath('following::blockquote[1]')[0]
  t=' '.join(block.itertext());t=' '.join(t.split())
  for m in re.finditer(r'Chapter\s+(\d+),\s*Figure\s+(\d+)\.\s*(.*?)(?=Chapter\s+\d+|$)',t):ext[(int(m[1]),int(m[2]))]=(a.attrib['href'],m[3].strip().rstrip('.'))
 assert len(ext)==13
 return ext
def caption(l,kind,n):
 t=' '.join(l.split())
 t=re.sub(r'^(?:Figure|Table)\s*\d+\s*\.\s*','',t,flags=re.I)
 return t.strip(' .')
def main():
 toc=html.fromstring((P/'main.htm').read_bytes());idx=offlist();fold=foldouts(toc)
 assert len(idx)==183,len(idx)
 arows=sorted([a for a in toc.xpath('//a') if re.search(r'ir138_\d\d\.pdf$',a.attrib.get('href',''))],key=lambda a:a.attrib['href']); assert len(arows)==20
 items=[];docs=[];loc=[];gaps=[];ac=[];audit=[]
 with gzip.open(C/'chapter_pages.csv.gz','wt',encoding='utf8',newline='') as f:
  w=csv.writer(f);w.writerow(['chapter','site','pdf_path','pdf_page','printed_page','printed_page_basis','source_text'])
  for ch,a in enumerate(arows,1):
   path=a.attrib['href'];site=str(835+ch) if 9<=ch<=19 else ''
   title=' '.join(' '.join(a.itertext()).split());title=re.sub(r'^\d+\.\s*','',title)
   doi=f'10.2973/odp.proc.ir.138.{100+ch}.1992'
   assert doi in ' '.join(toc.itertext())
   d=fitz.open(P/path);first=FIRST[ch-1];docs.append([ch,site,title,doi,path,len(d),first,first+len(d)-1])
   candidates=defaultdict(list);refs=defaultdict(list);folio={}
   for j,p in enumerate(d,1):
    t=p.get_text('text');pn=first+j-1
    numwords=[s for s in p.get_text('words') if s[4]==str(pn) and (s[1]>p.rect.height*.90 or s[3]<p.rect.height*.10)]
    basis='page_margin_text_match' if numwords else 'sequential_from_chapter_pagination'
    folio[j]=basis
    w.writerow([ch,site,path,j,pn,basis,t])
    for typ,rx in [('T',r'(?i)\btables?\s+(\d{1,3})\b'),('F',r'(?i)\b(?:fig(?:ure)?s?\.?)\s*(\d{1,3})\b')]:
     for m in re.finditer(rx,t):refs[(typ,int(m[1]))].append(j)
    for block in p.get_text('dict')['blocks']:
     lines=block.get('lines',[])
     for i,l in enumerate(lines):
      s=''.join(z['text'] for z in l['spans']).strip()
      # Require a caption terminator or a continuation, not a prose reference.
      if not (m:=re.match(r'^(Figure|Table)\s*(\d{1,2})\s*(\.|\(continued\)[.]?|[,:]\s*cont(?:inued)?[.])\s*(.*)',s,re.I)):continue
      k=(m[1][0].upper(),int(m[2]))
      if (ch,k[0],k[1],j) in PROSE:continue
      suffix=m[3]; role='caption_text_layer' if suffix=='.' else 'continued_caption_text_layer'
      head=m[4].strip()
      # Captions in the same PDF text block sometimes continue in multiple lines.
      # Keep only the caption head as searchable title; preserve full page OCR independently.
      candidates[k].append((j,role,','.join(f'{v:.1f}' for v in l['bbox']),head))
   for (cc,typ,n),(j,head) in EXTRA.items():
    if cc==ch:candidates[(typ,n)].append((j,'page_image_checked','',head))
   for typ in ['T','F']:
    ns={n for t,n in candidates if typ==t}|({n for cc,n in idx if cc==ch} if typ=='T' else {n for cc,n in fold if cc==ch})
    for n in range(1,max(ns,default=0)+1):
     ii=ident(ch,typ,n);cands=candidates.get((typ,n),[])
     firstcap=next((v for v in cands if v[1]=='page_image_checked'),None) or next((v for v in cands if v[1]=='caption_text_layer'),None)
     pg0=firstcap[0] if firstcap else ''
     ttl=(firstcap[3] if firstcap else '')
     native=member(ch,n) if typ=='T' and (P/member(ch,n)).is_file() else ''
     printcsv=f'print_tables/IR{ch:02}_T{n:02}.csv' if typ=='T' and (C/f'print_tables/IR{ch:02}_T{n:02}.csv').is_file() else ''
     ppath=path; pg=pg0; pr=first+pg-1 if pg else ''
     if typ=='T' and (ch,n) in idx:ttl=idx[(ch,n)][1]
     if typ=='F' and (ch,n) in fold:
      ppath,ttl=fold[ch,n];pg=pr='';status='foldout_from_official_contents'
      loc.append([ii,ppath,'','','','foldout_container_from_official_contents','',''])
     elif firstcap:
      status=firstcap[1]+('_with_native_table' if native else '_with_print_transcription' if printcsv else '')
     elif native or (typ=='T' and (ch,n) in idx):
      status='listed_native_table_no_detected_caption' if native else 'disc_list_entry_no_online_file'
      # Store narrative page as such, rather than labelling it a printed table.
      if refs.get((typ,n)):
       pg=refs[(typ,n)][0];pr=first+pg-1;loc.append([ii,path,pg,pr,folio[pg],'narrative_reference_candidate','',''])
     else:
      gaps.append([ch,site,typ,n,'no_caption_or_distribution_evidence']);continue
     if firstcap or cands:
      for pp,role,box,s in cands:
       loc.append([ii,path,pp,first+pp-1,folio[pp],role,box,s])
     items.append([ii,ch,site,'table' if typ=='T' else 'figure',n,ttl,status,ppath,pg,pr,native,printcsv])
     if typ=='T' and (ch,n) in idx:
      fp,title=idx[ch,n];ac.append([ii,ch,site,n,fp,title,native,'online' if native else 'listed_without_online_table',printcsv])
   for pg,v in folio.items():audit.append([ch,pg,v])
 write(C/'chapters.csv',['chapter','site','title','doi','pdf_path','pdf_pages','printed_first','printed_last'],docs)
 write(C/'chapter_items.csv',['item_id','chapter','site','kind','number','title','status','pdf_path','pdf_page','printed_page','native_path','print_csv'],items)
 write(C/'chapter_item_locations.csv',['item_id','pdf_path','pdf_page','printed_page','printed_page_basis','anchor_kind','caption_bbox_xyxy_pt','source_caption_head'],loc)
 write(C/'disc_list_collation.csv',['item_id','chapter','site','number','front_matter_pdf_page','front_matter_title','native_path','availability','print_csv'],ac)
 write(C/'caption_gaps.csv',['chapter','site','type','number','status'],gaps)
 print('Volume items',len(items),'chapters',len(docs),'caption or citation locators',len(loc),'gaps',gaps)
 print('F/T',sum(x[3]=='figure' for x in items),sum(x[3]=='table' for x in items),'pages',len(audit))
if __name__=='__main__':main()
