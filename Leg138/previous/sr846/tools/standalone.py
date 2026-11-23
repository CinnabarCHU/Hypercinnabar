"""Make the self-contained browser edition using Python's standard library."""
import argparse
import base64
import gzip
import json
import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def pack(obj):
    raw=json.dumps(obj,ensure_ascii=False,separators=(",",":")).encode()
    return base64.b64encode(gzip.compress(raw,compresslevel=7,mtime=0)).decode()
def main(out):
    with sqlite3.connect(ROOT/"Site846_SR.sqlite") as db:
        db.row_factory=sqlite3.Row
        def allof(sql,params=()):return [dict(r) for r in db.execute(sql,params)]
        sources={s['source']:s for s in allof('SELECT * FROM sources')}
        metadata={"sources":sources,"chapters":allof("SELECT * FROM chapters ORDER BY chapter"),
                  "datasets":allof("SELECT * FROM catalogue ORDER BY chapter,item,edition,dataset"),
                  "items":allof("SELECT * FROM items ORDER BY chapter,page_from,kind,item"),
                  "reviews":allof("SELECT * FROM cell_reviews"),"relations":allof("SELECT * FROM relations"),"fields":{}}
        ch={r["chapter"]:r for r in metadata["chapters"]}
        for r in metadata["items"]:
            s=ch[r["chapter"]];r["pdf_source"]=s["source"];r["pdf_url"]=s["url"];r["pdf"]=s["url"]+"#page="+str(r["pdf_page_from"])
            r["assets"]=allof("SELECT a.source,a.role,s.url FROM assets a JOIN sources s ON s.source=a.source WHERE item=?",(r['item'],))
        blobs={}
        for d in metadata["datasets"]:
            key=d["dataset"];metadata["fields"][key]=allof("SELECT f.field,n.label,n.unit,n.role FROM fields f JOIN field_notes n USING(dataset,field) WHERE f.dataset=? ORDER BY f.position",(key,))
            blobs[key]=pack([list(r) for r in db.execute('SELECT * FROM "'+key+'" ORDER BY row_no')])
        blobs["metadata"]=pack(metadata)
        blobs["figure"]=base64.b64encode((ROOT/"proofs/Chapter27_Figure3_Comparison.pdf").read_bytes()).decode()
    html=(ROOT/"index.html").read_text()
    original="const get=async path=>{const res=await fetch(path);if(!res.ok)throw Error(await res.text());return res.json()};"
    assert original in html
    html=html.replace(original,"const get=archiveGet;")
    tag="<script>\nconst el="
    html=html.replace(tag,'<script type="application/json" id="archive-pack">'+json.dumps(blobs,separators=(",",":"))+'</script>\n<script>\n'+(ROOT/"tools/offline.js").read_text()+'\nconst el=')
    assert "const archivePack=" in html
    out.write_text(html)
if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--out",type=Path,default=ROOT/"Site846_SR.html");main(ap.parse_args().out)
