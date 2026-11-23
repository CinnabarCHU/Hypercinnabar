"""Local read-only catalogue and HTTP/JSON API; no external packages."""
import argparse
import csv
import io
import json
import mimetypes
import shutil
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlsplit

ROOT=Path(__file__).resolve().parent

def source_info(con,key):
    r=dict(con.execute("SELECT * FROM sources WHERE source=?",(key,)).fetchone())
    r["local_url"]="/sources/"+quote(key,safe="/") if (Handler.source_root/key).is_file() else ""
    return r

class Handler(BaseHTTPRequestHandler):
    source_root=ROOT.parent/"sources"
    def send(self,body,typ,status=200):
        if isinstance(body,str):body=body.encode("utf-8")
        self.send_response(status);self.send_header("Content-Type",typ);self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    def packet(self,data,status=200):
        self.send(json.dumps(data,ensure_ascii=False),"application/json; charset=utf-8",status)
    def do_GET(self):
        parts=urlsplit(self.path);path=unquote(parts.path);q={k:v[-1] for k,v in parse_qs(parts.query).items()}
        with sqlite3.connect((ROOT/"Site846_SR.sqlite").as_uri()+"?mode=ro",uri=True) as con:
            con.row_factory=sqlite3.Row
            try:self.dispatch(con,path,q)
            except (ValueError,KeyError) as exc:self.packet({"error":str(exc)},400)
            except (BrokenPipeError,ConnectionResetError):pass
    def dispatch(self,con,path,q):
        if path=="/":
            return self.send((ROOT/"index.html").read_bytes(),"text/html; charset=utf-8")
        if path.startswith("/sources/"):
            key=path.removeprefix("/sources/")
            if not con.execute("SELECT 1 FROM sources WHERE source=?",(key,)).fetchone():return self.packet({"error":"unknown source"},404)
            file=self.source_root/key
            if not file.is_file():return self.packet({"error":"Original file is in the companion archive.","source":source_info(con,key)},404)
            self.send_response(200);self.send_header("Content-Type",mimetypes.guess_type(file.name)[0] or "application/octet-stream");self.send_header("Content-Length",str(file.stat().st_size));self.end_headers()
            with file.open('rb') as f:shutil.copyfileobj(f,self.wfile)
            return
        if path=="/figure.pdf":return self.send((ROOT/"proofs/Chapter27_Figure3_Comparison.pdf").read_bytes(),"application/pdf")
        if path=="/api":return self.packet({"chapters":"/api/chapters","items":"/api/items?chapter=27","datasets":"/api/datasets?item=c27_t1","rows":"/api/rows/c27_t1_print?limit=10&offset=0&q=C4-1","record":"/api/row/c27_t1_print/171","reviews":"/api/reviews?chapter=27&page=608&field=sst_c","relations":"/api/relations?item=c15_t5","export":"/csv/c27_t1_print"})
        if path=="/api/chapters":
            return self.packet([dict(r) for r in con.execute("SELECT * FROM chapters ORDER BY chapter")])
        if path=="/api/items":
            sel="SELECT i.*, c.url AS pdf_url,c.source AS pdf_source FROM items i JOIN chapters c USING(chapter)"
            args=()
            if "chapter" in q:sel+=" WHERE i.chapter=?";args=(int(q["chapter"]),)
            records=[]
            for r in con.execute(sel+" ORDER BY i.chapter, i.page_from, i.kind, i.item",args):
                item=dict(r);src=source_info(con,item['pdf_source']);item["pdf"]=(src["local_url"] or src["url"])+"#page="+str(item["pdf_page_from"])
                item['assets']=[{"source":a[0],"role":a[1],"url":(s["local_url"] or s["url"])} for a in con.execute("SELECT source,role FROM assets WHERE item=?",(item['item'],)) for s in [source_info(con,a[0])]];records.append(item)
            return self.packet(records)
        if path=="/api/datasets":
            sql="SELECT * FROM catalogue";values=()
            if "item" in q:sql+=" WHERE item=?";values=(q["item"],)
            return self.packet([dict(r) for r in con.execute(sql+" ORDER BY chapter,item,edition,dataset",values)])
        if path=="/api/relations":
            return self.packet([dict(r) for r in con.execute("SELECT * FROM relations WHERE child=? OR parent=?" if "item" in q else "SELECT * FROM relations", (q["item"],q["item"]) if "item" in q else ())])
        if path=="/api/reviews":
            terms=[];params=[]
            for field in ("chapter","page","field","printed_row"):
                if field in q:terms.append(field+"=?");params.append(q[field])
            stmt="SELECT * FROM cell_reviews"+(" WHERE "+" AND ".join(terms) if terms else "")
            return self.packet([dict(r) for r in con.execute(stmt,params)])
        tokens=path.strip("/").split("/")
        mode=tokens[1] if len(tokens)>=3 and tokens[0]=="api" else "csv" if len(tokens)==2 and tokens[0]=="csv" else None
        if mode not in ("rows","row","csv"):return self.packet({"error":"route not found"},404)
        key=tokens[1] if mode=="csv" else tokens[2]
        meta=con.execute("SELECT * FROM catalogue WHERE dataset=?",(key,)).fetchone()
        if meta is None:return self.packet({"error":"unknown dataset"},404)
        fields=[dict(r) for r in con.execute("SELECT f.field,n.label,n.unit,n.role FROM fields f JOIN field_notes n USING(dataset,field) WHERE f.dataset=? ORDER BY f.position",(key,))]
        src=source_info(con,meta["source"]);sql=' FROM "'+key+'"';values=[]
        if mode=="row":
            if len(tokens)!=4:raise ValueError("row number required")
            sql+=" WHERE row_no=?";values.append(int(tokens[3]))
        elif q.get("q"):
            field_names=["raw_literal",*[f["field"] for f in fields]]
            sql += " WHERE " + " OR ".join('instr(lower("' + n + '"), lower(?)) > 0' for n in field_names)
            values=[q["q"]]*len(field_names)
        if mode=="csv":
            out=io.StringIO();w=csv.writer(out);rs=con.execute("SELECT *"+sql+" ORDER BY row_no",values)
            w.writerow([c[0] for c in rs.description]);w.writerows(rs);return self.send(out.getvalue(),"text/csv; charset=utf-8")
        total=con.execute("SELECT count(*)"+sql,values).fetchone()[0]
        if mode=="row" and not total:return self.packet({"error":"row not found"},404)
        offset=max(0,int(q.get("offset",0)));limit=max(1,min(500,int(q.get("limit",30))))
        rows=[dict(r) for r in con.execute("SELECT *"+sql+" ORDER BY row_no LIMIT ? OFFSET ?",[*values,limit,offset])]
        for r in rows:
            link=src["local_url"] or src["url"]
            if r["print_page"]:
                pos=con.execute("SELECT page_from,pdf_page_from FROM items WHERE item=?",(meta["item"],)).fetchone();link+="#page="+str(r["print_page"]-pos[0]+pos[1])
            r["source_url"]=link
        return self.packet({"dataset":dict(meta),"source":src,"fields":fields,"total":total,"offset":offset,"rows":rows})

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--port",type=int,default=8460);ap.add_argument("--sources",type=Path)
    args=ap.parse_args()
    if args.sources:Handler.source_root=args.sources.resolve()
    elif (ROOT/"sources").is_dir():Handler.source_root=ROOT/"sources"
    print(f"Site 846 SR at http://127.0.0.1:{args.port}/",flush=True)
    ThreadingHTTPServer(("127.0.0.1",args.port),Handler).serve_forever()
