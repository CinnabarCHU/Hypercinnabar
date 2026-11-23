"""Mirror Leg 138 IR chapter PDFs, the proceedings front matter, and the complete TABLES directory."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request,urlopen
from urllib.parse import quote
from hashlib import sha256
from time import sleep
import csv,os,re
from lxml import html
import fitz
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'primary';C=ROOT/'core'
BASE='https://www-odp.tamu.edu/publications/138_IR/'
DIR='VOLUME/DATA/TABLES/'
def fetch(job):
    rel,role,url=job
    dest=P/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    for k in range(4):
        try:
            if dest.is_file():b=dest.read_bytes()
            else:
                with urlopen(Request(url,headers={'User-Agent':'ODP Leg 138 research collation'}),timeout=70) as f:b=f.read()
            if role=='pdf':
                if not b.startswith(b'%PDF'):raise ValueError('Invalid PDF')
                pages=len(fitz.open(stream=b,filetype='pdf'))
            else:pages=''
            if not dest.exists():tmp=dest.with_suffix(dest.suffix+'.partial');tmp.write_bytes(b);os.replace(tmp,dest)
            return dict(path=rel,role=role,url=url,bytes=len(b),sha256=sha256(b).hexdigest(),pdf_pages=pages)
        except Exception as e:
            if k==3:raise
            sleep(1+k)
def refs(path):
    return html.fromstring(path.read_bytes()).xpath('//a/@href')
def listed(name):
    return not name.startswith(('?','/','../','#')) and name not in ('.','')
def tablejob(path,role):
    return (path,'distribution_filename_map' if path.endswith('/YMTRANS.TBL') else role,BASE+quote(path,safe='/'))
def main():
    jobs=[tablejob('main.htm','publication_index'),(DIR+'index.html','table_directory',BASE+DIR)]
    fetched=list(map(fetch,jobs))
    links=refs(P/'main.htm')
    paths=sorted(set(x for x in links if re.fullmatch(r'VOLUME/CHAPTERS/ir138_\d{2}\.pdf',x,re.I)))
    assert len(paths)==20
    extras=['VOLUME/CHAPTERS/'+s for s in ['138ir.pdf','ir138_panels.pdf','ir138_policy.pdf']]
    jobs=[tablejob(x,'pdf') for x in paths+extras]
    rootrefs=[x for x in refs(P/(DIR+'index.html')) if listed(x)]
    djob=[(DIR+x+'index.html','table_directory',BASE+DIR+x) for x in rootrefs if x.endswith('/')]
    with ThreadPoolExecutor(max_workers=8) as e:fetched+=list(e.map(fetch,djob))
    jobs.extend(tablejob(DIR+x,'disc_table') for x in rootrefs if not x.endswith('/'))
    for rel,_,_ in djob:
        for leaf in refs(P/rel):
            if listed(leaf):
                assert not leaf.endswith('/'),leaf
                jobs.append(tablejob(str(Path(rel).parent/leaf),'disc_table'))
    with ThreadPoolExecutor(max_workers=10) as e:
        for r in e.map(fetch,jobs):fetched.append(r)
    fetched.sort(key=lambda r:r['path'])
    with (C/'sources.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,list(fetched[0]));w.writeheader();w.writerows(fetched)
    print('official objects',len(fetched),'MB',sum(r['bytes'] for r in fetched)/1e6)
if __name__=='__main__':main()
