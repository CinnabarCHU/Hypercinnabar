"""Reconstruct SP and PR collation privately from authenticated published PDFs."""
import json
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=4)
def plan_readings(root, doc_id, stat_key):
    # stat_key refreshes cached readings when the user replaces the source.
    with tempfile.TemporaryDirectory() as folder:
        out=Path(folder)
        subprocess.run([sys.executable,str(root/'revision/text_sp/build.py'),str(root/'sppr/primary'),
                        '--doc',doc_id,'--out',str(out)],check=True,stdout=subprocess.DEVNULL)
        return [json.loads(line) for line in (out/'pages.jsonl').read_text(encoding='utf8').splitlines()]

def available_readings(root,doc_id):
    if (root/'revision/text_sp/pages.jsonl').is_file():return []
    result=[]
    for doc in ('SP','PR'):
        if doc_id and doc_id!=doc:continue
        path=root/'sppr/primary'/f'{doc}.pdf'
        if path.is_file():result+=plan_readings(root,doc,(path.stat().st_mtime_ns,path.stat().st_size))
    return result
