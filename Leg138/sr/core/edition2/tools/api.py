"""Read-only, local-first review queries. Returns each critical-edition record beside its source locator."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,parse_qs,unquote
import argparse,csv,json

ROOT=Path(__file__).resolve().parents[1]
def load_tab(file):
    with file.open(encoding='utf-8') as f:return list(csv.DictReader(f))

def query(target):
    url=urlsplit(target);path=url.path.strip('/').split('/');f={k:v[0] for k,v in parse_qs(url.query).items()}
    name=path[0] or 'coverage';key=unquote(path[1]) if len(path)==2 else None
    if len(path)>2:raise KeyError(target)
    if name=='coverage':
        if key:return next_or_missing(load_tab(ROOT/'data/chapter_coverage.csv'),key,'chapter')
        return json.loads((ROOT/'data/verification.json').read_text())
    if name=='objects':
        rows=load_tab(ROOT/'data/objects.csv')
        if key:return next_or_missing(rows,key,'item_id')
        return [r for r in rows if r['status']==f.get('status','accepted') and (not f.get('chapter') or r['chapter']==f['chapter']) and (not f.get('kind') or r['kind']==f['kind'])]
    if name=='row-apparatus':
        rows=[json.loads(l) for l in (ROOT/'data/row_apparatus.jsonl').read_text().splitlines()]
        rows=[r for r in rows if (not key or r['dataset_id']==key) and (not f.get('line') or str(r['source_first_line'])==f['line'])]
        if key and not rows:raise KeyError(target)
        return rows
    if name=='print':
        records=load_tab(ROOT/'data/print_datasets.csv')
        if key:
            ds=next_or_missing(records,key,'dataset_id')
            return {'dataset':ds,'rows':load_tab(ROOT/ds['file'])}
        return records
    if name=='rotation-stages' and not key:
        return [r for r in load_tab(ROOT/'data/historical_rotation_stages.csv') if not f.get('site') or r['site']==f['site']]
    if name=='changes' and not key:return load_tab(ROOT/'data/changes.csv')
    raise KeyError(target)
def next_or_missing(rows,key,field):
    for r in rows:
        if r[field]==key:return r
    raise KeyError(key)
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:result=query(self.path);code=200
        except KeyError as exc:result={'error':'No matching review resource','key':str(exc)};code=404
        payload=json.dumps(result,ensure_ascii=False).encode()
        self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('target',nargs='?',default='/coverage');parser.add_argument('--serve',action='store_true');parser.add_argument('--port',type=int,default=1387)
    args=parser.parse_args()
    if args.serve:
        with ThreadingHTTPServer(('127.0.0.1',args.port),Handler) as http:print(f'http://127.0.0.1:{args.port}',flush=True);http.serve_forever()
    else:print(json.dumps(query(args.target),ensure_ascii=False,indent=2))
