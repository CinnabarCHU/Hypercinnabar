"""Reproduce visually reviewed SP/PR figure and caption crops using original PDF coordinates.

Coarse optical search boxes exclude running titles, folios and other composition.
Dark connected components tighten these regions. Full bitonal/grayscale source
imagery within the crop is retained by the consuming renderer.
"""
import argparse
import csv
import hashlib
from pathlib import Path

import fitz
import numpy as np
from scipy.ndimage import find_objects, label

# Rectangle coordinates in PDF points from upper left. Each row identifies one PDF page,
# with body search area followed by a verified search area for all printed caption lines.
# The printed legend belongs with the body. An absent repeated caption stays absent.
SP = {
    11: [(65,78,592,476),(102,476,561,525)],
    12: [(44,153,576,363),(67,404,534,566)],
    13: [(52,64,577,667),(86,668,559,715)],
}
PR = {
    31: [(70,162,505,498),(97,504,478,590)],
    32: [(76,76,662,494),(96,510,630,541)],
    33: [(90,108,495,687),(72,688,542,761)],
    34: [(142,108,535,658),None],
    35: [(38,96,665,452),(104,493,653,531)],
    36: [(75,111,548,741),(68,610,306,706)],
    37: [(107,108,505,696),(90,696,553,768)],
    38: [(110,108,507,666),None],
    39: [(45,106,656,483),(84,483,627,521)],
    40: [(98,109,545,741),(82,609,321,708)],
    41: [(107,108,505,695),(81,696,551,768)],
    42: [(114,111,517,691),(82,692,552,764)],
    43: [(109,108,505,671),None],
    44: [(48,104,668,447),(102,480,657,522)],
    45: [(93,109,547,738),(83,602,325,702)],
    46: [(109,108,505,693),(85,694,555,769)],
    47: [(110,108,506,554),None],
    48: [(35,110,644,482),(58,482,617,516)],
    49: [(112,109,547,742),(86,559,329,658)],
    50: [(76,128,520,597),(109,598,501,645)],
    51: [(105,110,515,564),(73,566,543,639)],
    52: [(29,104,645,464),(75,501,636,541)],
    53: [(97,109,548,747),(85,625,328,722)],
    54: [(105,108,505,693),(67,691,536,763)],
    55: [(109,108,505,667),None],
    56: [(93,108,494,479),(58,481,527,554)],
    57: [(46,70,671,519),(94,525,649,562)],
    58: [(72,109,522,748),(62,621,300.5,714)],
    59: [(111,108,512,695),(80,691,547,764)],
    60: [(96,110,490,673),(64,678,532,746)],
    61: [(131,108,518,552),None],
    62: [(50,115,520,571),(84,570,502,609)],
    63: [(99,110,549,744),(84,617,326,716)],
    64: [(95,108,491,691),(64,690,533,761)],
    65: [(113,108,516,668),None],
    66: [(95,109,486,484),(58,486,529,558)],
    67: [(37,66,662,511),(76,511,633,547)],
    68: [(67,109,507,749),(62,629,299.5,723)],
    69: [(93,108,493,693),(65,696,535,770)],
    70: [(50,73,672,443),(95,442,653,485)],
    71: [(100,110,557,747),(90,626,328,726)],
    72: [(62,108,447,495),(62,499,532,570)],
    73: [(51,76,671,444),(105,493,663,533)],
    74: [(59,115,495,744),(44,621,284,716)],
    75: [(137,111,520,406),(83,414,553,492)],
    76: [(31,74,674,498),(118,499,618,524)],
    77: [(87,169,538,604),(81,608,553,670)],
}
RATE = {36,40,45,49,53,58,63,68,71,74,77}
SEISMIC = {35,39,44,48,52,57,62,67,70,73,76}
EXPECTED_HASH = {'SP':'7934144bec5ec839c5a95c113cec9a266ac2ad5ef4b97b50cd44ffad3d534e37','PR':'48f7d7e22f672f499c38d610d995ad713874cfd01bc29516cf6b2f4cbe6d18c5'}

def bounds(page, box):
    """Tighten within a reviewed area and leave two points of breathing room."""
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=fitz.Rect(box), colorspace=fitz.csGRAY)
    gray = np.frombuffer(pix.samples,dtype='uint8').reshape(pix.height, pix.width)
    labels, n = label(gray < 183)
    sizes = np.bincount(labels.ravel(), minlength=n+1)
    components = [obj for i,obj in enumerate(find_objects(labels),1)
                  if obj and sizes[i] >= 4]
    if not components:
        raise ValueError(f'Empty reviewed region on page {page.number+1}')
    y0=min(s[0].start for s in components); y1=max(s[0].stop for s in components)
    x0=min(s[1].start for s in components); x1=max(s[1].stop for s in components)
    return (max(box[0],(pix.x+x0)/2-2),max(box[1],(pix.y+y0)/2-2),
            min(box[2],(pix.x+x1)/2+2),min(box[3],(pix.y+y1)/2+2))

def describe(doc, page):
    if doc=='SP' and page in (12,13):
        return ('black_white_line_art',1,'Axes, labels, arrows or station marks belong to the artwork.')
    if (doc=='SP' and page==11) or (doc=='PR' and page in (31,32,50)):
        return ('grayscale_cartographic_art',0,'Shaded fields, fills or halftone cartography are part of the image.')
    if page in SEISMIC:
        return ('grayscale_seismic_profile',0,'Keep the continuous-tone seismic image, scale, navigation annotations and line labels.')
    if page in RATE:
        return ('black_white_line_plot',1,'Contains published thin and thick lines, plotted symbols, axes and ticks.')
    return ('black_white_composite_line_art',1,'Keep lithology patterns, polarity, labels, printed traces and any key.')
    
def fmt(b):
    return ','.join(f'{x:g}' for x in b) if b else ''

def main():
    ap=argparse.ArgumentParser();ap.add_argument('primary',type=Path);ap.add_argument('items',type=Path);ap.add_argument('output',type=Path)
    a=ap.parse_args()
    with a.items.open(newline='') as f:
        ids={(r['doc_id'],p):r['item_id'] for r in csv.DictReader(f) if r['kind']=='figure'
             for p in range(int(r['pdf_first']),int(r['pdf_last'])+1)}
    rows=[]
    for doc,reg in [('SP',SP),('PR',PR)]:
        source=a.primary/(doc+'.pdf')
        if doc in EXPECTED_HASH:
            assert hashlib.sha256(source.read_bytes()).hexdigest()==EXPECTED_HASH[doc]
        with fitz.open(source) as pdf:
            for p,(body,cap) in reg.items():
                media,trace,note=describe(doc,p)
                if not cap:
                    note+=' Printed continuation has no repeated caption.'
                elif doc=='PR' and p in RATE-{77}:
                    trace=0
                    note+=' mask_caption_in_body: The original caption is in the lower-left empty panel. Exclude its rectangle when exporting the complete five-panel body.'
                row=[ids[doc,p],p,fmt(bounds(pdf[p-1],body)),fmt(bounds(pdf[p-1],cap)) if cap else '',media,trace,note]
                rows.append(row)
    assert len(rows)==50 and len({r[0] for r in rows})==39
    assert len([r for r in rows if not r[3]])==7
    with a.output.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(('item_id','pdf_page','body_bbox_pt','caption_bbox_pt','media_class','trace_ok','note'));w.writerows(rows)

if __name__=='__main__':
    main()
