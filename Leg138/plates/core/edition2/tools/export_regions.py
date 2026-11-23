"""Export exact native JPEG coordinate boxes as lossless PNGs, with pixel and file checksums."""
from collections import defaultdict
import argparse
import csv
import hashlib
import gzip
import io
from pathlib import Path

import fitz
from PIL import Image

BASE=Path(__file__).resolve().parents[1]


def rows(path):
    with path.open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))


def digest(b):
    return hashlib.sha256(b).hexdigest()


def get_image(primary,photo):
    path=primary / photo['source_path']
    binary=path.read_bytes()
    if digest(binary)!=photo['pdf_sha256']:
        raise ValueError(f'PDF checksum: {path}')
    with fitz.open(stream=binary,filetype='pdf') as doc:
        raw=doc.xref_stream_raw(int(photo['pdf_image_xref']))
    if digest(raw)!=photo['jpeg_sha256']:
        raise ValueError(f'Native JPEG checksum: {path}')
    image=Image.open(io.BytesIO(raw))
    if image.mode!='RGB' or image.size!=(int(photo['width_px']),int(photo['height_px'])):
        raise ValueError(f'Native JPEG geometry: {path}')
    image.load()
    return image


def bbox(region):
    return tuple(int(region[key]) for key in ('left_px','top_px','right_px_exclusive','bottom_px_exclusive'))


def export(primary,data,out,cores,roles,ids,all_cores):
    photos={r['core_id']:r for r in rows(data/'photos.csv')}
    by_core=defaultdict(list)
    selected_ids=set()
    for region in rows(data/'regions.csv'):
        if ids and region['roi_id'] not in ids:continue
        if roles and region['role'] not in roles:continue
        if cores and region['core_id'] not in cores:continue
        selected_ids.add(region['roi_id']);by_core[region['core_id']].append(region)
    if not (all_cores or cores or ids):
        raise ValueError('Choose one or more --core/--roi, or use --all to export the complete selection.')
    if set(cores)-photos.keys() or set(ids)-selected_ids or not by_core:
        raise ValueError('Unknown core, unknown ROI, or empty selection.')
    out.mkdir(parents=True,exist_ok=True)
    fingerprints={}
    catalogue=data/'roi_rgb_checksums.csv.gz'
    if catalogue.exists():
        with gzip.open(catalogue,'rt',encoding='utf-8') as stream:
            fingerprints={r['roi_id']:r['native_decoded_rgb_sha256'] for r in csv.DictReader(stream)}
    metadata=[]
    for core,regions in by_core.items():
        photo=photos[core];image=get_image(primary,photo)
        for region in regions:
            box=bbox(region);patch=image.crop(box)
            pixel_hash=digest(patch.tobytes())
            if fingerprints and fingerprints.get(region['roi_id'])!=pixel_hash:
                raise ValueError(f"Decoder or geometry changed for {region['roi_id']}")
            name=region['roi_id']+'.png'
            path=out/name;patch.save(path,optimize=True)
            with Image.open(path) as roundtrip:
                assert roundtrip.mode=='RGB' and roundtrip.tobytes()==patch.tobytes(),name
            metadata.append(dict(**region,source_path=photo['source_path'],pdf_sha256=photo['pdf_sha256'],
                  jpeg_sha256=photo['jpeg_sha256'],output_file=name,
                  decoded_rgb_sha256=pixel_hash,png_sha256=digest(path.read_bytes())))
    with (out/'export_manifest.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(metadata[0]));w.writeheader();w.writerows(metadata)
    return len(metadata)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('primary',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--data',type=Path,default=BASE/'data')
    p.add_argument('--core',action='append',default=[])
    p.add_argument('--role',action='append',choices=['printed_ruler','board_background','photographed_liner','sediment_candidate','reviewed_non_sediment_band'],default=[])
    p.add_argument('--roi',action='append',default=[])
    p.add_argument('--all',action='store_true')
    a=p.parse_args();print(export(a.primary,a.data,a.output,a.core,a.role,a.roi,a.all),'native crops')
