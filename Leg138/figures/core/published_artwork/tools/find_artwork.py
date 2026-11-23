"""Examine the published raster and OCR layout of each located numbered figure leaf.

The printed reproduction register remains authoritative. This separate catalogue records
where the body can be isolated, where the caption starts and why a page-only fallback remains.
"""
import argparse
import csv
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import re

import fitz
import numpy as np
from scipy.ndimage import label, find_objects

BASE=Path(__file__).resolve().parents[1]
DEFAULT_ROOT=BASE.parents[2]


def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))


def save(path,items):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)


def box(value):
    if not value:return None
    return tuple(float(v) for v in value.strip('[]').split(','))


def stringify(b):
    return ','.join(f'{v:.2f}' for v in b) if b is not None else ''


def spaced_runs(flags):
    points=np.flatnonzero(np.diff(np.r_[False,flags,False].astype(int)))
    return zip(points[::2],points[1::2])


def flat_lines(page):
    output=[]
    for blk in page.get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks']:
        for line in blk.get('lines',[]):
            txt=''.join(s['text'] for s in line['spans']).strip()
            if txt:output.append((txt,tuple(line['bbox']),tuple(line['dir']),blk['number']))
    return output


def caption_text(lines,anchor,regex):
    if anchor:
        # The curated anchor may be a title in a sideways caption; search near the actual
        # first line and retain its orientation, not the enclosing block's height.
        candidates=[l for l in lines if abs(l[1][1]-anchor[1])<6 and abs(l[1][0]-anchor[0])<28]
        if not candidates:return anchor,0,'catalog_anchor_only'
        first=min(candidates,key=lambda l:(not bool(regex.match(l[0])),abs(l[1][1]-anchor[1])+abs(l[1][0]-anchor[0])))
    else:
        candidates=[l for l in lines if regex.match(l[0])]
        if len(candidates)!=1:return None,0,'missing_or_ambiguous_caption'
        first=candidates[0]
    if first[2][0]<.9:return first[1],1,'non_horizontal_caption'
    chosen=[first];fbox=first[1];end=fbox[3]
    # Only adjacent same-block caption lines with the same left start are expanded.
    for l in sorted([ll for ll in lines if ll[3]==first[3] and ll[1][1]>fbox[1]+2],key=lambda q:q[1][1]):
        b=l[1]
        if abs(b[0]-fbox[0])>11 or b[1]-end>6 or len(l[0])<4:break
        if re.match(r'^(?:Figure|Table|Plate)\s+[A-Za-z0-9]',l[0],re.I):break
        chosen.append(l);end=max(end,b[3])
    b=(min(l[1][0] for l in chosen),fbox[1],max(l[1][2] for l in chosen),end)
    return b,len(chosen),'same_block_caption_lines'


def image_description(page):
    imgs=page.get_image_info(xrefs=False)
    refs=page.get_images(full=True)
    if len(imgs)!=1 or len(refs)!=1:return 'page_render',None
    im=imgs[0]
    ref=refs[0]
    if tuple(ref[2:4])!=(im['width'],im['height']) or ref[1]:return 'page_render',None
    im['xref']=ref[0]
    a,b,c,d,e,f=im['transform']
    rect=page.rect; frame=im['bbox']
    if (a<=0 or d<=0 or abs(b)>.01 or abs(c)>.01 or page.rotation or
        frame[0]>rect.x0+1 or frame[1]>rect.y0+1 or frame[2]<rect.x1-1 or frame[3]<rect.y1-1):
        return 'page_render',None
    return 'native_raster',im


def earlier_prose(lines,y0,y1):
    # Connected narrative and table entries in the proposed region invalidate a figure-only crop.
    relevant=[l for l in lines if y0+1<(l[1][1]+l[1][3])/2<y1]
    long=[l for l in relevant if len(re.findall(r'\b[A-Za-z]{3,}\b',l[0]))>=7 and len(l[0])>49 and l[2][0]>.85]
    other=[l for l in relevant if re.match(r'^(?:Table|Plate|Fig(?:ure)?)[ .]+\d+',l[0],re.I)]
    return len(long),len(other)


def find_body(gray,page,lines,caption,count):
    if caption is None:return None,'caption unavailable',None
    if count>1:return None,'multiple numbered figure bodies on this page',None
    h,w=gray.shape;W=page.rect.width;H=page.rect.height;sx=w/W;sy=h/H
    cy=caption[1]
    if cy/H<.52:return None,'caption is high on a mixed-layout page',None
    if W>900 or H>950 or W/H>1.12:return None,'foldout, landscape or oversized sheet',None
    mask=gray<175
    margin=max(8,round(w*.025)); lane=mask[:,margin:-margin]
    # Near the caption require a full-page white band, allowing a few isolated scanner specks.
    blank=lane.sum(axis=1)<=max(1,round(w*.003))
    upper=max(0,round((cy-24)*sy));lower=min(h,round((cy+1)*sy))
    separators=[(upper+a,upper+b) for a,b in spaced_runs(blank[upper:lower]) if b-a>=max(3,round(2.2*sy))]
    if not separators:return None,'no page-wide white gap before caption',None
    ystop=separators[-1][0]+1
    headers=[l for l in lines if l[1][1]<52 and l[1][3]<65 and
             (l[1][0]<W*.17 or l[1][2]>W*.83) and
             len(l[0])>4 and (l[0].upper()==l[0] or re.match(r'^SITE\s+\d+',l[0],re.I))]
    # Remove a running header only when followed by an entire white band.
    ystart=8
    if headers:
        header_y=max(q[1][3] for q in headers)
        a=max(0,round((header_y-2)*sy));b=min(h,round((header_y+28)*sy))
        gaps=[(a+i,a+j) for i,j in spaced_runs(blank[a:b]) if j-i>=max(4,round(4*sy))]
        if not gaps:return None,'running header not separated from artwork',None
        ystart=gaps[0][1]
    ystart=max(ystart,round(8*sy))
    if ystop-ystart<120*sy:return None,'artwork interval too short',None
    nprose,nother=earlier_prose(lines,ystart/sy,ystop/sy)
    if nprose or nother:return None,f'intervening prose/table/caption evidence ({nprose},{nother})',None
    # Require visual ink rather than a just a numerical table composed of columns.
    visual=lane[ystart:ystop].copy()
    lab,num=label(visual)
    areas=np.bincount(lab.ravel());areas[0]=0
    if num==0 or max(areas)<95:return None,'no prominent graphic ink component',None
    kept=areas[lab]>=4
    ys,xs=np.nonzero(kept)
    if not xs.size:return None,'no useful source ink',None
    xx0,xx1=int(xs.min()+margin),int(xs.max()+margin+1);yy0,yy1=int(ys.min()+ystart),int(ys.max()+ystart+1)
    if (xx1-xx0)/sx<135 or (yy1-yy0)/sy<115:return None,'small or fragmented illustration',None
    # If potential running text is still present near the top refuse, even where OCR is fragmented.
    for l in lines:
        if yy0/sy-1<=l[1][1]<52 and (l[1][0]<W*.17 or l[1][2]>W*.83) and len(l[0])>6:
            return None,'unresolved possible running header within crop',None
    if yy0/sy<42:
        stop=min(yy1,yy0+round(32*sy))
        bands=[(yy0+i,yy0+j) for i,j in spaced_runs(blank[yy0:stop]) if j-i>=round(8*sy)]
        if bands:
            before=np.flatnonzero(mask[yy0:bands[0][0],:].any(axis=0))
            if len(before) and (before.max()<w*.3 or before.min()>w*.7):
                return None,'unread running header suggested by isolated marginal ink',None
    left=max(0,(xx0-3)/sx);top=max(0,(yy0-3)/sy);right=min(W,(xx1+3)/sx)
    bottom=min((ystop+1)/sy,(yy1+3)/sy,cy-.75)
    if bottom<=top:return None,'invalid drawing extent',None
    body=(left,top,right,bottom)
    return body,'single located figure; clear caption gutter; no intervening long prose; prominent raster ink', gray[yy0:yy1,xx0:xx1]


def coverage_class(region):
    # At 72 dpi a grayscale or halftoned region has high midtone ink or repeated dense image
    # windows. For uncertain graphic type default to original raster without threshold tracing.
    dark=region<105;mid=(region>=105)&(region<228);other=region<228
    ratio=mid.sum()/max(1,other.sum())
    dark_ratio=dark.mean()
    hh,ww=region.shape;tile=20
    tiles=other[:hh//tile*tile,:ww//tile*tile].reshape(hh//tile,tile,ww//tile,tile).mean((1,3))
    dense=float((tiles>.58).mean()) if tiles.size else 1.
    media='monochrome_ink_candidate' if ratio<=.57 and dark_ratio<.20 and dense<.035 else 'raster_tonal_or_uncertain'
    return media,round(float(ratio),4),round(float(dark_ratio),4),round(dense,4)


def inspect(job):
    path,targets,roots,expected_hash=job
    source=roots/path
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if digest!=expected_hash:raise ValueError(f'Source checksum changed: {path}')
    records=[]
    with fitz.open(source) as doc:
        pages=defaultdict(list)
        for item,n,anchor in targets:pages[n].append((item,anchor))
        for n,items in sorted(pages.items()):
            fitz.TOOLS.store_shrink(100)
            page=doc[n-1];lines=flat_lines(page)
            mode,image=image_description(page)
            dct=(image or {})
            gray=None
            if page.rect.width<=900 and page.rect.height<=950 and len(items)==1:
                pix=page.get_pixmap(matrix=fitz.Matrix(1,1),colorspace=fitz.csGRAY,alpha=False)
                gray=np.frombuffer(pix.samples,'u1').reshape(pix.height,pix.width)
            for r,anchor in items:
                id_=r['item_id'];num=re.search(r'(?:FIGURE|\.F)([^.]*)$',id_,re.I).group(1)
                num=num.lstrip('0') or '0'
                pattern=re.compile(r'^Fig(?:ure)?[.\s]+0*'+re.escape(num)+r'\s*[.:(\-]',re.I)
                cap,num_lines,cap_status=caption_text(lines,anchor,pattern)
                if gray is None or cap_status=='non_horizontal_caption':
                    b=None;reason='multiple figures, oversized sheet, or rotated caption; inspect source page';region=None
                else:b,reason,region=find_body(gray,page,lines,cap,len(items))
                media,tones,ink,dense=coverage_class(region) if region is not None else ('','','','')
                records.append(dict(item_id=id_,series=r['series'],doc_id=r['doc_id'],site=r['site'],
                    source_path=path,source_sha256=digest,source_pdf_page=n,source_url=r['source_url'].split('#')[0]+f'#page={n}',
                    page_width_pt=round(page.rect.width,2),page_height_pt=round(page.rect.height,2),
                    body_bbox_pt=stringify(b),body_evidence='machine_candidate' if b else 'page_only',
                    caption_bbox_pt=stringify(cap),caption_scope=cap_status,caption_matched_lines=num_lines,
                    media_class=media,trace_ok=0,source_image_mode=mode,source_image_xref=dct.get('xref',''),
                    source_raster_width=dct.get('width',''),source_raster_height=dct.get('height',''),
                    reason=reason,gray_midtone_fraction=tones,dark_pixel_fraction=ink,dense_tile_fraction=dense))
    return records


def gather(root,primary,data,workers):
    inventory={r['local_path']:r for r in read_inventory(root)}
    figures=[r for r in rows(root/'data/figure_reproduction.csv') if r['object_scope']=='numbered_figure']
    anchors={}
    for r in rows(root/'ir/core/chapter_item_locations.csv'):
        if r['anchor_kind'] in ('caption_text_layer','continued_caption_text_layer','page_image_checked'):
            anchors[(r['item_id'],int(r['pdf_page']))]=box(r['caption_bbox_xyxy_pt'])
    for r in rows(root/'sr/core/caption_anchors.csv'):
        if r['kind']=='figure' and r['pdf_page'] and r['bbox_pt'] and re.match(r'^Figure\s+[^ .]+[. ]+\(?cont',r['caption_text'],re.I):
            anchors[(r['item_id'],int(r['pdf_page']))]=box(r['bbox_pt'])
    for r in rows(root/'sr/core/edition2/data/objects.csv'):
        if r['kind']=='figure' and r['status']=='accepted' and r['pdf_page']:
            anchors[(r['item_id'],int(r['pdf_page']))]=box(r['source_bbox_pt'])
    for r in rows(root/'plates/core/data/foldouts.csv'):
        item=f"IR{int(r['chapter']):02}.F{int(r['figure']):02}"
        anchors[(item,1)]=tuple(float(r[k]) for k in ('caption_anchor_left_pt','caption_anchor_top_pt','caption_anchor_right_pt','caption_anchor_bottom_pt'))
    bypath=defaultdict(list)
    for r in figures:
        for n in map(int,r['source_pdf_pages'].split('|')):
            bypath[r['source_path']].append((r,n,anchors.get((r['item_id'],n))))
    jobs=[(path,items,primary,inventory[path]['sha256']) for path,items in bypath.items()]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        examined=[r for doc in pool.map(inspect,jobs) for r in doc]
    return apply_readings(examined,data,len(jobs))


def apply_readings(examined,data,source_count):
    manual={}
    for path in sorted(data.glob('manual_*.csv')):
        for r in rows(path):
            key=r['item_id'],int(r['pdf_page'])
            if key in manual:raise ValueError(f'Duplicate manual reading: {key}')
            manual[key]=r
    for e in examined:
        key=e['item_id'],e['source_pdf_page']
        if key not in manual:continue
        m=manual.pop(key)
        b=box(m['body_bbox_pt']);c=box(m['caption_bbox_pt'])
        if b:
            assert 0<=b[0]<b[2]<=e['page_width_pt']+.1 and 0<=b[1]<b[3]<=e['page_height_pt']+.1,key
        if c:
            assert 0<=c[0]<c[2]<=e['page_width_pt']+.1 and 0<=c[1]<c[3]<=e['page_height_pt']+.1,key
        e.update(body_bbox_pt=stringify(b),body_evidence='visual_confirmed' if b else 'page_only',
                 media_class=m['media_class'],trace_ok=int(m['trace_ok']) if b else 0,reason=m['note'])
        if c:e.update(caption_bbox_pt=stringify(c),caption_scope='visually_confirmed_caption')
        elif 'caption' in m['note'].lower() and ('not repeat' in m['note'].lower() or 'no caption' in m['note'].lower() or 'no printed caption' in m['note'].lower() or 'no repeated caption' in m['note'].lower()):
            e.update(caption_bbox_pt='',caption_scope='visually_checked_absent_caption',caption_matched_lines=0)
    if manual:raise ValueError(f'Unmatched manual rows: {list(manual)[:10]}')
    assert len({r['item_id'] for r in examined})==1206
    save(data/'artwork_pages.csv',examined)
    stats=dict(numbered_figures=1206,located_figure_pages=len(examined),individual_source_leaves=len({(r['source_path'],r['source_pdf_page']) for r in examined}),
               source_pdfs_checked=source_count,body_evidence=dict(Counter(r['body_evidence'] for r in examined)),
               body_identifiers_with_one_or_more_boxes=len({r['item_id'] for r in examined if r['body_bbox_pt']}),
               body_identifiers_with_all_located_pages=sum(all(x['body_bbox_pt'] for x in examined if x['item_id']==id_) for id_ in {r['item_id'] for r in examined}),
               trace_approved_leaves=sum(r['trace_ok'] for r in examined),
               embedded_source_modes=dict(Counter(r['source_image_mode'] for r in examined)))
    (data/'coverage.json').write_text(json.dumps(stats,indent=2)+'\n');print(json.dumps(stats),flush=True)


def read_inventory(root):
    import gzip
    with gzip.open(root/'data/source_inventory.csv.gz','rt') as f:return list(csv.DictReader(f))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path,help='Leg138 folder containing ir/primary, sr/primary, sppr/primary and plates/primary')
    p.add_argument('--root',type=Path,default=DEFAULT_ROOT);p.add_argument('--out',type=Path,default=BASE/'data');p.add_argument('--workers',type=int,default=4)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);gather(a.root,a.primary,a.out,a.workers)
