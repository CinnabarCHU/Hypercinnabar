"""Draw source excerpts for human reading of selected physical rows."""
from pathlib import Path
from collections import defaultdict
from PIL import Image,ImageDraw,ImageFont
import argparse,csv,gzip,json,fitz
from build import ROOT,DATA,load
def reviews(ir):
    rows=load(DATA/'print_rows.csv.gz');regs=load(DATA/'regions.csv');info={s['item_id']:s for s in load(DATA/'datasets.csv')}
    files={};cuts=[];choices=[]
    for reg in regs:
        item,pg=reg['item_id'],reg['pdf_page'];path=ir/reg['pdf_path']
        if path not in files:files[path]=fitz.open(path)
        pp=files[path][int(pg)-1];l,t,r,b=map(float,reg['body_bbox'].split(','))
        if item=='IR02.T09':target=0.3
        else:target=.42
        candid=[s for s in rows if (s['item_id'],s['pdf_page'])==(item,pg) and len(json.loads(s['cell_readings_json']))>=2]
        q=min(candid,key=lambda z:abs(float(z['row_y_pt'])-(t+(b-t)*target)))
        l,yt,r,yb=map(float,q['source_row_bbox_pt'].split(','))
        pm=pp.get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(l,yt-.8,r,yb+.8),colorspace=fitz.csGRAY)
        img=Image.frombytes('L',(pm.width,pm.height),pm.samples).convert('RGB');cuts.append((img,item,pg,q))
        choices.append(q)
    review=ROOT/'review';review.mkdir(exist_ok=True)
    for k in range(0,len(cuts),10):
        z=cuts[k:k+10];w=max(i.width for i,*_ in z)+10;new=Image.new('RGB',(w,sum(i.height+28 for i,*_ in z)), 'white');yy=0;dd=ImageDraw.Draw(new)
        for i,it,pg,q in z:
            dd.text((4,yy),f"{it} / PDF {pg} / y {q['row_y_pt']} pt", fill='#07574b', font=ImageFont.truetype('/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',15))
            new.paste(i,(4,yy+18));yy+=i.height+28
        new.save(review/f'qa_{k//10}.png')
    with (review/'chosen_rows.txt').open('w') as writer:
        for row in choices:print(row['item_id'],row['pdf_page'],row['row_y_pt'],row['cell_readings_json'],file=writer)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ir_primary',type=Path);reviews(p.parse_args().ir_primary)
