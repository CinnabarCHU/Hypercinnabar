"""Regenerate the public source registry from the repository's component manifests."""
import argparse
import csv
import gzip
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ['local_path','collection','series','role','site','doc_ids','report_id','report_pdf','book_input',
           'source_release','storage_encoding','directory_snapshot','bytes','sha256','url']


def rows(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path,'rt',encoding='utf-8',newline='') as stream:
        return list(csv.DictReader(stream))


def assemble(root):
    docs = {r['local_source']:r['doc_id'] for r in rows(root/'data/documents.csv')}
    attachments = defaultdict(set)
    for r in rows(root/'ir/core/chapter_items.csv'):
        if r['status']=='foldout_from_official_contents':
            attachments['plates/primary/'+r['pdf_path']].add('IR.C'+str(r['chapter']).zfill(2))
    archive = json.loads((root/'data/source_package_checks.json').read_text(encoding='utf8'))
    registered = {}
    def add(path,collection,series,role,site,source,chapter='',release='1',encoding='identity',extra_docs=()):
        if path in registered:raise ValueError('Duplicate source path '+path)
        doc_ids = set(extra_docs) | attachments[path]
        if path in docs:doc_ids.add(docs[path])
        if chapter:doc_ids.add(f'{series}.C{int(chapter):02d}')
        primary_book_input = path in docs or (series=='IR' and role=='disc_table') or (series=='SR' and role in ('ODP/cd_data','ODP/erratum_ch39_table2'))
        registered[path] = dict(local_path=path,collection=collection,series=series,role=role,site=site,
            doc_ids='|'.join(sorted(doc_ids)),report_id=docs.get(path,''),report_pdf=int(path in docs),book_input=int(primary_book_input),
            source_release=release,storage_encoding=encoding,directory_snapshot=int(source['url'].split('?',1)[0].endswith('/')),
            bytes=int(source['bytes']),sha256=source['sha256'],url=source['url'])
    for r in rows(root/'sppr/core/data/source_manifest.csv'):
        add('sppr/primary/'+r['filename'],'SP_PR_IR',r['doc_id'],'report','',r)
    for r in rows(root/'ir/core/sources.csv'):
        p=r['path']; m=re.search(r'CHAP_(\d+)|ir138_(\d+)\.pdf',p)
        ch=int(next(x for x in m.groups() if x)) if m else 0
        add('ir/primary/'+p,'SP_PR_IR','IR',r['role'],str(ch+835) if 9<=ch<=19 else '',r,ch)
    for e in archive['archives']['SP_PR_IR']['separately_identified_directory_witnesses']:
        if not e['in_module_manifest']:
            add(e['path'],'SP_PR_IR','IR','distribution_directory','',dict(e,url='https://www-odp.tamu.edu/publications/138_IR/VOLUME/DATA/TABLES/'))
    extra_sr={'erratum_ch39_table2':('SR.C39',),'erratum_ch39_notice':('SR.C39',),'erratum_ch01_caption':('SR.C01',),'ch21_fig17_foldout':('SR.C21',)}
    for r in rows(root/'sr/core/source_manifest.csv'):
        add('sr/primary/'+r['source'],'SR','SR',r['channel']+'/'+r['kind'],'',r,r['chapter'],extra_docs=extra_sr.get(r['kind'],()))
    for r in rows(root/'plates/core/data/plate_sources.csv'):
        add('plates/primary/'+r['source_path'],'CORE_PLATES','PLATES',r['document_kind'],r['site'],r)
    for r in rows(root/'plates/core/data/plate_directory_witness.csv'):
        add('plates/primary/'+r['source_path'],'CORE_PLATES','PLATES','distribution_directory','',r)
    disc = {r['path']:r for r in rows(root/'disc/core/file_index.csv.gz')}
    for r in rows(root/'disc/core/sources.csv'):
        e=disc[r['path']]
        add('disc/primary/'+r['path'],'SHIPBOARD_CD','CD',e['family']+'/'+e['record_role'],e['site'],r)
    if len(registered)!=5425:raise ValueError(f'Expected 5425 first-release sources, found {len(registered)}')
    # Each of the nine data editions was actually used in the corresponding chapter apparatus.
    pangaea_chapters={'701308':['SR.C15'],'701312':['SR.C15'],'806757':['SR.C35'],'806678':['SR.C23']}
    for code in ('808116','808118','808119','808121','808122'):pangaea_chapters[code]=['SR.C11','SR.C23']
    for r in rows(root/'sr/core/edition2/data/witnesses.csv'):
        add('sr/core/edition2/'+r['compressed_file'],'SR','SR','PANGAEA/editorial_comparison_witness','',
            dict(url=r['url'],bytes=r['original_bytes'],sha256=r['original_sha256']),release='2',encoding='gzip',extra_docs=pangaea_chapters[r['PANGAEA_id']])
    assert len(registered)==5434 and len(docs)==76 and set(docs)<=set(registered)
    assert sum(r['book_input'] for r in registered.values())==322
    return [registered[k] for k in sorted(registered)]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--out',type=Path,help='Defaults to data/source_inventory.csv.gz under the selected root')
    a=p.parse_args();result=assemble(a.root);out=a.out or a.root/'data/source_inventory.csv.gz'
    with out.open('wb') as target,gzip.GzipFile(filename='',mode='wb',fileobj=target,mtime=0) as zw,io.TextIOWrapper(zw,encoding='utf8',newline='') as stream:
        writer=csv.DictWriter(stream,COLUMNS);writer.writeheader();writer.writerows(result)
    print(f'{len(result)} sources in {out}');print(dict(Counter(r['collection'] for r in result)))

if __name__=='__main__':main()
