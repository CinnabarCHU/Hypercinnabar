"""Replace one chapter in the shared SR reader index, preserving every other one."""
import csv
import fcntl
import io
import json
import os
import tempfile

def atomic_text(path, text):
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",dir=path.parent,delete=False) as tmp:
        tmp.write(text)
    os.chmod(tmp.name,0o644)
    os.replace(tmp.name,path)

def update_register(directory, doc_id, records, inventory):
    def ordered(items):
        return sorted(items,key=lambda r:(r["doc_id"],int(r["source_page"])))
    fd=os.open(directory,os.O_RDONLY)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX)
        path=directory/"pages.jsonl"
        existing=[json.loads(s) for s in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []
        combined=ordered([r for r in existing if r["doc_id"]!=doc_id]+records)
        atomic_text(path,"".join(json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n" for r in combined))
        path=directory/"pages.csv"
        if path.exists():
            with path.open(encoding="utf-8") as stream:
                existing=list(csv.DictReader(stream))
        else:
            existing=[]
        stream=io.StringIO(newline="")
        writer=csv.DictWriter(stream,fieldnames=list(inventory[0]),lineterminator="\n")
        writer.writeheader()
        writer.writerows(ordered([r for r in existing if r["doc_id"]!=doc_id]+inventory))
        atomic_text(path,stream.getvalue())
    finally:
        os.close(fd)
