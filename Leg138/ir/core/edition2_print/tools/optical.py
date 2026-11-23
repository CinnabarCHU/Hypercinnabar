"""Independently OCR each calibrated table rectangle from the printed scan."""
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import argparse, csv, gzip, io, os, subprocess
import fitz
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]

def calc(task):
    ir,config,path=task
    site,pg=config['item_id'],config['pdf_page']
    with fitz.open(ir/path) as doc:
        page=doc[int(pg)-1]
        rect=fitz.Rect(*[float(config[k]) for k in ('x0','header_y','x1','end_y')])
        mat=fitz.Matrix(4,4)
        pix=page.get_pixmap(matrix=mat,colorspace=fitz.csGRAY,clip=rect)
        buf=io.BytesIO()
        Image.frombytes('L',(pix.width,pix.height),pix.samples).save(buf,'PNG',compress_level=1)
    env={**os.environ,'OMP_THREAD_LIMIT':'1'}
    proc=subprocess.run(['tesseract','stdin','stdout','--dpi','288','--psm','6','-l','eng','tsv'],
                        input=buf.getvalue(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,env=env)
    results=[]
    for token in csv.DictReader(io.StringIO(proc.stdout.decode()),delimiter='\t',quoting=csv.QUOTE_NONE):
        if token['level']!='5' or not token.get('text','').strip():continue
        x,y,w,h=map(int,[token[k] for k in ['left','top','width','height']])
        box=[(pix.x+x)/4,(pix.y+y)/4,(pix.x+x+w)/4,(pix.y+y+h)/4]
        results.append((site,pg,*box,token['conf'],token['text']))
    return results

def run(ir):
    specs=list(csv.DictReader((ROOT/'data/layouts.psv').open(),delimiter='|'))
    locs={r['item_id']:r['pdf_path'] for r in csv.DictReader((ROOT.parent/'chapter_items.csv').open())}
    jobs=[(ir,s,locs[s['item_id']]) for s in specs]
    with gzip.open(ROOT/'data/optical_tokens.csv.gz','wt',newline='') as out,ProcessPoolExecutor(max_workers=5) as pool:
        writer=csv.writer(out);writer.writerow(['item_id','pdf_page','x0','y0','x1','y1','confidence','text'])
        for rows in pool.map(calc,jobs):writer.writerows(rows)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('ir_primary',type=Path);run(ap.parse_args().ir_primary)
