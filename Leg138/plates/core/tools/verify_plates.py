"""Verify preserved source files, their native JPEG streams, documented crops, and index coverage."""
import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

import fitz
from PIL import Image
from optical_windows import get_native


def load_rows(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def verify(primary, root):
    data = root / 'data'
    assets = load_rows(data / 'plate_sources.csv')
    witness = load_rows(data / 'plate_directory_witness.csv')
    pages = load_rows(data / 'vcd_pages.csv')
    photos = load_rows(data / 'native_photo_catalog.csv')
    foldouts = load_rows(data / 'foldouts.csv')
    slides = load_rows(data / 'smear_pages.csv')
    stations = load_rows(data / 'station_summary.csv')
    for item in assets + witness:
        path = primary / item['source_path']
        assert path.stat().st_size == int(item['bytes']), path
        assert sha256(path.read_bytes()) == item['sha256'], path
    assert len(assets) == len({a['source_path'] for a in assets}) == 617
    assert len(witness) == 1
    for photo in photos:
        with fitz.open(primary / photo['source_path']) as pdf:
            assert len(pdf) == 1
            (obj,) = pdf[0].get_images(full=True)
            assert obj[0] == int(photo['xref']) and obj[1] == 0
            assert obj[2:6] == (int(photo['width_px']), int(photo['height_px']), 8, 'DeviceRGB')
            assert obj[8] == 'DCTDecode'
            assert sha256(pdf.xref_stream_raw(obj[0])) == photo['native_stream_sha256']
    regions = load_rows(data / 'optical_regions.csv')
    saved = {(r['core_id'],r['role']): r for r in load_rows(root / 'optical' / 'patches.csv')}
    for region in regions:
        entry = saved[(region['core_id'],region['role'])]
        source = primary / region['source_path']
        full, jpeg, obj = get_native(source)
        assert sha256(jpeg) == region['jpeg_sha256']
        assert sha256(source.read_bytes()) == region['source_sha256']
        box = tuple(int(region[key]) for key in ('left_px','top_px','right_px_exclusive','bottom_px_exclusive'))
        patch = root / 'optical' / entry['file']
        with Image.open(patch) as im:
            assert im.tobytes() == full.crop(box).tobytes()
            assert sha256(im.tobytes()) == entry['decoded_rgb_sha256']
        assert sha256(patch.read_bytes()) == entry['png_sha256']
    with gzip.open(data / 'plate_page_text.jsonl.gz','rt',encoding='utf-8') as f:
        indexed_pages = [json.loads(line) for line in f]
    assert len(set((r['source_path'],r['pdf_page']) for r in indexed_pages)) == len(indexed_pages) == 620
    assert len(pages) == 592 and len(photos) == 593 and len(slides) == 26 and len(foldouts) == 13
    for station in stations:
        s = station['site']
        assert int(station['photo_pdf_count']) == sum(p['core_id'].startswith(s) for p in photos)
        assert int(station['vcd_pdf_pages']) == sum(p['site'] == s for p in pages)
        assert int(station['smear_pdf_pages']) == sum(p['site'] == s for p in slides)
        assert (len([r for r in regions if r['site'] == s]), len([r for r in foldouts if r['scope'] == s])) == (2,1)
    assert len(stations) == 11 and len(regions) == len(saved) == 22
    return dict(source_pdfs=len(assets), source_pdf_bytes=sum(int(a['bytes']) for a in assets),
                directory_listings=len(witness),directory_listing_bytes=int(witness[0]['bytes']),
                sites=len(stations),native_photo_streams_checked=len(photos),
                native_raster_height_counts=dict(Counter(row['height_px'] for row in photos)),
                vcd_pages=len(pages),vcd_page_identifier_evidence_counts=dict(Counter(row['identity_evidence'] for row in pages)),
                smear_slide_pages=len(slides),foldout_figures=len(foldouts),searchable_source_pages=len(indexed_pages),
                native_pixel_crops_checked=len(regions),coring_table_ids_without_separate_photo=len(load_rows(data / 'core_photo_gaps.csv')))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('primary',type=Path)
    p.add_argument('core',type=Path)
    p.add_argument('--output',type=Path)
    a = p.parse_args()
    verified = json.dumps(verify(a.primary,a.core),indent=2) + '\n'
    if a.output:
        a.output.write_text(verified,encoding='utf-8')
    print(verified,end='')
