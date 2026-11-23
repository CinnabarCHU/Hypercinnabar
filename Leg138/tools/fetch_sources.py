"""Fetch or verify selected Leg 138 source witnesses from the public registry (Python standard library)."""
import argparse
import csv
import gzip
import hashlib
import http.client
import os
import sys
import tempfile
import time
import zlib
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT/'data/source_inventory.csv.gz'
BUFFER = 256*1024
COLLECTIONS = {'SP_PR_IR','SR','CORE_PLATES','SHIPBOARD_CD'}
SERIES = {'SP','PR','IR','CD','PLATES'}
SUMMARY_COLS = ['local_path','status','bytes','sha256','detail']


def read_manifest(path):
    open_text = gzip.open if path.suffix=='.gz' else open
    with open_text(path,'rt',encoding='utf-8',newline='') as stream:
        rows = list(csv.DictReader(stream))
    if len(set(r['local_path'] for r in rows))!=len(rows):raise ValueError('Manifest has duplicate local paths')
    return rows


def select(rows,options):
    cols={c.upper().replace('-','_') for c in options.collection}
    unknown=cols-COLLECTIONS-SERIES
    if unknown:raise ValueError('Unknown collection '+', '.join(sorted(unknown)))
    docs={d.casefold() for d in options.doc};known={r['report_id'].casefold() for r in rows if r['report_id']}
    if docs-known:raise ValueError('Unknown document '+', '.join(sorted(docs-known)))
    found=[]
    for r in rows:
        related = {r['report_id'].casefold()} if options.pdf_only else {x.casefold() for x in r['doc_ids'].split('|')}
        if cols and r['collection'] not in cols and r['series'] not in cols:continue
        if docs and docs.isdisjoint(related):continue
        if options.prefix and not any(r['local_path'].startswith(p) for p in options.prefix):continue
        if options.pdf_only and r['report_pdf']!='1':continue
        if options.book and r['book_input']!='1':continue
        if options.skip_directory_snapshots and r['directory_snapshot']=='1':continue
        found.append(r)
    if not found:raise ValueError('No registered path matches the selection. Paths and prefixes are case-sensitive.')
    return found


def fingerprint(source,out=None):
    sha=hashlib.sha256();size=0
    while chunk:=source.read(BUFFER):
        sha.update(chunk);size+=len(chunk)
        if out is not None:out.write(chunk)
    return size,sha.hexdigest()


def result(r,status,actual=None,detail=''):
    return dict(local_path=r['local_path'],status=status,bytes=actual[0] if actual else '',
                sha256=actual[1] if actual else '',detail=detail)


def mismatch(r,where,actual):
    directory=r['directory_snapshot']=='1';name=('directory_snapshot_changed' if directory else 'source_digest_mismatch')
    detail=f"{where}; expected {r['bytes']} bytes / {r['sha256']}; received {actual[0]} / {actual[1]}"
    if directory:detail+='; the publisher directory listing may have changed since capture'
    return result(r,name,actual,detail)


def check_local(r,path):
    reader = gzip.open if r['storage_encoding']=='gzip' else open
    with reader(path,'rb') as src:actual=fingerprint(src)
    return result(r,'verified',actual) if actual==(int(r['bytes']),r['sha256']) else mismatch(r,'existing local witness',actual)


def install(r,path,timeout):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,temp=tempfile.mkstemp(prefix='.leg138-',suffix='.partial',dir=path.parent);os.close(fd)
    try:
        request=Request(r['url'],headers={'User-Agent':'ODP-Leg-138-source-collation/2','Accept-Encoding':'identity'})
        with urlopen(request,timeout=timeout) as incoming,open(temp,'wb') as output:
            # Some servers or proxies still apply HTTP gzip. Decode transfer content before
            # checking the scientific witness bytes, independent of our local gzip representation.
            encoding=incoming.headers.get('Content-Encoding','identity').strip().lower() or 'identity'
            if encoding not in ('identity','gzip','x-gzip'):raise ValueError('Unexpected HTTP content encoding '+encoding)
            decoder=gzip.GzipFile(fileobj=incoming,mode='rb') if encoding!='identity' else nullcontext(incoming)
            encoder=gzip.GzipFile(filename='',fileobj=output,mode='wb',mtime=0) if r['storage_encoding']=='gzip' else nullcontext(output)
            with decoder as src, encoder as dest:actual=fingerprint(src,dest)
        if actual!=(int(r['bytes']),r['sha256']):return mismatch(r,'download differs; original path left untouched',actual)
        # Publish only a fully verified file and never replace a competing process's copy.
        try:os.link(temp,path)
        except FileExistsError:return check_local(r,path)
        return result(r,'fetched',actual)
    finally:
        Path(temp).unlink(missing_ok=True)


def process(r,root,offline,attempts,timeout):
    try:
        path=(root/r['local_path']).resolve();path.relative_to(root)
        if path.exists():return check_local(r,path)
        if offline:return result(r,'missing',detail='File absent from local source root')
        for attempt in range(attempts):
            try:return install(r,path,timeout)
            except HTTPError as err:
                if err.code not in (408,429,500,502,503,504) or attempt+1==attempts:raise
            except (URLError,TimeoutError,ConnectionError,http.client.HTTPException,EOFError):
                if attempt+1==attempts:raise
            time.sleep(min(2**attempt,4))
    except (OSError,EOFError,ValueError,http.client.HTTPException,zlib.error) as err:
        return result(r,'error',detail=f'{type(err).__name__}: {err}')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=ROOT,help='Leg138 tree to populate or verify; the bundled registry remains the default')
    p.add_argument('--manifest',type=Path,default=INVENTORY,help='Alternative source-inventory CSV or CSV.gz')
    p.add_argument('--collection',action='append',default=[],help='SP_PR_IR, SR, CORE_PLATES or SHIPBOARD_CD (also SP/PR/IR/CD/PLATES). Repeat for a union.')
    p.add_argument('--doc',action='append',default=[],help='A report ID, e.g. IR.C11; includes associated chapter sources. Repeat for a union.')
    p.add_argument('--prefix',action='append',default=[],help='Case-sensitive local-path prefix. Repeat for a union.')
    p.add_argument('--pdf-only',action='store_true',help='Only the indexed main PDFs; --doc selects just that document PDF')
    p.add_argument('--book',action='store_true',help='All 76 report PDFs plus all 246 electronic table witnesses used in the book')
    p.add_argument('--all',action='store_true',help='All 5,434 registered paths (about 1.4 GB)')
    p.add_argument('--list',action='store_true',help='Print selected manifest entries as UTF-8 CSV without access to the network or sources')
    p.add_argument('--verify-only','--offline',dest='offline',action='store_true',help='Verify files under --root without downloading; report missing paths')
    p.add_argument('--skip-directory-snapshots',action='store_true',help='Exclude changeable server-generated directory listing snapshots')
    p.add_argument('--workers',type=int,default=4,help='Maximum concurrent downloads or checks (default 4)')
    p.add_argument('--timeout',type=float,default=60,help='Network timeout in seconds (default 60)')
    p.add_argument('--attempts',type=int,default=3,help='Attempts after transient network failures, including first attempt (default 3)')
    p.add_argument('--report',type=Path,help='Write one CSV result per selected path')
    p.add_argument('--verbose',action='store_true',help='Print successful paths as well as errors')
    a=p.parse_args(argv)
    if not any((a.collection,a.doc,a.prefix,a.pdf_only,a.book,a.all,a.list,a.offline)):p.error('Choose --doc, --collection, --prefix, --pdf-only, --book or --all. Use --list to inspect the registry.')
    if min(a.workers,a.attempts,a.timeout)<=0:p.error('workers, attempts and timeout must be positive')
    try:chosen=select(read_manifest(a.manifest),a)
    except (OSError,ValueError,KeyError) as err:p.error(str(err))
    if a.list:
        w=csv.DictWriter(sys.stdout,chosen[0].keys());w.writeheader();w.writerows(chosen)
        print(f'{len(chosen)} selected',file=sys.stderr);return 0
    root=a.root.resolve();totals=Counter();failed=False
    reportfile=open(a.report,'w',encoding='utf8',newline='') if a.report else nullcontext()
    with reportfile as report, ThreadPoolExecutor(a.workers) as pool:
        writer=csv.DictWriter(report,SUMMARY_COLS) if report is not None else None
        if writer:writer.writeheader()
        for rs in pool.map(lambda r:process(r,root,a.offline,a.attempts,a.timeout),chosen):
            totals[rs['status']]+=1;ok=rs['status'] in ('verified','fetched');failed|=not ok
            if writer:writer.writerow(rs)
            if a.verbose or not ok:print(f"{rs['status']} {rs['local_path']} {rs['detail']}".rstrip(),file=sys.stderr)
    print('Selected '+str(len(chosen))+', '+', '.join(f'{key} {n}' for key,n in sorted(totals.items())),file=sys.stderr)
    return 1 if failed else 0

if __name__=='__main__':raise SystemExit(main())
