"""Serve the offline reader and a local, read-only JSON/CSV API."""
import argparse
import csv
import gzip
import io
import json
import mimetypes
import re
import sqlite3
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from itertools import islice
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
from edition2_api import NAMES as V2_ENDPOINTS, retrieve, find_named, matches_site

def list_rows(db,sql,params=()):
    return [dict(r) for r in db.execute(sql,params)]

def page(q):
    limit=int(q.get('limit','100'));offset=int(q.get('offset','0'))
    if not 1<=limit<=1000 or offset<0:raise ValueError('limit must be 1–1000 and offset nonnegative')
    return limit,offset

def endpoint(db,root,name,q):
    limit,offset=page(q);site=q.get('site','');series=q.get('series','').upper()
    allowed_sites={str(i) for i in range(844,855)}
    if name=='rotation-stages' or (name=='rows' and q.get('dataset') in ('SR.E2.HISTORICAL_ROTATION_STAGES','SR.C01.TABLE1.PRINT.E2')):
        allowed_sites.update(('84','495','503','677'))
    if name=='sr-apparatus' or (name=='rows' and q.get('dataset')=='SR.C15.TABLE9'):allowed_sites.add('677')
    if site and site not in allowed_sites:raise ValueError('Unsupported site for this endpoint')
    v2_ready=db.execute("SELECT 1 FROM sqlite_master WHERE name='item_reviews' AND type='table'").fetchone() is not None
    if not v2_ready and (name in V2_ENDPOINTS or (name=='rows' and q.get('item') and not q.get('dataset'))):
        raise ValueError('Rebuild the second-edition catalogue to use this endpoint')
    if name=='rotation-stages':
        return endpoint(db,root,'rows',{**q,'dataset':'SR.E2.HISTORICAL_ROTATION_STAGES'})
    if name in V2_ENDPOINTS:return retrieve(db,name,q,limit,offset)
    if name=='sites':
        raw=list_rows(db,'SELECT * FROM sites WHERE (?="" OR site=?) ORDER BY site',(site,site))
        return [json.loads(r['record_json']) for r in raw]
    if name=='plans':
        return [json.loads(r[0]) for r in db.execute('SELECT record_json FROM plans ORDER BY proposed_site')]
    if name=='documents':
        return list_rows(db,'SELECT * FROM documents WHERE (?="" OR series=?) ORDER BY series,chapter LIMIT ? OFFSET ?',(series,series,limit,offset))
    if name=='sources':
        # Cross-site SR sources are located through publication evidence or explicit dataset records.
        sql="""SELECT a.* FROM assets a WHERE (?='' OR a.series=?) AND (?='' OR a.local_path=?) AND
            (?='' OR a.site=? OR EXISTS (SELECT 1 FROM evidence e WHERE e.site=? AND e.source_path=a.local_path))
            ORDER BY a.local_path LIMIT ? OFFSET ?"""
        return list_rows(db,sql,(series,series,q.get('path',''),q.get('path',''),site,site,site,limit,offset))
    if name=='items':
        item=q.get('item','');status=q.get('review_status','');kind=q.get('kind','')
        if not v2_ready:
            if status:return []
            return list_rows(db,"""SELECT i.*,d.url AS document_url FROM items i JOIN documents d USING(doc_id)
                WHERE (?='' OR d.series=?) AND (?='' OR EXISTS(SELECT 1 FROM evidence e WHERE e.item_id=i.item_id AND e.site=?))
                AND (?='' OR i.kind=?) AND (?='' OR i.item_id=?) ORDER BY i.doc_id,i.pdf_page,i.item_id LIMIT ? OFFSET ?""",
                (series,series,site,site,kind,kind,item,item,limit,offset))
        sql="""SELECT i.*,d.url AS document_url,r.state AS review_state,r.review_basis,r.source_path AS reviewed_source_path
            FROM items i JOIN documents d USING(doc_id) LEFT JOIN item_reviews r USING(item_id)
            WHERE (?='' OR d.series=?) AND (?='' OR EXISTS (SELECT 1 FROM evidence e WHERE e.site=? AND e.item_id=i.item_id))
            AND (?='' OR i.kind=?) AND (?='' OR i.item_id=?) AND (?='' OR r.state=?)
            ORDER BY i.doc_id,i.pdf_page,i.item_id LIMIT ? OFFSET ?"""
        return list_rows(db,sql,(series,series,site,site,kind,kind,item,item,status,status,limit,offset))
    if name=='fields':
        return list_rows(db,"SELECT * FROM field_notes WHERE (?='' OR dataset_id=?) ORDER BY rowid LIMIT ? OFFSET ?",(q.get('dataset',''),q.get('dataset',''),limit,offset))
    if name=='evidence':
        return list_rows(db,"""SELECT * FROM evidence WHERE (?='' OR site=?) AND (?='' OR role=?) AND (?='' OR item_id=?)
           ORDER BY id LIMIT ? OFFSET ?""",(site,site,q.get('role',''),q.get('role',''),q.get('item',''),q.get('item',''),limit,offset))
    if name=='datasets':
        item=q.get('item','')
        records=list_rows(db,"""SELECT d.* FROM datasets d WHERE (?='' OR series=?) AND
           (?='' OR EXISTS (SELECT 1 FROM dataset_items m WHERE m.dataset_id=d.dataset_id AND m.item_id=?))
           ORDER BY dataset_id LIMIT ? OFFSET ?""",(series,series,item,item,limit,offset))
        for r in records:r['fields']=json.loads(r.pop('fields_json') or '[]')
        return records
    if name=='page':
        return list_rows(db,"""SELECT p.doc_id,p.pdf_page,p.printed_page,p.basis,p.text,d.url,d.local_source
            FROM pages p JOIN documents d USING(doc_id) WHERE p.doc_id=? AND p.pdf_page=?""",(q.get('doc',''),int(q.get('page','1'))))
    if name=='search':
        words=re.findall(r'[^\W_]+',q.get('q',''),re.UNICODE)
        if not words:raise ValueError('q must contain at least one search term')
        term=' AND '.join('"'+w+'"' for w in words[:24])
        if series=='PLATES':
            return list_rows(db,"""SELECT p.local_source,p.url,p.kind,p.site,p.pdf_page,snippet(plate_fts,0,'[',']',' … ',20) AS excerpt
                FROM plate_fts JOIN plate_pages p ON plate_fts.rowid=p.id WHERE plate_fts MATCH ?
                AND (?='' OR p.site=?) ORDER BY rank LIMIT ? OFFSET ?""",(term,site,site,limit,offset))
        return list_rows(db,"""SELECT p.doc_id,p.pdf_page,p.printed_page,d.url,d.local_source,snippet(page_fts,0,'[',']',' … ',20) AS excerpt
            FROM page_fts JOIN pages p ON page_fts.rowid=p.id JOIN documents d ON d.doc_id=p.doc_id WHERE page_fts MATCH ?
            AND (?='' OR d.series=?) AND (?='' OR d.site=? OR EXISTS
                (SELECT 1 FROM evidence e LEFT JOIN items i ON i.item_id=e.item_id
                 WHERE e.site=? AND e.doc_id=p.doc_id AND (e.pdf_page=p.pdf_page OR p.pdf_page BETWEEN i.pdf_page AND i.last_page)))
            ORDER BY rank LIMIT ? OFFSET ?""",(term,series,series,site,site,site,limit,offset))
    if name!='rows':raise KeyError('Unknown endpoint')
    ident=q.get('dataset','');item=q.get('item','')
    if item and not ident:return find_named(db,item,site,limit,offset)
    if item and not db.execute('SELECT 1 FROM dataset_items WHERE item_id=? AND dataset_id=?',(item,ident)).fetchone():return []
    d=db.execute('SELECT * FROM datasets WHERE dataset_id=?',(ident,)).fetchone()
    if d is None:raise KeyError('Unknown dataset')
    if site and d['scope_site'] and site!=d['scope_site']:return []
    if d['storage']=='sr_print_slots':return retrieve(db,'sr-table-rows',{**q,'item':d['item_id']},limit,offset)
    if d['storage']=='ir_print_rows':return find_named(db,d['item_id'],site,limit,offset)
    if d['storage']=='native_ir':
        return list_rows(db,"""SELECT item_id,line_number,source_path,raw_text,line_ending,tokens_with_positions
           FROM native_ir WHERE item_id=? AND (?='' OR ?=?) ORDER BY line_number LIMIT ? OFFSET ?""",(d['item_id'],site,site,d['scope_site'],limit,offset))
    if d['storage']=='sr_rows':
        fields=json.loads(d['fields_json']);result=[]
        source=db.execute('SELECT url FROM assets WHERE local_path=?',(d['source_path'],)).fetchone()
        records=db.execute("""SELECT * FROM sr_rows WHERE dataset_id=? AND (?='' OR instr(sites,?)>0)
            ORDER BY record_no LIMIT ? OFFSET ?""",(ident,site,'|'+site+'|',limit,offset))
        for row in records:
            vals=json.loads(row['values_json'])
            entry=dict(dataset_id=ident,source_path=d['source_path'],source_url=source[0] if source else None,record_no=row['record_no'],first_line=row['line_first'],last_line=row['line_last'],sites=row['sites'].strip('|'),values=dict(zip(fields,vals)) if isinstance(vals,list) and len(vals)==len(fields) else vals)
            entry.update(json.loads(row['raw_json']))
            apparatus=db.execute('SELECT record_json FROM sr_apparatus WHERE dataset_id=? AND record_no=?',(ident,row['record_no'])).fetchone() if v2_ready else None
            if apparatus:entry['editorial_review']=json.loads(apparatus[0])
            result.append(entry)
        return result
    path=root/d['local_path']
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt',encoding='utf-8-sig',newline='') as stream:
        data=csv.DictReader(stream)
        if item and 'item_id' in (data.fieldnames or []):data=(r for r in data if r.get('item_id')==item)
        if site and d['dataset_id']=='IR.EDITORIAL_NOTES':
            data=(r for r in data if r['item_id'].startswith(f'IR{int(site)-835:02d}.'))
        elif site and d['scope_site']!=site:
            data=(r for r in data if r.get('site')==site or matches_site(r,site))
        return list(islice(data,offset,offset+limit))

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path=urlsplit(self.path)
        if path.path=='/':
            self.send_response(302);self.send_header('Location','/browse.html');self.end_headers();return
        if not path.path.startswith('/api/'):
            return super().do_GET()
        q={k:v[-1] for k,v in parse_qs(path.query).items()};root=Path(self.directory)
        if path.path=='/api/geography':q.setdefault('limit','1000')
        try:
            with sqlite3.connect((root/'Leg138.sqlite').as_uri()+'?mode=ro',uri=True) as db:
                db.row_factory=sqlite3.Row
                records=endpoint(db,root,path.path[5:],q)
                geo_meta=json.loads(db.execute('SELECT metadata_json FROM geography_metadata').fetchone()[0]) if path.path=='/api/geography' and q.get('format','geojson')=='geojson' else None
            if geo_meta is not None:
                body=json.dumps({**geo_meta,'features':records},ensure_ascii=False).encode();typ='application/geo+json; charset=utf-8'
            elif q.get('format')=='csv':
                if path.path in ('/api/rows','/api/item-rows'):
                    for r in records:
                        if isinstance(r.get('values'),dict):
                            values=r.pop('values')
                            for k,v in values.items():
                                r[k if k not in r else 'value_'+k]=v
                f=io.StringIO();keys=list(dict.fromkeys(k for row in records for k in row))
                w=csv.DictWriter(f,keys);w.writeheader()
                for r in records:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})
                body=f.getvalue().encode();typ='text/csv; charset=utf-8'
            else:
                payload={'count':len(records),'limit':page(q)[0],'offset':page(q)[1],'records':records}
                body=json.dumps(payload,ensure_ascii=False).encode();typ='application/json; charset=utf-8'
            status=200
        except (ValueError,KeyError) as exc:
            status=400;typ='application/json; charset=utf-8';body=json.dumps({'error':str(exc)}).encode()
        self.send_response(status);self.send_header('Content-Type',typ);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--port',type=int,default=8138)
    a=parser.parse_args();http=ThreadingHTTPServer(('127.0.0.1',a.port),partial(Handler,directory=str(a.root.resolve())))
    print(f'http://127.0.0.1:{a.port}/browse.html',flush=True)
    http.serve_forever()
