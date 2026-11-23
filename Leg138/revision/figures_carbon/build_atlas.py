"""Make a visual comparison of the 44 IR water and carbon plates from original scans."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

import fitz
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def bounds(fig,is_carbon):
    panels=fig['panels']
    if is_carbon:
        left=min(panels[0]['frame'][0]-51,*[a['x']-3 for a in fig['caption']])
        top=min(p['frame'][1] for p in panels)-42
        right=max(panels[-1]['frame'][2]+9,*[a['x']+a['width']+3 for a in fig['caption']])
        bottom=fig['caption'][-1]['baseline_y']+7
    else:
        left=min(panels[0]['source_frame_950x1240'][0]-49,min(c[0] for c in fig['caption_geometry']))-4
        top=min(p['letter_origin'][1] for p in panels)-19
        right=max(panels[-1]['source_frame_950x1240'][2]+14,max(c[0]+c[2]+3 for c in fig['caption_geometry']))
        bottom=fig['caption_geometry'][-1][1]+7
    return fitz.Rect(left,top,right,bottom)


def crop_scan(source,box):
    box=fitz.Rect(box.x0*source.rect.width/950,box.y0*source.rect.height/1240,
                  box.x1*source.rect.width/950,box.y1*source.rect.height/1240)
    # Render this preview at the actual scan's sampled horizontal resolution.
    native=source.get_image_info()[0]
    ratio=native['width']/(native['bbox'][2]-native['bbox'][0])
    pix=source.get_pixmap(matrix=fitz.Matrix(ratio,ratio),clip=box,colorspace=fitz.csGRAY)
    image=Image.frombytes('L',(pix.width,pix.height),pix.samples)
    stream=io.BytesIO()
    image.save(stream,format='JPEG',quality=88,optimize=True)
    return stream.getvalue()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',required=True,type=Path)
    parser.add_argument('--output',type=Path,default=HERE/'IR_Chemistry_Comparison_Atlas.pdf')
    args=parser.parse_args()
    plates=[]
    for directory,carbon in [(HERE.parent/'figures_ir',False),(HERE,True)]:
        layouts=json.loads((directory/'plot_layout.json').read_text())
        manifest={r['item_id']:r for r in csv.DictReader((directory/'manifest.csv').open())}
        plates.extend([(s,manifest[s['item_id']],carbon) for s in layouts])
    plates.sort(key=lambda p:(p[0]['site'],p[0]['source_page']))
    book=fitz.open()
    bookmarks=[]
    for n,(spec,m,carbon) in enumerate(plates,1):
        item=spec['item_id']
        path=f'VOLUME/CHAPTERS/ir138_{item[2:4]}.pdf'
        src=args.sources/'ir/primary'/path
        if hashlib.sha256(src.read_bytes()).hexdigest()!=m['source_pdf_sha256']:
            raise ValueError('Changed source '+str(src))
        pgnum=int(m['source_page'])
        page=book.new_page(width=850,height=620)
        family='Carbonate and organic carbon' if carbon else 'Interstitial-water geochemistry'
        if spec['site']==854 and carbon:
            family='Carbonate'
        page.insert_text((25,30),f'Site {spec["site"]}   /   {item}   /   {family}',fontname='hebo',fontsize=16)
        page.insert_text((25,57),f'Initial Reports 138  |  chapter PDF p. {pgnum}',fontsize=11)
        page.insert_text((440,57),f'Numerical reconstruction  |  {m["table_ids"]}',fontsize=11)
        left=fitz.Rect(25,70,411,527)
        right=fitz.Rect(440,70,826,527)
        with fitz.open(src) as original, fitz.open(ROOT/m['output']) as redrawn:
            page.insert_image(left,stream=crop_scan(original[pgnum-1],bounds(spec,carbon)))
            page.show_pdf_page(right,redrawn,0)
        page.draw_line((425,63),(425,535),color=(.8,.82,.83),width=.55)
        page.draw_line((25,540),(825,540),color=(.8,.82,.83),width=.55)
        note=m['qualification'].replace('–','-')
        if page.insert_textbox(fitz.Rect(25,551,820,587),note,fontsize=9,fontname='helv',color=(.2,.24,.26))<0:
            raise ValueError('Note does not fit '+item)
        page.insert_text((25,604),'Open original chapter at this page',fontsize=9,color=(.1,.27,.42))
        url='https://www-odp.tamu.edu/publications/138_IR/'+path+'#page='+str(pgnum)
        page.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(22,592,164,607),'uri':url})
        page.insert_text((778,604),f'{n} / {len(plates)}',fontsize=9)
        bookmarks.append([1,f'Site {spec["site"]} | {item}',n])
    book.set_toc(bookmarks)
    book.set_metadata({'title':'Leg 138 | Interstitial-water and carbon figures compared','creator':'Leg 138 digital edition'})
    book.save(args.output,garbage=4,deflate=True,no_new_id=True)
    book.close()


if __name__=='__main__':
    main()
