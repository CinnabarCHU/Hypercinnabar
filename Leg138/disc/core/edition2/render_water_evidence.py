"""Extract the comparison header crops and Site 848 continuation directly from publisher PDFs."""
import argparse
from pathlib import Path
import fitz
from PIL import Image,ImageDraw
from collate_water import PAGE
def extract(page,rect,zoom):
    p=page.get_pixmap(matrix=fitz.Matrix(zoom,zoom),clip=rect)
    return Image.frombytes("RGB",(p.width,p.height),p.samples)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ir",type=Path);parser.add_argument("output",type=Path)
    a=parser.parse_args()
    first=Image.new("RGB",(1420,len(PAGE)*88),"white");continued=Image.new("RGB",(1350,600),"white")
    j=0
    for i,(site,(page,printed)) in enumerate(PAGE.items()):
        doc=fitz.open(a.ir/f"primary/VOLUME/CHAPTERS/ir138_{site-835:02}.pdf")
        p=doc[page-1];words=p.get_text("words")
        salts=[w for w in words if w[4]=="Salinity"];chlorides=[w for w in words if w[4]=="Chloride"]
        y=min((abs(c[1]-s[1]),s[1]) for c in chlorides for s in salts)[1]
        im=extract(p,fitz.Rect(0,y-15,p.rect.width,y+20),2.2)
        first.paste(im.resize((1380,int(im.height*1380/im.width))),(30,i*88))
        ImageDraw.Draw(first).text((3,i*88+27),str(site),fill="black")
        if site not in [845,848,849,850,851,852]:continue
        p=doc[page-(site==852)];y=p.search_for("Ammonia")[0].y0
        im=extract(p,fitz.Rect(0,y-10,p.rect.width,y+24),2.2);continued.paste(im,(22,j*95))
        ImageDraw.Draw(continued).text((1,j*95+28),str(site),fill="black");j+=1
        if site==848:
            # Preserve the raster extracted directly from the relevant printed table body.
            p.get_pixmap(matrix=fitz.Matrix(2.8,2.8),clip=fitz.Rect(153,y-23,389,y+115)).save(a.output/"site848_table10_continued.png")
    first.save(a.output/"print_headers.jpg",quality=92)
    continued.save(a.output/"print_continued_headers.jpg",quality=92)
if __name__=="__main__":main()
