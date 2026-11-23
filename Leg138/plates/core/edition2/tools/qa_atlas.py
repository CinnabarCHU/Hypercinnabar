"""Publish selected original/overlay pairs showing successful, ambiguous and withheld segments."""
import argparse
from collections import defaultdict
import io
from pathlib import Path

import fitz

from export_regions import BASE,rows
from qa_sheets import overlay

CASES=[
 ('844B2H','A paper tag crosses the first liner near 80 cm. The red band masks the PALEO label and a small margin.'),
 ('845A1H','Two central slots have no sustained pair of sleeve edges. Six photographed liners are outlined.'),
 ('846D20X','One of two 1063-pixel-high archival JPEGs. The marked white catcher tag is excluded.'),
 ('847C25X','One short photographed catcher or section. The ruler continues below the recovered interval.'),
 ('848B8H','Eight liners remain visible. Sediment and the backing are too similar in RGB for the material gate.'),
 ('852A1H','A white sleeve with red handwriting interrupts lane two. The lower section is retained as a candidate.')]
def stream(im):
    target=io.BytesIO();im.save(target,format='JPEG',quality=86,subsampling=0);return target.getvalue()

def build(primary,data,out):
    photos={r['core_id']:r for r in rows(data/'photos.csv')}
    regs=defaultdict(list)
    for x in rows(data/'regions.csv'):regs[x['core_id']].append(x)
    pdf=fitz.open();toc=[]
    for sheet in range(3):
        page=pdf.new_page(width=595,height=842)
        page.insert_text((38,35),'OCEAN DRILLING PROGRAM  /  LEG 138',fontsize=9,color=(.19,.37,.40))
        page.insert_text((36,67),'Native image segmentation checks',fontsize=23,fontname='hebo',color=(.12,.22,.26))
        for i,(label,color) in enumerate([('Liner',(.01,.46,.39)),('Candidate material',(.89,.43,.07)),
               ('Ruler',(.08,.24,.84)),('Board',(.64,.08,.74)),('Reviewed exclusion',(.7,.14,.29))]):
            x=[37,107,232,298,366][i];page.draw_rect(fitz.Rect(x,87,x+9,96),fill=color,color=color)
            page.insert_text((x+14,96),label,fontsize=9)
        for j,(core,description) in enumerate(CASES[sheet*2:sheet*2+2]):
            p=photos[core];thumb,anno=overlay(primary,p,regs[core],thumb_height=560)
            base=115+j*340
            page.insert_text((37,base+5),core,fontsize=14,fontname='hebo',color=(.10,.23,.25))
            page.insert_text((37,base+20),'Original JPEG',fontsize=9)
            page.insert_text((238,base+20),'Region overlay',fontsize=9)
            for col,im in [(37,thumb),(238,anno)]:
                width=250*im.width/im.height
                page.insert_image(fitz.Rect(col,base+28,col+width,base+278),stream=stream(im))
            page.insert_textbox(fitz.Rect(37,base+284,556,base+312),description,fontsize=9.6,lineheight=1.25)
            page.insert_text((37,base+325),f'Native {p["width_px"]} x {p["height_px"]} px    |    {p["liner_rois"]} liner ROIs    |    {p["material_rois"]} candidate intervals',fontsize=8,color=(.23,.33,.35))
            page.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(436,base+313,555,base+329),'uri':p['source_url']})
            page.insert_text((455,base+325),'Open publisher PDF',fontsize=8,color=(.12,.38,.40))
        page.insert_text((37,819),'Regions refer to the decoded archival JPEG. Brightness and RGB values have no absolute optical calibration here.',fontsize=8)
        page.insert_text((548,819),f'{sheet+1}/3',fontsize=8)
        toc.append([1,' / '.join(c for c,_ in CASES[sheet*2:sheet*2+2]),sheet+1])
    pdf.set_toc(toc);pdf.set_metadata({'title':'Leg 138 | Native image segmentation checks'})
    pdf.save(out,deflate=True,garbage=4,no_new_id=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path);p.add_argument('pdf',type=Path)
    p.add_argument('--data',type=Path,default=BASE/'data');a=p.parse_args();build(a.primary,a.data,a.pdf)
