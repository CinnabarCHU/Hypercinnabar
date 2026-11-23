"""Addressed readings and figure recipes exposed by the local read-only service."""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'edition2'))
from revisions import readings, checked_lines

def lookup(root,doc,page):
    key=(doc,page)
    proof=readings(root,doc).get(key)
    headers=list(checked_lines(root,doc).get(key,{}).values())
    return dict(visual_collation=proof,checked_lines=headers)

def query(root,name,q,limit,offset,db):
    series=q.get('series','').upper();site=q.get('site','')
    if name=='figure-reproductions':
        with (root/'data/figure_reproduction.csv').open(encoding='utf8',newline='') as f:
            items=[r for r in csv.DictReader(f) if (not q.get('item') or r['item_id']==q['item'])
                   and (not series or r['series']==series) and (not site or site in r['site'].split('|'))
                   and (not q.get('doc') or r['doc_id']==q['doc'])
                   and (not q.get('status') or r['status']==q['status'])]
        return items[offset:offset+limit]
    doc=q.get('doc','');page=int(q['page']) if q.get('page') else None
    texts=readings(root,doc or None);headers=checked_lines(root,doc or None);result=[]
    terms=[w.casefold() for w in re.findall(r'[^\W_]+',q.get('q',''),re.UNICODE)]
    relevant=None
    if site:
        relevant={(r[0],r[1]) for r in db.execute("""SELECT d.doc_id,p.pdf_page FROM documents d
            JOIN pages p USING(doc_id) WHERE d.site=? OR EXISTS (SELECT 1 FROM evidence e
            LEFT JOIN items i ON e.item_id=i.item_id WHERE e.site=? AND e.doc_id=p.doc_id AND
            (e.pdf_page=p.pdf_page OR p.pdf_page BETWEEN i.pdf_page AND i.last_page))""",(site,site))}
    for key in sorted(set(texts)|set(headers)):
        d,n=key
        if (series and d.split('.')[0]!=series) or (page and n!=page) or (relevant is not None and key not in relevant):
            continue
        reading=texts.get(key)
        fields=list(headers.get(key,{}).values())
        text=' '.join([b['text'] for b in reading['blocks']] if reading else []).casefold()+' '+' '.join(r['reading'] for r in fields).casefold()
        if all(term in text for term in terms):
            result.append(dict(doc_id=d,source_page=n,visual_collation=reading,checked_lines=fields))
    return result[offset:offset+limit]
