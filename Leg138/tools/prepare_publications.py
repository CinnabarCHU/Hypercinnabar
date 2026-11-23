"""Extract navigable PDF text layers, native document titles and principal hole checks."""
import argparse,csv,gzip,hashlib,json,re,subprocess
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
import fitz

class Anchors(HTMLParser):
    def __init__(self):super().__init__();self.links={};self.href=None;self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.href=dict(attrs).get('href','');self.parts=[]
    def handle_data(self,t):
        if self.href:self.parts.append(t)
    def handle_endtag(self,tag):
        if tag=='a' and self.href:
            self.links[self.href]=' '.join(''.join(self.parts).split());self.href=None
def csvread(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))
def csvwrite(p,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
def folio(pdf):
    rect=pdf.rect
    nums=[]
    for word in pdf.get_text('words'):
        x,y,r,b,t=word[:5]
        if y>rect.height*.865 and t.isdigit() and (r<rect.width*.22 or x>rect.width*.77) and len(t)<=4:nums.append((y,int(t)))
    return max(nums)[1] if nums else None
def text_layer(params):
    root,doc=params
    p=root/doc['local_source']
    raw=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,check=True).stdout.decode('utf-8').split('\f')
    with fitz.open(p) as d:
        assert len(raw) in (len(d),len(d)+1),(p,len(raw),len(d))
        pages=[]
        for n,page in enumerate(d,1):
            t=raw[n-1].strip('\n')
            if doc['series'] in ('SP','PR'):
                m=re.search(r'^\s*page\s+(\d+)\s*$',t,re.M|re.I)
                printed=int(m[1]) if m else {('PR',29):30,('PR',30):31,('PR',44):46,('SP',43):44,('SP',46):47}.get((doc['series'],n))
            else:printed=folio(page)
            pages.append(dict(doc_id=doc['doc_id'],pdf_page=n,printed_page=printed,basis='text_layer_or_known_print_folio' if doc['series'] in ('SP','PR') else 'footer_candidate',text=t))
        return pages,len(d)
def build(root,out):
    out.mkdir(exist_ok=True,parents=True);docs=[]
    base='https://www-odp.tamu.edu/publications/'
    def append(code,series,ch,site,title,role,path,url,doi='',pages=''):
        docs.append(dict(doc_id=code,series=series,chapter=ch,site=site,title=title,role=role,local_source=path,url=url,doi=doi,pdf_pages=pages))
    append('SP','SP','','','Leg 138 Scientific Prospectus','precruise_plan','sppr/primary/SP.pdf',base+'prosp/digital/138prosp.pdf')
    append('PR','PR','','','Leg 138 Preliminary Report','preliminary_shipboard_report','sppr/primary/PR.pdf',base+'prelim/138PREL.PDF')
    parser=Anchors();parser.feed((root/'ir/primary/main.htm').read_text(errors='replace'))
    irfiles=csvread(root/'ir/core/sources.csv')
    ir_chapters={r['pdf_path']:r for r in csvread(root/'ir/core/chapters.csv')}
    for r in irfiles:
        path=r['path']
        if not path.lower().endswith('.pdf'):continue
        leaf=Path(path).name;ch=re.fullmatch(r'ir138_(\d\d).pdf',leaf)
        if ch:
            n=int(ch[1]);site=str(n+835) if 9<=n<=19 else ''
            ident=f'IR.C{n:02}';title=parser.links.get(path,f'Chapter {n}');role='site_chapter' if site else 'leg_chapter'
        else:
            n='';site='';ident='IR.'+Path(path).stem;title=parser.links.get(path,'Volume contents' if leaf=='138ir.pdf' else leaf);role='volume_material'
        append(ident,'IR',n,site,title,role,'ir/primary/'+path,r['url'],doi=ir_chapters.get(path,{}).get('doi',''),pages=r['pdf_pages'])
    srfiles=csvread(root/'sr/core/source_manifest.csv')
    chapters={r['source']:r for r in csvread(root/'sr/core/chapters.csv')}
    sr_source={}
    for r in srfiles:
        path=r['source']
        if not(path.startswith('official/') and path.lower().endswith('.pdf')):continue
        c=chapters.get(path)
        ident=f"SR.C{int(c['chapter']):02}" if c else 'SR.'+Path(path).stem
        append(ident,'SR',c['chapter'] if c else '','',c['title'] if c else r['title'],c['kind'] if c else 'volume_material','sr/primary/'+path,r['url'],r['doi'],r['pages']);sr_source[path]=ident
    pages=0
    with (out/'pages.jsonl.gz').open('wb') as f,gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:
        def save(obj):
            z.write((json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n').encode())
        subset=[d for d in docs if d['series']!='SR']
        with ThreadPoolExecutor(max_workers=5) as ex:
            for doc,(rows,n) in zip(subset,ex.map(text_layer,((root,d) for d in subset)),strict=True):
                doc['pdf_pages']=n
                for row in rows:save(row);pages+=1
        got=set()
        with gzip.open(root/'sr/core/pages.jsonl.gz','rt') as f:
            for line in f:
                row=json.loads(line);key=sr_source[row['source']];got.add(key)
                save(dict(doc_id=key,pdf_page=row['pdf_page'],printed_page=row['printed_page'],basis=row['folio_basis'],text=row['text']));pages+=1
        for d in docs:
            if d['series']=='SR' and d['doc_id'] not in got:
                rows,n=text_layer((root,d));d['pdf_pages']=n
                for row in rows:save(row);pages+=1
    assert pages==sum(int(d['pdf_pages']) for d in docs)
    csvwrite(out/'documents.csv',docs)
    print('Documents',len(docs),'pages',pages)
def arithmetic(out):
    h=defaultdict(dict)
    for r in csvread(out/'ir_hole_headers.csv'):h[r['hole']][r['field']]=r
    results=[]
    for hole,values in sorted(h.items()):
        for k,a,b,c in [('total_depth_minus_bottom_and_penetration','total_depth_mbrf','bottom_felt_mbrf','penetration_m'),('bottom_minus_sea_depth_and_rig_height','bottom_felt_mbrf','water_depth_sea_level_m','rig_floor_above_sea_m')]:
            x,y,z=[values[col]['value_as_extracted'] for col in (a,b,c)]
            delta=Decimal(x)-Decimal(y)-Decimal(z)
            results.append(dict(site=hole[:3],hole=hole,check=k,reported_left_m=x,right_part1_m=y,right_part2_m=z,residual_m=str(delta),status='scan_checked_difference' if abs(delta)>Decimal('.15') else 'within_display_precision',source_url=values[a]['url']))
    csvwrite(out/'ir_depth_checks.csv',results)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('out',type=Path);args=p.parse_args();build(args.root,args.out);arithmetic(args.out)
