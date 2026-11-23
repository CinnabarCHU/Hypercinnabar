"""Compare selected publisher lines to a new OCR reading of the underlying scan.

Run from Leg138. Source PDFs live under --sources in the catalogue's layout.
The sample is deliberately biased towards scientific glyphs. It is a review queue,
never a character-error estimator or an automatic change to the publication.
"""
import argparse
import csv
import difflib
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import fitz
from PIL import Image

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
sys.path.insert(0, str(BASE / "edition2"))
from page_text import runs

# Select one high-risk scientific line and two spread-out prose/heading/caption
# lines per eligible page. Short number-only rows and vertical plot labels are
# outside this particular sampling frame.
SCIENCE = re.compile(r"\d[°′″]|[δσμµ±×‰⁰¹²³₀₁₂₃₄₅₆₇₈₉]|[A-Za-z][|~][A-Za-z]|(?i:\b(?:Corg|CaCO3|SiO2|El Ni.o|d18O|mmol|mcd|mbsf)\b)")

def digest(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()

def plain(t):
    return " ".join(t.split())

def select(packets,page,complete=False):
    lines=[]
    for pk in packets:
        if pk["role"]=="positioned":
            continue
        for s in pk["lines"]:
            x,y,r,b=s["bbox"]
            if (s["direction"][0]>.96 and 6<b-y<24 and r-x>45
                and len(s["text"])>=18 and sum(c.isalpha() for c in s["text"])>=9):
                lines.append((s,pk["role"]))
    if complete or not lines:return lines,len(lines)
    # The content hash makes tie-breaking stable without picking the same
    # running head every time. No probabilities or confidence inferred.
    def tie(entry):
        return hashlib.sha256((str(page)+"|"+entry[0]["text"]).encode()).digest()
    best=max(lines,key=lambda e:(len(SCIENCE.findall(e[0]["text"])),tie(e)))
    first,second=lines[:max(1,len(lines)//2)],lines[len(lines)//2:]
    out=[]
    for e in (best, min(first,key=tie), min(second or first,key=tie)):
        if e not in out:out.append(e)
    return out,len(lines)

def read_sheet(batch):
    # Stack strips at separate, known y coordinates. Assign each OCR word by
    # its center, so dropped lines do not shift any later comparison.
    if not batch:return
    widths=[im.width for row,im in batch]
    y=12; bands=[]
    for _,im in batch:
        bands.append((y,y+im.height))
        y+=im.height+14
    sheet=Image.new("L",(max(widths)+24,y),255)
    for (_,im),(top,_) in zip(batch,bands):sheet.paste(im,(12,top))
    buf=io.BytesIO();sheet.save(buf,format="PNG")
    proc=subprocess.run(["tesseract","stdin","stdout","--dpi","240","-l","eng","--psm","6","tsv"],
        input=buf.getvalue(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,env={**os.environ,"OMP_THREAD_LIMIT":"1"})
    words=[[] for _ in batch]
    for word in csv.DictReader(io.StringIO(proc.stdout.decode()),delimiter="\t",quoting=csv.QUOTE_NONE):
        if word.get("level")!="5" or not (word.get("text") or "").strip():continue
        center=int(word["top"])+int(word["height"])/2
        for i,(lo,hi) in enumerate(bands):
            if lo<=center<hi:
                words[i].append((int(word["left"]),word["text"]));break
    for (row,im),line in zip(batch,words):
        text=" ".join(w for x,w in sorted(line))
        row["scan_ocr"]=text
        row["comparison"]="literal_agreement" if plain(text)==plain(row["publisher"]) else ("disagreement" if text else "empty_new_reading")
        row["similarity"]=round(difflib.SequenceMatcher(a=plain(row["publisher"]),b=plain(text),autojunk=False).ratio(),4)

def run(job):
    source,doc,complete=job
    path=source/doc["source_local"]
    if digest(path)!=doc["source_pdf_sha256"]:raise ValueError(path)
    records=[];pages=[];batch=[]
    with fitz.open(path) as pdf:
        for n,p in enumerate(pdf,1):
            selected,eligible=select(runs(p)[1],n,complete)
            pages.append(dict(doc_id=doc["doc_id"],source_page=n,eligible_line_segments=eligible,sampled_line_segments=len(selected)))
            for s,role in selected:
                rect=fitz.Rect(s["bbox"])+(-1.2,-1.15,1.2,1.15)
                rect=rect & p.rect
                px=p.get_pixmap(matrix=fitz.Matrix(240/72,240/72),clip=rect,colorspace=fitz.csGRAY,alpha=False,annots=False)
                im=Image.frombytes("L",(px.width,px.height),px.samples)
                addr=".".join(str(s[k]) for k in ("block","line","part"))
                row=dict(doc_id=doc["doc_id"],source_page=n,segment=addr,role=role,
                    bbox_pt=s["bbox"],clip_pt=[round(a,3) for a in rect],witness_sha256=doc["source_pdf_sha256"],
                    strip_sha256=hashlib.sha256(px.samples).hexdigest(),publisher=s["text"])
                records.append(row);batch.append((row,im))
                if len(batch)>=24:read_sheet(batch);batch=[]
    read_sheet(batch)
    return records,pages

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--sources",type=Path,required=True);p.add_argument("--out",type=Path,default=HERE)
    p.add_argument("--workers",type=int,default=3);p.add_argument("--doc",action="append")
    p.add_argument("--all-eligible",action="store_true",help="Run every eligible line, including the sample; use a separate output directory.")
    a=p.parse_args()
    with (BASE/"edition2/documents.csv").open(newline="") as f:docs=list(csv.DictReader(f))
    selected=[d for d in docs if not a.doc or d["doc_id"] in a.doc]
    if not selected or set(a.doc or [])-{r["doc_id"] for r in selected}:raise ValueError("Unknown document ID")
    a.out.mkdir(parents=True,exist_ok=True);pages=[];states=Counter()
    with (a.out/"lines.jsonl.gz").open("wb") as raw,gzip.GzipFile(filename="",fileobj=raw,mode="wb",mtime=0) as zipped,ProcessPoolExecutor(max_workers=a.workers) as pool:
        for records,pp in pool.map(run,((a.sources,d,a.all_eligible) for d in selected)):
            pages.extend(pp)
            for r in records:
                states[r["comparison"]]+=1
                zipped.write((json.dumps(r,ensure_ascii=False,separators=(",",":"))+"\n").encode())
            print(pp[0]["doc_id"],len(pp),len(records),flush=True)
    with (a.out/"page_sample.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=pages[0]);w.writeheader();w.writerows(pages)
    stats=dict(mode=('all_eligible' if a.all_eligible else 'sample'),documents=len(selected),pages_indexed=len(pages),pages_with_sample=sum(bool(r["sampled_line_segments"]) for r in pages),
        eligible_segments=sum(r["eligible_line_segments"] for r in pages),sampled_segments=sum(states.values()),states=dict(states),
        engine=subprocess.check_output(["tesseract","--version"],text=True).splitlines()[0],pymupdf=fitz.VersionBind,render_dpi=240)
    (a.out/"summary.json").write_text(json.dumps(stats,indent=2)+"\n")
if __name__=="__main__":main()
