from pathlib import Path
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
import hashlib,gzip,csv
E=Path(__file__).resolve().parents[1]
ids=['806757','806678','808116','808118','808119','808121','808122','701308','701312']
def get(doi):
    u=f'https://doi.pangaea.de/10.1594/PANGAEA.{doi}?format=textfile'
    with urlopen(u,timeout=40) as r:
        b=r.read()
    if not b.startswith(b'/*'):raise ValueError(b[:120])
    p=E/'witnesses'/f'PANGAEA.{doi}.txt.gz'
    p.write_bytes(gzip.compress(b,mtime=0))
    return doi,u,len(b),hashlib.sha256(b).hexdigest(),str(p.relative_to(E))
if __name__=='__main__':
    with ThreadPoolExecutor(5) as pool:found=list(pool.map(get,ids))
    with (E/'data/witnesses.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['PANGAEA_id','url','original_bytes','original_sha256','compressed_file']);w.writerows(found)
    print(found)
