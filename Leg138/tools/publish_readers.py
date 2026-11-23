"""Publish compact reading PDFs from the full paired edition, retaining links to source leaves."""
import argparse
import csv
import hashlib
import html
import itertools
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import fitz

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def get_rows(path):
    with path.open(encoding='utf-8-sig',newline='') as stream:
        return list(csv.DictReader(stream))

def compact(job):
    source,out,doc,spans=job
    witness={int(s['edition_witness'])-1:int(s['source_page']) for s in spans}
    source_pdf=source/doc['pdf']
    assert digest(source_pdf)==doc['edition_pdf_sha256'],source_pdf
    target=out/(doc['doc_id']+'.pdf')
    with fitz.open(source_pdf) as full,fitz.open() as reader:
        retained=[i for i in range(len(full)) if i not in witness]
        new={orig:i for i,orig in enumerate(retained)}
        for _,sequence in itertools.groupby(enumerate(retained),lambda t:t[1]-t[0]):
            pages=[n for k,n in sequence]
            reader.insert_pdf(full,from_page=pages[0],to_page=pages[-1],links=False,final=0)
        links=0
        for old,num in new.items():
            page=reader[num]
            for link in full[old].get_links():
                kind=link['kind']
                if kind==fitz.LINK_GOTO:
                    dest=link['page']
                    if dest in witness:
                        info={'kind':fitz.LINK_URI,'from':link['from'],'uri':doc['source_url'].split('#')[0]+f'#page={witness[dest]}'}
                    elif dest in new:
                        info={'kind':kind,'from':link['from'],'page':new[dest],'to':link.get('to',fitz.Point()),'zoom':link.get('zoom',0)}
                    else:raise ValueError((doc['doc_id'],old,dest,'invalid destination'))
                else:
                    info={k:v for k,v in link.items() if k not in ('id','xref')}
                page.insert_link(info);links+=1
        outline=[[lev,title,new[pg-1]+1] for lev,title,pg in full.get_toc() if pg-1 in new]
        if outline:reader.set_toc(outline)
        reader.set_metadata({'title':doc['title'],'subject':'ODP Leg 138 • modern reading pages with numbered publisher links','author':'Leg 138 digital collation; original authors credited in the publication'})
        reader.save(target,garbage=4,deflate=True,no_new_id=True)
        with fitz.open(target) as check:
            assert len(check)==len(full)-len(spans)
            assert len(check.get_toc())==len(outline)
            check_count=sum(len(p.get_links()) for p in check)
            assert check_count==links,(doc['doc_id'],check_count,links)
            for old,num in new.items():
                assert full[old].get_text()==check[num].get_text(),(doc['doc_id'],old,num)
    return dict(doc_id=doc['doc_id'],series=doc['series'],chapter=doc['chapter'],title=doc['title'],source_url=doc['source_url'],source_pages=len(spans),reading_pages=len(new),links=links,local_path=target.name,bytes=target.stat().st_size,sha256=digest(target))

def build(source,out,workers=3,selection=None,keep_archival=False):
    out.mkdir(parents=True,exist_ok=True)
    docs=get_rows(source/'documents.csv');spans=defaultdict(list)
    for row in get_rows(source/'pages.csv'):
        spans[row['doc_id']].append(row)
    archival={}
    if keep_archival:
        for r in get_rows(out/'archival_readers.csv'):
            path=out/r['local_path']
            if digest(path)!=r['sha256']:raise ValueError(f'Archived reader has changed: {path}')
            archival[r['doc_id']]={k:v for k,v in r.items() if k not in ('paired_baseline_sha256','branch_baseline_commit')}
            for k in ('source_pages','reading_pages','links','bytes'):archival[r['doc_id']][k]=int(r[k])
    jobs=[(source,out,d,spans[d['doc_id']]) for d in docs if (not selection or d['doc_id']==selection) and d['doc_id'] not in archival]
    if selection in archival:return [archival[selection]]
    if not jobs:raise ValueError('Unknown document')
    with ProcessPoolExecutor(max_workers=workers) as pool:
        results=list(pool.map(compact,jobs))
    if selection:return results
    if archival:
        bydoc={**archival,**{r['doc_id']:r for r in results}}
        results=[bydoc[d['doc_id']] for d in docs]

    with (out/'catalog.csv').open('w',encoding='utf8',newline='') as s:
        writer=csv.DictWriter(s,results[0]);writer.writeheader();writer.writerows(results)
    sections=[]
    for series in ['SP','PR','IR','SR']:
        lis=[]
        for r in results:
            if r['series']!=series:continue
            version=' · 公开版沿用前次分册，精校版见离线对读本' if r['doc_id'] in archival else ''
            esc=html.escape
            lis.append(f'<li><a href="{esc(r["local_path"])}"><b>{esc(r["doc_id"])}</b> {esc(r["title"])}</a><small>{r["reading_pages"]} 页{version} · <a href="{esc(r["source_url"])}">原刊 {r["source_pages"]} 页</a></small></li>')
        sections.append(f'<section><h2 id="{series}">{series}</h2><ul>'+''.join(lis)+'</ul></section>')
    (out/'index.html').write_text('<!DOCTYPE html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Leg 138 · 分册阅读</title><style>body{font:16px/1.6 system-ui,sans-serif;max-width:62rem;margin:3rem auto;padding:0 1.25rem;color:#20383a}a{color:#165b63}li{margin:.6rem 0}small{display:block;color:#536466}h1,h2{font-family:serif}nav a{margin-right:1.5rem}</style><a href="../../browse.html">返回站点浏览</a><h1>Leg 138 分册阅读</h1><p>分册保留现代正文、已入版的结构化表和对照图。点击页上的原刊链接可核验当时的版式、图表与读数。来源 OCR 与待校单元格带有各自的核读状态。</p><nav>'+''.join(f'<a href="#{s}">{s}</a>' for s in ['SP','PR','IR','SR'])+'</nav>'+''.join(sections)+'</html>',encoding='utf8')
    print('documents',len(results),'pages',sum(r['reading_pages'] for r in results),'bytes',sum(r['bytes'] for r in results),flush=True)
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('full_edition',type=Path);p.add_argument('output_directory',type=Path);p.add_argument('--workers',type=int,default=3);p.add_argument('--doc')
    p.add_argument('--keep-archival',action='store_true',help='Publish newer IR and SR files alongside the two previously public SP and PR readers')
    args=p.parse_args();build(args.full_edition,args.output_directory,args.workers,args.doc,args.keep_archival)
