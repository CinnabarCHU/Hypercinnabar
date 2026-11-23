"""Partition the all-eligible scan-reading ledger by document for offline review."""
import argparse
import csv
import gzip
import hashlib
import json
import shutil
from contextlib import ExitStack
from collections import Counter
from pathlib import Path

def distribute(src,dest):
    corpus=dest/'corpus';corpus.mkdir(exist_ok=True,parents=True)
    counts={};outputs={}
    with gzip.open(src/'lines.jsonl.gz','rb') as source,ExitStack() as stack:
        for line in source:
            r=json.loads(line);doc=r['doc_id']
            if doc not in outputs:
                raw=stack.enter_context((corpus/(doc+'.jsonl.gz')).open('wb'))
                outputs[doc]=stack.enter_context(gzip.GzipFile(filename='',mode='wb',mtime=0,fileobj=raw))
                counts[doc]=Counter()
            outputs[doc].write(line);counts[doc][r['comparison']]+=1
    records=[]
    for doc,c in counts.items():
        path=corpus/(doc+'.jsonl.gz')
        with path.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
        records.append(dict(doc_id=doc,file='corpus/'+path.name,sha256=sha,bytes=path.stat().st_size,
            eligible_segments=sum(c.values()),agreements=c['literal_agreement'],disagreements=c['disagreement'],empty=c['empty_new_reading']))
    with (dest/'corpus_index.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,records[0]);w.writeheader();w.writerows(records)
    shutil.copyfile(src/'summary.json',dest/'corpus_summary.json')
    shutil.copyfile(src/'page_sample.csv',dest/'corpus_pages.csv')
    return records
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path)
    p.add_argument('out',type=Path,default=Path(__file__).resolve().parent,nargs='?')
    a=p.parse_args();print(len(distribute(a.run,a.out)),'document ledgers')
