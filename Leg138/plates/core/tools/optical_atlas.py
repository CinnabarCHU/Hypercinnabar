"""Compose an inspection PDF using the verified source crops and native photo context."""
from pathlib import Path
import argparse,csv,io
from PIL import Image,ImageDraw
import fitz
from optical_windows import get_native
def png(im):
    b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()
def make(primary,pdf):
    root=Path(__file__).resolve().parents[1]
    with (root/'data/optical_regions.csv').open() as f:regions=list(csv.DictReader(f))
    dest=fitz.open()
    for i in range(4):
        page=dest.new_page(width=680,height=835)
        page.insert_text((36,43),'Leg 138  /  Optical windows',fontsize=24,fontname='Times-Bold')
        page.insert_text((36,62),'Section 3, Hole B, Core 2H. Source windows at native RGB resolution; coloured boxes are editorial locators.',fontsize=9)
        page.insert_text((36,76),'Pixel coordinates start at the top left of the embedded JPEG. A printed cm ruler is preserved separately.',fontsize=9)
        for rowidx in range(3):
            site=844+3*i+rowidx
            if site>854:break
            pair=[r for r in regions if int(r['site'])==site];core=pair[0]['core_id'];im,raw,obj=get_native(primary/pair[0]['source_path'])
            h=90+rowidx*231
            thumb=im.copy();thumb.thumbnail((145,206),Image.Resampling.LANCZOS);draw=ImageDraw.Draw(thumb)
            for r,col in zip(pair,[(0,128,115),(214,96,38)]):
                box=[int(r[k]) for k in ('left_px','top_px','right_px_exclusive','bottom_px_exclusive')]
                rect=(box[0]*thumb.width/im.width,box[1]*thumb.height/im.height,box[2]*thumb.width/im.width,box[3]*thumb.height/im.height)
                draw.rectangle(rect,outline=col,width=2)
            page.insert_text((36,h+15),f'Site {site}',fontsize=14,fontname='Times-Bold')
            page.insert_image(fitz.Rect(36,h+22,176,h+220),stream=png(thumb),keep_proportion=True)
            for k,r in enumerate(pair):
                box=tuple(int(r[c]) for c in ('left_px','top_px','right_px_exclusive','bottom_px_exclusive'));patch=im.crop(box)
                x=(205,365)[k];page.insert_text((x,h+15),('Sediment interior','Printed ruler')[k],fontsize=10)
                page.insert_image(fitz.Rect(x,h+23,x+75,h+215),stream=png(patch),keep_proportion=True)
                page.insert_text((x+77,h+45),f'x {box[0]}:{box[2]}',fontsize=8)
                page.insert_text((x+77,h+58),f'y {box[1]}:{box[3]}',fontsize=8)
            page.insert_text((518,h+18),f'{core}',fontsize=12,fontname='Courier-Bold')
            page.insert_text((518,h+43),f'{im.width} x {im.height} px',fontsize=8)
            page.insert_text((518,h+56),'DeviceRGB / JPEG',fontsize=8)
            page.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(516,h+65,655,h+85),'uri':'https://www-odp.tamu.edu/publications/138_IR/'+pair[0]['source_path']})
            page.insert_text((518,h+78),'Open original PDF',fontsize=9,color=(.08,.4,.39))
            page.draw_line((36,h+225),(646,h+225),color=(.78,.83,.81),width=.5)
        page.insert_text((36,805),'Crops preserve decoded JPEG values. Absolute colorimetry, core depth and whole-core segmentation require additional evidence.',fontsize=8.1)
        page.insert_text((610,805),f'{i+1}/4',fontsize=8)
    dest.save(pdf,garbage=4,deflate=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path);p.add_argument('pdf',type=Path);a=p.parse_args();make(a.primary,a.pdf)
