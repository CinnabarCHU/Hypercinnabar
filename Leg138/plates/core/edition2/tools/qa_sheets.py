"""Build diagnostic overlays for a deterministic stratified review, including narrow and low-resolution scans."""
import argparse
from collections import defaultdict
import csv
import hashlib
from pathlib import Path

from PIL import Image,ImageDraw,ImageFont
from export_regions import rows,get_image,bbox,BASE


def choose(photos):
    sites=defaultdict(list)
    picks={}
    def mark(core,why):picks.setdefault(core,[]).append(why)
    for p in photos:
        sites[p['site']].append(p)
        if int(p['height_px'])<2000:mark(p['core_id'],'low-resolution source')
        if p['geometric_status']!='edge_supported':mark(p['core_id'],'all geometrically ambiguous photographs')
        if p['core_id'] in {'844B14H','844C13H','846D2H','850B2H','852A1H'}:
            mark(p['core_id'],'regression check for interrupted liner edges')
        if not int(p['material_rois']):mark(p['core_id'],'no sediment candidate was emitted')
    for site,subset in sorted(sites.items()):
        mark(site+'B2H','edition-one manually located windows')
        smallest=min(subset,key=lambda p:int(p['width_px'])/int(p['height_px']))
        mark(smallest['core_id'],'narrowest composition at this site')
        difficult=min(subset,key=lambda p:(int(p['material_rois'])/int(p['detected_or_attempted_lanes']),
                         int(p['material_rois']),int(p['width_px'])))
        mark(difficult['core_id'],'fewest candidate intervals per lane')
        ordinary=sorted(subset,key=lambda p:hashlib.sha256(('138-qa-'+p['core_id']).encode()).hexdigest())
        for p in ordinary:
            if p['core_id'] not in picks:
                mark(p['core_id'],'deterministic within-site selection')
                break
    return picks


def overlay(primary,photo,regions,thumb_height=295):
    image = get_image(primary,photo)
    w = round(image.width*thumb_height/image.height)
    preview=image.resize((w,thumb_height),Image.Resampling.LANCZOS)
    annotated=preview.copy()
    draw=ImageDraw.Draw(annotated)
    sx,sy=w/image.width,thumb_height/image.height
    palette={'photographed_liner':'#007865','printed_ruler':'#1643e6','board_background':'#ad16ca','sediment_candidate':'#e3780a','reviewed_non_sediment_band':'#b02c51'}
    for region in regions:
        role=region['role']
        x0,y0,x1,y1=bbox(region)
        box=[round(x0*sx),round(y0*sy),round(x1*sx)-1,round(y1*sy)-1]
        if role=='sediment_candidate':
            # Two corner ticks delineate the candidate while keeping the actual sediment visible.
            draw.line([box[0],box[1],box[0],box[3]],fill=palette[role],width=1)
            draw.line([box[0],box[1],box[2],box[1]],fill=palette[role],width=1)
            draw.line([box[0],box[3],box[2],box[3]],fill=palette[role],width=1)
        else:
            draw.rectangle(box,outline=palette[role],width=1)
    return preview,annotated


def sheets(primary,data,out):
    out.mkdir(parents=True,exist_ok=True)
    ps=rows(data/'photos.csv')
    picks=choose(ps)
    selected={p['core_id']:p for p in ps if p['core_id'] in picks}
    grouped=defaultdict(list)
    for r in rows(data/'regions.csv'):
        if r['core_id'] in selected:grouped[r['core_id']].append(r)
    selected_ids=sorted(selected)
    with (out/'review_selection.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['core_id','selection'])
        w.writerows((c,' | '.join(picks[c])) for c in selected_ids)
    tilew,tileh=210,325
    for i in range(0,len(selected_ids),6):
        canvas=Image.new('RGB',(3*tilew,2*tileh),'#f3f1ec')
        draw=ImageDraw.Draw(canvas)
        for j,core in enumerate(selected_ids[i:i+6]):
            p=selected[core]
            _,anno=overlay(primary,p,grouped[core])
            x=(j%3)*tilew;y=(j//3)*tileh
            canvas.paste(anno,(x,y+24))
            draw.text((x+2,y+5),f'{core} / {p["liner_rois"]} liners / {p["material_rois"]} interiors',fill='#162227')
        canvas.save(out/f'sheet_{i//6+1:02}.jpg',quality=87)
    print(len(picks),'photos in review sheets')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--data',type=Path,default=BASE/'data')
    a=p.parse_args();sheets(a.primary,a.data,a.output)
