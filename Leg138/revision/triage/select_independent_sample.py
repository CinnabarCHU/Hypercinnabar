"""Recreate the stratified 30-line audit selection and optional blinded scan comparison sheets."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
STATES = ('literal_agreement','disagreement','empty_new_reading')
QUOTAS = (('SP',1),('PR',1),('IR',4),('SR',4))


def rank(row):
    key='|'.join(('leg138-ocular-sample-v1',row['comparison'],row['doc_id'],str(row['source_page']),row['segment']))
    return hashlib.sha256(key.encode()).hexdigest()


def select():
    with gzip.open(HERE/'lines.jsonl.gz','rt') as stream:
        pool=sorted((json.loads(line) for line in stream),key=rank)
    selected=[]
    for state in STATES:
        eligible=[r for r in pool if r['comparison']==state]
        docs=set()
        for series,quota in QUOTAS:
            for r in eligible:
                if not quota:
                    break
                if r['doc_id'].split('.')[0]==series and r['doc_id'] not in docs:
                    selected.append(r)
                    docs.add(r['doc_id'])
                    quota-=1
        # A series can lack empty readings. Complete that stratum with distinct documents.
        for r in eligible:
            if len(docs)>=10:
                break
            if r['doc_id'] not in docs:
                selected.append(r)
                docs.add(r['doc_id'])
        if len(docs)!=10:
            raise ValueError('Sample lacks ten distinct documents for '+state)
    return selected


def scan(pg,box,ratio):
    pix=pg.get_pixmap(matrix=fitz.Matrix(ratio,ratio),clip=box,colorspace=fitz.csGRAY,alpha=False,annots=False)
    return Image.frombytes('L',(pix.width,pix.height),pix.samples),hashlib.sha256(pix.samples).hexdigest()


def sheets(rows,sources,out):
    docs={r['doc_id']:r for r in csv.DictReader((HERE.parents[1]/'data/documents.csv').open())}
    out.mkdir(parents=True,exist_ok=True)
    for i,r in enumerate(rows):
        if not i%5:
            sheet=Image.new('RGB',(1370,5*225),'#edf0f3')
        path=sources/docs[r['doc_id']]['local_source']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=r['witness_sha256']:
            raise ValueError(str(path))
        with fitz.open(path) as pdf:
            pg=pdf[r['source_page']-1]
            rect=fitz.Rect(r['clip_pt'])
            strip,sha=scan(pg,rect,240/72)
            if sha!=r['strip_sha256']:
                raise ValueError('Different crop '+str(i))
            context,_=scan(pg,(rect+(-22,-26,22,26)) & pg.rect,2.2)
            thumb,_=scan(pg,pg.rect,.25)
            scale=thumb.width/pg.rect.width
            ImageDraw.Draw(thumb).rectangle(tuple(v*scale for v in rect),outline=110,width=2)
        y=(i%5)*225
        label=f'{i+1:02d}   {r["doc_id"]}, source p.{r["source_page"]}, segment {r["segment"]}'
        ImageDraw.Draw(sheet).text((5,y+3),label,fill='black')
        strip.thumbnail((1160,67))
        context.thumbnail((1160,125))
        sheet.paste(strip,(5,y+20))
        sheet.paste(context,(5,y+95))
        sheet.paste(thumb,(1190,y+4))
        if i%5==4:
            sheet.save(out/f'audit_{i//5+1}.png')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources',type=Path)
    p.add_argument('--contact-sheets',type=Path)
    args=p.parse_args()
    sample=select()
    for i,r in enumerate(sample,1):
        print(i,r['comparison'],r['doc_id'],r['source_page'],r['segment'],rank(r))
    if args.contact_sheets:
        if not args.sources:
            p.error('--sources is required to render the comparison sheets')
        sheets(sample,args.sources,args.contact_sheets)


if __name__=='__main__':
    main()
