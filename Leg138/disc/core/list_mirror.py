"""Snapshot the public IR data-directory index (excluding separately catalogued TABLES)."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
from html.parser import HTMLParser
import argparse,base64,csv,gzip,json,hashlib
URL='https://www-odp.tamu.edu/publications/138_IR/VOLUME/DATA/'
class Links(HTMLParser):
    def __init__(self):super().__init__();self.names=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            for k,v in attrs:
                if k=='href' and v and not v.startswith(('?','/','.')):self.names.append(v)
def inventory(directory,snapshot=None):
    url=URL+directory
    if snapshot:raw=(snapshot/directory/'index.html').read_bytes()
    else:
        with urlopen(url,timeout=60) as f:raw=f.read()
    parser=Links();parser.feed(raw.decode('utf-8',errors='replace'))
    return {'directory':directory,'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'html_base64':base64.b64encode(raw).decode()},parser.names
def main():
    p=argparse.ArgumentParser();p.add_argument('destination',type=Path);p.add_argument('--from-snapshot',type=Path);a=p.parse_args()
    a.destination.mkdir(exist_ok=True,parents=True)
    dirs=[''];records=[];files=[]
    with ThreadPoolExecutor(8) as e:
        while dirs:
            further=[]
            for d,(record,names) in zip(dirs,e.map(lambda v:inventory(v,a.from_snapshot),dirs)):
                records.append(record)
                for n in names:
                    if n.endswith('/'):
                        if d+n!='TABLES/':further.append(d+n)
                    else:files.append(d+n)
            dirs=sorted(further)
    with (a.destination/'directory_listings.jsonl.gz').open('wb') as f,gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:
        for r in sorted(records,key=lambda r:r['directory']):z.write((json.dumps(r,separators=(',',':'))+'\n').encode())
    (a.destination/'listed_paths.txt').write_text('\n'.join(sorted(files))+'\n')
    print(len(records),'directory index pages,',len(files),'listed files')
if __name__=='__main__':main()
