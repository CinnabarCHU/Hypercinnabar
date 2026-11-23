"""Fetch one registered digital source, checking its length and SHA-256 before installation."""
import argparse
import hashlib
import os
import sqlite3
import tempfile
from pathlib import Path
from urllib.request import Request,urlopen

def fetch(root,key):
    with sqlite3.connect(root/'Leg138.sqlite') as db:
        row=db.execute('SELECT bytes,sha256,url FROM assets WHERE local_path=?',(key,)).fetchone()
    if not row:raise ValueError('No source registered with that exact path')
    size,sha,url=row
    dest=(root/key).resolve();dest.relative_to(root.resolve())
    if dest.is_file():
        if dest.stat().st_size==size and hashlib.sha256(dest.read_bytes()).hexdigest()==sha:return dest
        raise ValueError('The existing local copy has different bytes; preserve it as a separate witness before importing this one')
    dest.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=dest.parent)
    try:
        digest=hashlib.sha256();total=0
        request=Request(url,headers={'User-Agent':'ODP Leg 138 source archive'})
        with os.fdopen(fd,'wb') as out,urlopen(request,timeout=90) as incoming:
            while chunk:=incoming.read(1048576):
                out.write(chunk);digest.update(chunk);total+=len(chunk)
        if (total,digest.hexdigest())!=(size,sha):raise ValueError('The response differs from the registered digital witness')
        os.replace(tmp,dest)
    finally:
        Path(tmp).unlink(missing_ok=True)
    return dest

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('local_path');p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    print(fetch(a.root,a.local_path))
