"""Build chapter batches in parallel then merge in deterministic order."""
import argparse,csv,gzip,io,shutil,tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from build import generate
def runpart(arg):
    core,base,index,chapters=arg
    out=base/str(index);generate(core,out,chapters);return out
def merge(parts,out):
    for name in ['coverage.csv','segments.csv','field_dictionary.csv.gz','cells.jsonl.gz']:
        compressed=name.endswith('gz');isjson=name.endswith('jsonl.gz')
        target=(gzip.GzipFile(filename=str(out/name),mode='wb',mtime=0) if compressed else (out/name).open('wb'))
        with target:
            for i,part in enumerate(parts):
                src=gzip.open(part/name,'rb') if compressed else (part/name).open('rb')
                with src:
                    if i and not isjson:src.readline()
                    shutil.copyfileobj(src,target)
def main():
    p=argparse.ArgumentParser();p.add_argument('core',type=Path);p.add_argument('output',type=Path);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    with tempfile.TemporaryDirectory(dir=a.output) as tmp:
        base=Path(tmp);ranges=[list(range(n,min(n+4,48))) for n in range(1,48,4)]
        with ProcessPoolExecutor(max_workers=a.workers) as pool:
            parts=list(pool.map(runpart,[(a.core,base,i,ch) for i,ch in enumerate(ranges)]))
        merge(parts,a.output)
if __name__=='__main__':main()
