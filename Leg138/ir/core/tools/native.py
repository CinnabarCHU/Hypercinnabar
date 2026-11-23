"""Preserve native ASCII tables and curate two cross-site table families with native source locations."""
from pathlib import Path
import csv,gzip,re,json,hashlib
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'primary';C=ROOT/'core'
def write(file,cols,rows):
 with file.open('w',newline='',encoding='utf8') as f:
  w=csv.writer(f);w.writerow(cols);w.writerows(rows)
def member(ch,n):return f'VOLUME/DATA/TABLES/CHAP_{ch}/TABLE.{n}'
def ident(ch,typ,n):return f'IR{ch:02}.{typ}{n:02}'
CARBON=[(14,[18,30,41,52,62,72,83]),(12,[18,30,42,53,64,75,86]),(10,[24,36,48,59,70,82,93]),(10,[28,40,46,56,66,76]),(17,[28,36,44,52,60,69]),(10,[26,39,47,58,70,81]),(16,[24,36,48,60,71]),(12,[24,36,48,60,71]),(13,[22,34,46,58,70]),(10,[20,32,43,54,66]),(9,[20,32,43,54])]
CARB_FIELDS=['depth_mbsf','depth_mcd','total_c_pct','inorganic_c_pct','carbonate_pct','organic_c_pct','nitrogen_pct']
def native():
 catalogue=[];nlines=0
 files=sorted(P.glob('VOLUME/DATA/TABLES/CHAP_*/TABLE.*'),key=lambda p:(int(p.parent.name[5:]),int(p.suffix[1:])))
 with gzip.open(C/'native_lines.csv.gz','wt',encoding='utf8',newline='') as g:
  writer=csv.writer(g);writer.writerow(['item_id','source_path','line_number','raw_text','line_ending','tokens_with_positions'])
  for p in files:
   path=p.relative_to(P).as_posix();ch=int(p.parent.name[5:]);n=int(p.suffix[1:]);id=ident(ch,'T',n)
   b=p.read_bytes();lines=re.findall(rb'([^\r\n]*)(\r\n|\n|\r|$)',b)
   if lines[-1]==(b'',b''):lines.pop()
   assert b''.join(t+e for t,e in lines)==b
   for ln,(t,e) in enumerate(lines,1):
    s=t.decode('latin1')
    tokens=[[m.start(),m.end(),m.group()] for m in re.finditer(r'\S+',s)]
    writer.writerow([id,path,ln,s,{b'\r\n':'CRLF',b'\n':'LF',b'\r':'CR',b'':'none'}[e],json.dumps(tokens,ensure_ascii=False,separators=(',',':'))])
   catalogue.append([id,ch,ch+835 if ch>=9 else '',n,path,len(lines),hashlib.sha256(b).hexdigest()]);nlines+=len(lines)
 write(C/'native_tables.csv',['item_id','chapter','site','table_number','source_path','line_count','sha256'],catalogue)
 return len(files),nlines
def carbon():
 out=[];annual=[]
 for ch,(n,centers) in enumerate(CARBON,9):
  path=member(ch,n);ls=(P/path).read_text(encoding='latin1').splitlines();hole=''
  fields=CARB_FIELDS[:{7:7,6:6,5:0,4:0}[len(centers)]] if len(centers)>=6 else ['depth_mbsf','depth_mcd','inorganic_c_pct','carbonate_pct']+(['organic_c_pct'] if len(centers)==5 else [])
  assert len(centers)==len(fields)
  base=len(out)
  for ln,s in enumerate(ls,1):
   if m:=re.fullmatch(r'\s*(?:138-|-)?(\d{3})-?([A-E])\s*-?\s*',s):hole=''.join(m.groups());continue
   if not re.match(r'^\s*(?:(?:138-)?\d{3}-?[A-E]-)?\d+[A-Z]+[-]?(?:\d|CC)',s):continue
   tokens=list(re.finditer(r'\S+',s))
   sample=' '.join(w.group() for w in tokens[:2])
   if m:=re.match(r'(?:138-)?(\d{3})-?([A-E])-',sample):hole=''.join(m.groups())
   d={}
   for w in tokens[2:]:
    x=(w.start()+w.end())/2
    k=min(range(len(centers)),key=lambda i:abs(centers[i]-x))
    assert abs(centers[k]-x)<=4.5,(ch,ln,w.group(),x,d)
    if fields[k] in d:
     assert d[fields[k]]=='a' and fields[k]=='organic_c_pct',(ch,ln,d)
     d[fields[k]]+=' '+w.group()
    else:d[fields[k]]=w.group()
   assert hole and d.get('depth_mbsf') and d.get('depth_mcd'),(ch,ln,s)
   out.append([ident(ch,'T',n),str(ch+835),path,ln,hole,sample,*[d.get(k,'') for k in CARB_FIELDS]])
  annual.append([ch+835,len(out)-base])
 write(C/'tables/carbons.csv',['item_id','site','source_path','source_line','reported_hole','sample_label',*CARB_FIELDS],out)
 return len(out),annual
def coring():
 out=[];counts=[]
 for ch in range(9,20):
  path=member(ch,1);id=ident(ch,'T',1);site=ch+835
  ls=(P/path).read_text(encoding='latin1').splitlines()
  datehead=next((m[1] for s in ls if (m:=re.search(r'(May 1991|June 1991)',s,re.I))),'')
  hole='';group=1;cores=0
  for ln,s in enumerate(ls,1):
   if m:=re.search(rf'({site})([A-E])',s):hole=''.join(m.groups())
   a=s.split()
   if len(a)==7 and re.fullmatch(r'(?:138-\d{3}[A-E]-)?\d+[A-Z]',a[0]):
    assert hole,(ch,ln)
    out.append([id,site,path,ln,'core',group,hole,datehead,*a]);cores+=1
   elif s.lower().lstrip().startswith('coring totals'):
    assert len(a)==5,(ch,ln,s)
    out.append([id,site,path,ln,'hole_total',group,hole,datehead,'','','','',*a[2:]])
    group+=1
  counts.append([site,cores,group-1])
 write(C/'tables/coring.csv',['item_id','site','source_path','source_line','row_kind','source_group','reported_hole','printed_date_header','core_label','day','utc_time','depth_range_mbsf','length_cored_m','length_recovered_m','recovery_pct'],out)
 return len(out),counts
if __name__=='__main__':
 print('native',native());print('carbon',carbon());print('coring',coring())
