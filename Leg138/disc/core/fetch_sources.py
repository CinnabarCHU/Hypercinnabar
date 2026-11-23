"""Acquire any selected archived source files by digest; no dependency on a directory server listing."""
import argparse,csv,hashlib,os,tempfile,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen
def verify(p,row):
    with p.open('rb') as f:return p.stat().st_size==int(row['bytes']) and hashlib.file_digest(f,'sha256').hexdigest()==row['sha256']
def obtain(job):
    root,row=job;target=root/row['path']
    if target.is_file():
        if not verify(target,row):raise RuntimeError('Different local bytes: '+row['path'])
        return row['path']
    target.parent.mkdir(parents=True,exist_ok=True)
    for attempt in range(3):
        fd,path=tempfile.mkstemp(dir=target.parent);path=Path(path)
        try:
            with os.fdopen(fd,'wb') as f,urlopen(row['url'],timeout=90) as src:
                while data:=src.read(1<<20):f.write(data)
            if not verify(path,row):raise ValueError('Different distributed bytes: '+row['path'])
            os.replace(path,target);return row['path']
        except (OSError,TimeoutError):
            if attempt==2:raise
            time.sleep(1+attempt)
        finally:path.unlink(missing_ok=True)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path);p.add_argument('--prefix',default='');p.add_argument('--workers',default=6,type=int);p.add_argument('--verify-only',action='store_true');args=p.parse_args()
    with Path(__file__).with_name('sources.csv').open() as f:rs=[r for r in csv.DictReader(f) if r['path'].startswith(args.prefix)]
    if not rs:p.error('No registered files for prefix')
    if args.verify_only:
        for r in rs:
            if not verify(args.primary/r['path'],r):raise ValueError('Checksum differs: '+r['path'])
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:list(pool.map(obtain,((args.primary,r) for r in rs)))
    print('Verified',len(rs),'files.')
if __name__=='__main__':main()
