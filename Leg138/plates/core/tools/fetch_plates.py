"""Fetch the distribution's 11 core-description PDFs, smear-slide tables, back-pocket foldouts and photo PDFs."""
from pathlib import Path
from html.parser import HTMLParser
import argparse,concurrent.futures,csv,hashlib,json,os,re,tempfile,time
from urllib.request import Request,urlopen
from urllib.parse import urljoin
BASE='https://www-odp.tamu.edu/publications/138_IR/'
CD='VOLUME/CORES/IMAGES/'
class Links(HTMLParser):
    def __init__(self):super().__init__();self.targets=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.targets.append(dict(attrs).get('href',''))
def download(dest,path,force=False):
    dest.parent.mkdir(exist_ok=True,parents=True)
    if dest.is_file() and not force:return
    for it in range(4):
        try:
            with urlopen(Request(urljoin(BASE,path),headers={'User-Agent':'Leg138-research-archive/1.0'}),timeout=60) as response:
                fd,name=tempfile.mkstemp(dir=dest.parent,prefix='.fetch_')
                try:
                    with os.fdopen(fd,'wb') as out:
                        while blob:=response.read(1<<19):out.write(blob)
                    if dest.suffix.lower()=='.pdf':
                        with open(name,'rb') as f:
                            if not f.read(100).lstrip().startswith(b'%PDF-'):raise ValueError('Not a PDF')
                    os.replace(name,dest)
                finally:Path(name).unlink(missing_ok=True)
            return
        except Exception:
            if it==3:raise
            time.sleep(1.5*(it+1))
def list_targets(primary):
    path=primary/CD/'index.html'
    download(path,CD)
    links=Links();links.feed(path.read_text('latin1'))
    photos=[]
    for x in links.targets:
        m=re.fullmatch(r'(8\d\d)([A-Z])(\d+)([A-Z])\.pdf',x,re.I)
        if m:photos.append((CD+x,'core_photo',m[1],m[1]+m[2],m[3],m[4]))
    for site in range(844,855):
        for kind,stem in [('core_description_book','cor'),('smear_slide_book','smear')]:
            yield f'VOLUME/CHAPTERS/{stem}_{site:04}.pdf',kind,str(site),'','',''
    for f in ['ir138_f05.pdf','ir138_f10.pdf']:
        yield 'VOLUME/CHAPTERS/'+f,'back_pocket','','','',''
    # Fetch the first B-hole photo of each site first to allow parallel optical QA.
    yield from sorted(photos,key=lambda r:(not bool(re.search(r'B2H\.PDF',r[0],re.I)),int(r[2]),r[3],int(r[4])))
def collect(primary,data,workers):
    import fitz
    tasks=list(list_targets(primary)); print('targets',len(tasks),flush=True)
    failures=[];coll=[]
    def get(task):
        path,kind,site,hole,n,tool=task
        dest=primary/path
        download(dest,path)
        with dest.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
        with fitz.open(dest) as pdf:
            return dict(source_path=path,document_kind=kind,site=site,hole=hole,core_no=n,core_type=tool,url=urljoin(BASE,path),bytes=dest.stat().st_size,sha256=digest,pdf_pages=len(pdf))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as e:
        futures={e.submit(get,t):t for t in tasks}
        for i,f in enumerate(concurrent.futures.as_completed(futures)):
            try:coll.append(f.result())
            except Exception as ex:failures.append((futures[f][0],repr(ex)))
            if i%80==79:print(i+1,'cached',len(coll),'failures',len(failures),flush=True)
    data.mkdir(exist_ok=True,parents=True)
    if coll:
        with (data/'plate_sources.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(coll[0]));w.writeheader();w.writerows(sorted(coll,key=lambda r:r['source_path']))
    (data/'plate_fetch_errors.json').write_text(json.dumps(failures,indent=2))
    print(len(coll),'verified resources',len(failures),'failed',flush=True)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('primary',type=Path);a.add_argument('data',type=Path);a.add_argument('--workers',type=int,default=8);p=a.parse_args();collect(p.primary,p.data,p.workers)
