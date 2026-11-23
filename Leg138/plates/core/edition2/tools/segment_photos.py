"""Locate the printed ruler, photographed liners, candidate sediment windows and blank board patches.

Usage: python tools/segment_photos.py PATH_TO_PLATES_PRIMARY [--out DATA] [--workers N]
CSV coordinates use native JPEG pixels with left/top inclusive and right/bottom exclusive.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import io
import math
from pathlib import Path

import fitz
import numpy as np
from PIL import Image
from scipy.ndimage import median_filter, gaussian_filter1d

BASE = Path(__file__).resolve().parents[1]
WORK_HEIGHT = 540


def read_csv(path):
    with path.open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_csv(path, rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def series_runs(mask):
    edges = np.flatnonzero(np.diff(np.r_[False, mask, False].astype(int)))
    return zip(edges[::2], edges[1::2])


def native_box(box,width,height,work_width):
    # Round inward so conservative inner windows do not admit outside pixels.
    x0,y0,x1,y1 = box
    return (math.ceil(x0*width/work_width), math.ceil(y0*height/WORK_HEIGHT),
            math.floor(x1*width/work_width), math.floor(y1*height/WORK_HEIGHT))


def board_patch(rgb,first_edge):
    """Choose a bright uniform patch away from ruler, labels, cut edges and liner."""
    h,w,_ = rgb.shape
    scored = []
    for y in range(22,h-26,12):
        for x in range(4,first_edge-38,5):
            patch = rgb[y:y+18,x:x+17,:]
            q05,q50,q95 = np.percentile(patch,[5,50,95],axis=(0,1))
            score = float(np.max(q95-q05) + max(0,155-q50.mean()))
            scored.append((score,(x,y,x+17,y+18)))
    return min(scored,key=lambda item:item[0])


def inspect(args):
    row,src,primary,exclusions = args
    core = row['core_id']
    path = primary / row['source_path']
    width,height = int(row['width_px']),int(row['height_px'])
    with fitz.open(path) as doc:
        native = doc.xref_stream_raw(int(row['xref']))
    if hashlib.sha256(native).hexdigest() != row['native_stream_sha256']:
        raise ValueError(f'Source stream changed: {core}')
    photo = Image.open(io.BytesIO(native))
    if photo.size != (width,height) or photo.mode != 'RGB':
        raise ValueError(f'Unexpected raster: {core}')
    work_width = round(width * WORK_HEIGHT / height)
    photo.draft('RGB',(work_width,WORK_HEIGHT))
    rgb = np.asarray(photo.resize((work_width,WORK_HEIGHT),Image.Resampling.LANCZOS),dtype=np.float32)
    gray = rgb.mean(axis=2)
    edges = np.diff(gray,axis=1)
    leading = gaussian_filter1d(np.median(np.maximum(-edges[17:55],0),axis=0),.6)
    # At the standard height, the first liner starts close to x=75; successive lanes are ~35.3 px apart.
    # Search independently around the expected template, and require visible edge evidence.
    peaks = []
    for i in range(10):
        start = round(75+35.35*i)
        if start+21 >= work_width:
            break
        lo,hi = max(0,start-6),min(work_width-2,start+7)
        x = lo+int(np.argmax(leading[lo:hi]))
        peaks.append((x,float(leading[x])))
    assert peaks,(core,work_width)
    first = peaks[0][0]
    lanes,regions = [],[]
    def region(role,lane,ordinal,box,basis,score=''):
        coords = native_box(box,width,height,work_width)
        ident = f'{core}.L{lane:02}.{role}.{ordinal:02}'
        r = dict(roi_id=ident,core_id=core,site=core[:3],lane_ordinal=lane,role=role,
                 left_px=coords[0],top_px=coords[1],right_px_exclusive=coords[2],bottom_px_exclusive=coords[3],
                 basis=basis,score=score)
        regions.append(r)
    region('printed_ruler',0,1,(first-23,16,first-1,529),'board template bounded by first liner')
    bgscore,bbox = board_patch(rgb,first)
    if bgscore <= 35:
        region('board_background',0,1,bbox,'bright low-variation window outside the ruler and liners',f'{bgscore:.2f}')
    for pos,(x,strength) in enumerate(peaks,1):
        # The sleeve's second edge is normally 25–26 working pixels from the first.
        right_expected = min(x+25,work_width-3)
        rlo,rhi = max(x+19,right_expected-3),min(work_width-1,right_expected+4)
        upper_edges = np.median(np.abs(edges[17:55]),axis=0)
        right = rlo+int(np.argmax(upper_edges[rlo:rhi]))
        left_map = np.max(np.abs(edges[:,x-4:x+5]),axis=1)
        right_map = np.max(np.abs(edges[:,max(0,right-4):min(work_width-1,right+5)]),axis=1)
        rails = median_filter(np.minimum(left_map,right_map),size=9)
        # A dark printed cap may sit above an empty slot. Conversely a white VOID slip or
        # pale sediment may interrupt rails above genuine sample. Require sustained paired
        # support, and locate the last supported segment rather than stopping at the first gap.
        search = (np.arange(WORK_HEIGHT)>=16) & (np.arange(WORK_HEIGHT)<530)
        supported = [(a,b) for a,b in series_runs((rails>=38)&search) if b-a>=15]
        end = int(supported[-1][1]) if supported else 16
        interruptions = sum(1 for a,b in series_runs((rails<34)&search&(np.arange(WORK_HEIGHT)<end)) if b-a>=17)
        layout='strong' if strength>=32 else 'weak'
        if not supported:
            layout='unresolved'
        elif end<46:
            layout='short'
        evidence = float(np.median(rails[20:max(21,end-4)]))
        lane = dict(lane_id=f'{core}.L{pos:02}',core_id=core,site=core[:3],lane_ordinal=pos,
                    left_edge_native_px=round(x*width/work_width),right_edge_native_px=round(right*width/work_width),
                    start_native_y=round(16*height/WORK_HEIGHT),estimated_lower_edge_y=round(end*height/WORK_HEIGHT),
                    layout_evidence=layout,internal_rail_interruptions=interruptions,top_left_edge_strength=f'{strength:.2f}',paired_edge_median=f'{evidence:.2f}',
                    material_region_count=0,material_fraction_of_envelope='0.000')
        lanes.append(lane)
        if layout == 'unresolved':
            continue
        region('photographed_liner',pos,1,(x+1,16,right+1,end),'pair of detected edges; may contain caps, liner, voids or labels',layout)
        # Background from the two inter-liner gaps separately at each y. Ruler marks can occur in the gaps.
        # Use non-edge pixels, take a per-row median, and smooth perpendicular to the printed graduations.
        gap1=rgb[:,max(0,x-6):x-2]
        gap2=rgb[:,min(work_width-1,right+4):min(work_width,right+8)]
        board = np.median(np.concatenate([gap1,gap2],axis=1),axis=1)
        board = median_filter(board,size=(11,1))
        xx0,xx1=x+6,right-4
        mat = np.median(rgb[:,xx0:xx1],axis=1)
        distance = np.sqrt(((board-mat)**2).sum(axis=1))
        distance = median_filter(distance,size=5)
        # Avoid white voids and labels that resemble the board, reserve extra padding at possible catcher ends.
        # Interior texture alone cannot distinguish white paper or plastic from very pale sediment.
        safe = ((np.arange(WORK_HEIGHT)>=22) &
                (np.arange(WORK_HEIGHT)<end-(18 if pos==len(peaks) else 9)) &
                (rails>=40) & (distance>=35))
        for exclusion in exclusions:
            if int(exclusion['lane_ordinal'])!=pos:
                continue
            top=int(exclusion['top_px']);bottom=int(exclusion['bottom_px_exclusive'])
            first_y=math.floor(top*WORK_HEIGHT/height);last_y=math.ceil(bottom*WORK_HEIGHT/height)
            safe[first_y:last_y]=False
            region('reviewed_non_sediment_band',pos,1,(xx0,first_y,xx1,last_y),exclusion['reason'],'visually checked, padded')
        eligible=[(int(a)+1,int(b)-1) for a,b in series_runs(safe) if b-a>=15]
        covered=0
        for number,(y0,y1) in enumerate(eligible,1):
            covered+=y1-y0
            region('sediment_candidate',pos,number,(xx0,y0,xx1,y1),
                   'interior of paired edges; local RGB-distance gate and end padding',
                   f'{np.median(distance[y0:y1]):.2f}')
        lane['material_region_count']=len(eligible)
        lane['material_fraction_of_envelope']=f'{covered/(end-16):.3f}'
    status=[p['layout_evidence'] for p in lanes]
    geometry = 'review_needed' if 'unresolved' in status else ('weak_or_short_lane' if any(s!='strong' for s in status) else 'edge_supported')
    summary=dict(core_id=core,site=core[:3],source_path=row['source_path'],source_url=src['url'],pdf_sha256=src['sha256'],
               jpeg_sha256=row['native_stream_sha256'],pdf_image_xref=row['xref'],width_px=width,height_px=height,
               geometric_status=geometry,detected_or_attempted_lanes=len(lanes),
               liner_rois=sum(r['role']=='photographed_liner' for r in regions),
               material_rois=sum(r['role']=='sediment_candidate' for r in regions),
               ruler_rois=sum(r['role']=='printed_ruler' for r in regions),
               background_rois=sum(r['role']=='board_background' for r in regions),
               human_review='see qa.csv; only explicitly named review scopes apply')
    return summary,lanes,regions


def run(primary,data,out,workers):
    photos = read_csv(data/'native_photo_catalog.csv')
    sources = {r['source_path']:r for r in read_csv(data/'plate_sources.csv')}
    out.mkdir(parents=True,exist_ok=True)
    exclusions=read_csv(BASE/'data/reviewed_exclusions.csv')
    inputs = [(p,sources[p['source_path']],primary,[e for e in exclusions if e['core_id']==p['core_id']]) for p in photos]
    results = []
    if workers == 1:
        results = [inspect(work) for work in inputs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as workers_pool:
            results = list(workers_pool.map(inspect,inputs,chunksize=3))
    save_csv(out/'photos.csv',[x[0] for x in results])
    save_csv(out/'lanes.csv',[r for x in results for r in x[1]])
    save_csv(out/'regions.csv',[r for x in results for r in x[2]])
    print('photos',len(results),'lanes',sum(len(r[1]) for r in results),'ROIs',sum(len(r[2]) for r in results))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('primary',type=Path)
    p.add_argument('--catalog',type=Path,default=BASE.parent/'data')
    p.add_argument('--out',type=Path,default=BASE/'data')
    p.add_argument('--workers',type=int,default=4)
    a=p.parse_args();run(a.primary,a.catalog,a.out,a.workers)
