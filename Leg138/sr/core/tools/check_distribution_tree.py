"""Compare the public publisher file listing to this harvest and retain the empty directories."""
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
from urllib.parse import urljoin, unquote
import csv
from pathlib import Path
from lxml.html import fromstring

ROOT=Path(__file__).resolve().parents[1]
PUBLISHER='https://www-odp.tamu.edu/publications/138_SR/'
def directory(url):
    with urlopen(url,timeout=30) as request:
        links=fromstring(request.read()).xpath('//a/@href')
    return url,sorted(h for h in links if not h.startswith(('/','?','#','..')))
def run():
    manifest={r['url']:r['source'] for r in csv.DictReader((ROOT/'source_manifest.csv').open())}
    todo=[urljoin(PUBLISHER,'VOLUME/DATA/'),urljoin(PUBLISHER,'VOLUME/CHAPTERS/')]
    rows=[]
    with ThreadPoolExecutor(6) as pool:
        while todo:
            results=pool.map(directory,todo);todo=[]
            for base,links in results:
                rows.append((base,'directory',len(links),''))
                for path in links:
                    target=urljoin(base,path)
                    if target.endswith('/'):
                        todo.append(target)
                    else:
                        rows.append((target,'file','',manifest.get(target,manifest.get(unquote(target),''))))
    output=ROOT/'distribution_tree.csv'
    with output.open('w',newline='') as file:
        writer=csv.writer(file);writer.writerow(['url','entry_type','children','manifest_source'])
        writer.writerows(sorted(rows))
    print('directories, listed files, unmatched',sum(r[1]=='directory' for r in rows),sum(r[1]=='file' for r in rows),[r for r in rows if r[1]=='file' and not r[3]])
if __name__=='__main__':run()
