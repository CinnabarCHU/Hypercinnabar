"""Pin every native RGB crop to a byte checksum and compare independently hand-marked first-edition windows."""
import argparse
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path

from export_regions import BASE,rows,get_image,bbox


def crop_hashes(args):
    primary,photo,records=args
    full=get_image(primary,photo)
    out=[]
    for r in records:
        x0,y0,x1,y1=bbox(r)
        if not (0<=x0<x1<=full.width and 0<=y0<y1<=full.height):raise ValueError(r['roi_id'])
        patch=full.crop((x0,y0,x1,y1))
        out.append(dict(roi_id=r['roi_id'],core_id=r['core_id'],width_px=x1-x0,height_px=y1-y0,
                        native_decoded_rgb_sha256=hashlib.sha256(patch.tobytes()).hexdigest()))
    return out


def coverage(anchor,boxes):
    # Candidate windows in one lane are disjoint along y. Report the fraction of original anchor pixels intersected.
    ax,ay,bx,by=anchor
    intersections=sum(max(0,min(bx,x1)-max(ax,x0))*max(0,min(by,y1)-max(ay,y0)) for x0,y0,x1,y1 in boxes)
    return intersections/((bx-ax)*(by-ay))


def run(primary,data,old_data,workers):
    photos=rows(data/'photos.csv');regions=rows(data/'regions.csv');lanes=rows(data/'lanes.csv')
    assert len(photos)==593 and len({r['core_id'] for r in photos})==593
    assert len(regions)==len({r['roi_id'] for r in regions})
    by_core=defaultdict(list)
    for r in regions:by_core[r['core_id']].append(r)
    for p in photos:
        roles=Counter(x['role'] for x in by_core[p['core_id']])
        assert (roles['photographed_liner'],roles['sediment_candidate'],roles['board_background'],roles['printed_ruler'])==tuple(int(p[x]) for x in ('liner_rois','material_rois','background_rois','ruler_rois'))
        for ex in (r for r in by_core[p['core_id']] if r['role']=='reviewed_non_sediment_band'):
            candidate=[bbox(r) for r in by_core[p['core_id']] if r['role']=='sediment_candidate' and ex['lane_ordinal']==r['lane_ordinal']]
            assert coverage(bbox(ex),candidate)==0,ex['roi_id']
    with ProcessPoolExecutor(max_workers=workers) as pool:
        harvested=list(pool.map(crop_hashes,[(primary,p,by_core[p['core_id']]) for p in photos],chunksize=3))
    flat=[r for per_photo in harvested for r in per_photo]
    with (data/'roi_rgb_checksums.csv.gz').open('wb') as target:
        with gzip.GzipFile(filename='',fileobj=target,mode='wb',mtime=0) as bundle:
            with io.TextIOWrapper(bundle,encoding='utf-8',newline='') as output:
                w=csv.DictWriter(output,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
    evidence=[]
    for prior in rows(old_data/'optical_regions.csv'):
        core=prior['core_id']
        if prior['role']=='printed_ruler':
            targets=['printed_ruler']
        else:targets=['photographed_liner','sediment_candidate']
        for role in targets:
            boxes=[bbox(r) for r in by_core[core] if r['role']==role and (role=='printed_ruler' or r['lane_ordinal']==prior['printed_section'])]
            evidence.append(dict(core_id=core,edition_one_role=prior['role'],edition_two_role=role,
                 original_window_coverage_fraction=f'{coverage(bbox(prior),boxes):.4f}'))
    with (data/'anchor_overlap.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,list(evidence[0]));w.writeheader();w.writerows(evidence)
    result=dict(photos=len(photos),verified_pdf_and_jpeg_sources=len(photos),attempted_columns=len(lanes),
       layout_grades=dict(Counter(p['geometric_status'] for p in photos)),roi_counts=dict(Counter(r['role'] for r in regions)),
       columns_by_evidence=dict(Counter(l['layout_evidence'] for l in lanes)),
       no_sediment_candidates=[p['core_id'] for p in photos if p['material_rois']=='0'],columns_without_sediment_candidate=sum(l['material_region_count']=='0' for l in lanes),
       native_rgb_checksums=len(flat),inherited_manual_windows=22,
       crop_decode='RGB byte order, Pillow decoder, no resizing or color correction; hash per ROI excludes PNG headers')
    (data/'photo_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path)
    p.add_argument('--data',type=Path,default=BASE/'data');p.add_argument('--catalog',type=Path,default=BASE.parent/'data')
    p.add_argument('--workers',type=int,default=4)
    a=p.parse_args();run(a.primary,a.data,a.catalog,a.workers)
