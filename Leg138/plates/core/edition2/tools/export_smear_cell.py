"""Export a source-faithful scan of a smear-slide cell or row by published location."""
import argparse
import csv
import gzip
import hashlib
from pathlib import Path

import fitz
from export_regions import BASE,rows


def run(primary,data,identifier,destination,scale):
    with gzip.open(data/'smear_cells.csv.gz','rt',encoding='utf-8') as f:
        matches=[r for r in csv.DictReader(f) if identifier in (r['cell_id'],r['row_id'])]
    if not matches:raise ValueError(f'Unknown cell or row {identifier}')
    r=matches[0];source=next(p for p in rows(data/'smear_grid_pages.csv') if (p['site'],p['pdf_page'])==(r['site'],r['pdf_page']))
    raw=(primary/source['source_path']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=source['source_sha256']:raise ValueError('Source PDF checksum mismatch')
    left=min(float(q['x0_pt']) for q in matches);right=max(float(q['x1_pt']) for q in matches)
    rect=fitz.Rect(left,float(r['y0_pt']),right,float(r['y1_pt']))
    with fitz.open(stream=raw,filetype='pdf') as pdf:
        png=pdf[int(r['pdf_page'])-1].get_pixmap(matrix=fitz.Matrix(scale,scale),clip=rect,alpha=False).tobytes('png')
    destination.parent.mkdir(exist_ok=True,parents=True);destination.write_bytes(png)
    with destination.with_suffix('.csv').open('w',newline='',encoding='utf-8') as f:
        out=csv.DictWriter(f,fieldnames=list(matches[0])+['source_url','pdf_sha256','render_scale','png_sha256'])
        out.writeheader()
        out.writerows(dict(q,source_url=source['source_url'],pdf_sha256=source['source_sha256'],render_scale=scale,
                              png_sha256=hashlib.sha256(png).hexdigest()) for q in matches)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path);p.add_argument('identifier')
    p.add_argument('png',type=Path);p.add_argument('--data',type=Path,default=BASE/'data')
    p.add_argument('--scale',type=float,default=4);a=p.parse_args()
    run(a.primary,a.data,a.identifier,a.png,a.scale)
