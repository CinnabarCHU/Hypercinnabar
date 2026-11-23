"""Validate the geometry and local targets in the published source-region views."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import argparse,json
import fitz
from PIL import Image
from companions import read,digest
from verify_edition import Links

def check(out):
    docs={r['doc_id']:r for r in read(out/'documents.csv')}
    page_map={(r['doc_id'],int(r['source_page'])):r for r in read(out/'pages.csv')}
    regions=read(out/'source_regions.csv');pngs=0;links=0
    for r in regions:
        if r['pdf_page']:
            p=page_map[(r['doc_id'],int(r['pdf_page']))]
            assert r['paired_witness_page']==p['edition_witness']
        if not r['preview_file']:continue
        window=fitz.Rect([float(x) for x in r['source_box_pt'].split(',')])
        page=fitz.Rect(0,0,float(p['source_width_pt']),float(p['source_height_pt']))
        bounds=((window & page)*fitz.Matrix(1.4,1.4)).irect
        with Image.open(out/r['preview_file']) as img:
            assert img.size==(bounds.width,bounds.height),(r['item_id'],r['pdf_page'],img.size,bounds)
            img.verify()
        pngs+=1
    for f in list((out/'regions').glob('*.html'))+list((out/'html').glob('*.html'))+[out/'index.html']:
        links_parser=Links();links_parser.feed(f.read_text())
        for url in links_parser.paths:
            path=unquote(urlsplit(url).path)
            assert not path or (f.parent/path).is_file(),(f.name,url)
            links+=1
    assert len(list((out/'regions/crops').glob('*.png')))==pngs
    return {'verified_crop_png_files':pngs,'verified_relative_browser_links':links,'indexed_region_rows':len(regions)}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);a=p.parse_args();result=check(a.output)
    (a.output/'region_file_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
