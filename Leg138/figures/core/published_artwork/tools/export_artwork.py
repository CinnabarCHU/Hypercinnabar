"""Export the numbered artwork as published. A threshold trace is an optional visual derivative."""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import warnings

import fitz
import numpy as np
from PIL import Image

from find_artwork import BASE, box, image_description, rows


def sha(value):
    return hashlib.sha256(value).hexdigest()


def digest_file(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def bounds_in_image(bounds, transform, size):
    a,_,_,d,e,f=transform
    w,h=size
    return (max(0,math.floor((bounds[0]-e)*w/a)),max(0,math.floor((bounds[1]-f)*h/d)),
            min(w,math.ceil((bounds[2]-e)*w/a)),min(h,math.ceil((bounds[3]-f)*h/d)))


def region(doc, page, info, bounds, image_cache):
    """Return original decoded image window whenever the source leaf is one axis-aligned image."""
    if info is not None:
        xref=info['xref']
        if xref not in image_cache:
            stream=doc.xref_stream_raw(xref)
            original=stream if doc.xref_get_key(xref,'Filter')==('name','/DCTDecode') else doc.extract_image(xref)['image']
            try:
                # The two verified 300-dpi foldouts exceed Pillow's decompression warning threshold.
                # Preserve the hard upper bound, and check dimensions against the PDF before decoding.
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore',Image.DecompressionBombWarning)
                    decoded=Image.open(io.BytesIO(original))
                if decoded.size!=(info['width'],info['height']):raise ValueError('Image header dimensions differ from PDF')
                decoded.load()
            except OSError:
                pix=fitz.Pixmap(doc,xref)
                decoded=Image.frombytes({1:'L',3:'RGB',4:'CMYK'}[pix.n],(pix.width,pix.height),pix.samples)
            image_cache[xref]=(decoded,sha(stream))
        decoded,stream_hash=image_cache[xref]
        pixel_rect=bounds_in_image(bounds,info['transform'],decoded.size)
        return decoded.crop(pixel_rect),dict(pixel_basis='native_embedded_image',xref=xref,
                     stream_sha256=stream_hash,source_size=list(decoded.size),source_mode=decoded.mode,
                     pdf_image_transform=list(info['transform']),source_pixel_bbox=list(pixel_rect))
    pix=page.get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(bounds),colorspace=fitz.csRGB,alpha=False)
    decoded=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    return decoded,dict(pixel_basis='144_dpi_page_render',source_pixel_bbox=list(pix.irect))


def mask_rectangles(mask):
    """Coalesce exact horizontal ink runs on successive rows. Coordinates are pixel edges."""
    opened={}
    for y,row in enumerate(mask):
        edges=np.flatnonzero(np.diff(np.r_[False,row,False].astype(np.int8))).tolist()
        current=set(zip(edges[::2],edges[1::2]))
        for span in sorted(opened.keys()-current):
            yield span[0],opened.pop(span),span[1],y
        for span in current-opened.keys():
            opened[span]=y
    for (x0,x1),y0 in sorted(opened.items()):
        yield x0,y0,x1,mask.shape[0]


def trace(crop):
    mask=np.asarray(crop.convert('L'))<128
    h,w=mask.shape
    elements=[];subpaths=[];count=0
    for x0,y0,x1,y1 in mask_rectangles(mask):
        dx=x1-x0;dy=y1-y0
        subpaths.append(f'M{x0} {y0}h{dx}v{dy}h-{dx}z')
        count+=1
        if len(subpaths)==512:
            elements.append('<path d="' + ''.join(subpaths) + '"/>')
            subpaths=[]
    if subpaths:elements.append('<path d="' + ''.join(subpaths) + '"/>')
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
         '<title>Printed black ink silhouette, native pixel grid</title>'
         f'<rect width="{w}" height="{h}" fill="white"/>'
         +''.join(elements)+'</svg>\n').encode()
    with fitz.open(stream=svg,filetype='svg') as doc:
        raster=doc[0].get_pixmap(alpha=False,colorspace=fitz.csGRAY)
        if (raster.width,raster.height)!=(w,h):raise ValueError('SVG output dimensions changed')
        ink=np.frombuffer(raster.samples,np.uint8).reshape(h,w)<128
    diff=int(np.count_nonzero(mask!=ink))
    if diff:raise ValueError(f'Trace lost alignment: {diff} changed pixels')
    check=dict(pixel_width=w,pixel_height=h,black_pixels=int(mask.sum()),rectangles=count,
               threshold='Pillow L < 128',mask_sha256=sha(np.packbits(mask).tobytes()),
               rendered_mask_sha256=sha(np.packbits(ink).tobytes()),mismatch_pixels=diff,svg_sha256=sha(svg))
    return svg,check


def overlap(one,two):
    if one is None or two is None:return None
    rect=(max(one[0],two[0]),max(one[1],two[1]),min(one[2],two[2]),min(one[3],two[3]))
    return rect if rect[2]>rect[0] and rect[3]>rect[1] else None


def export_page(doc, r, directory, component, use_candidates, with_trace):
    n=int(r['source_pdf_page']);page=doc[n-1];stem=f"{r['item_id']}.p{n:03}"
    result=dict(item_id=r['item_id'],source_path=r['source_path'],source_pdf_page=n,source_url=r['source_url'],
                source_pdf_sha256=r['source_sha256'],body_evidence=r['body_evidence'],caption_scope=r['caption_scope'],
                media_class=r['media_class'],reading_note=r['reason'],files={})
    body=box(r['body_bbox_pt']);caption=box(r['caption_bbox_pt']);clipping=overlap(body,caption)
    permit=(r['body_evidence']=='visual_confirmed' or (use_candidates and r['body_evidence']=='machine_candidate'))
    components=[]
    if component in ('auto','body') and body and permit:components.append(('body',body))
    if component=='caption' or (component=='auto' and components):
        if caption:components.append(('caption',caption))
    if not components:
        path=directory/f'{stem}.source-page.pdf'
        with fitz.open() as leaf:
            leaf.insert_pdf(doc,from_page=n-1,to_page=n-1)
            leaf.save(path,garbage=3,deflate=True)
        result['files']['source_page']=dict(file=path.name,sha256=digest_file(path),mode='complete_source_leaf',
                             reason='requested original page' if component=='page' else 'independent crop unavailable or requires opt-in')
    mode,info=image_description(page) if components else ('',None)
    image_cache={}
    for name,bounds in components:
        crop,origin=region(doc,page,info,bounds,image_cache)
        # LEG 138 archival color/grayscale pages use RGB, L or bilevel. Other source modes
        # are retained losslessly in TIFF, rather than silently converting them to RGB PNG.
        extension='png' if crop.mode in ('1','L','LA','RGB','RGBA','P','I','I;16') else 'tif'
        path=directory/f'{stem}.{name}.{extension}'
        crop.save(path)
        with Image.open(path) as check:
            if check.mode!=crop.mode or check.tobytes()!=crop.tobytes():raise ValueError('Lossless crop verification failed')
        piece=dict(file=path.name,sha256=digest_file(path),decoded_sha256=sha(crop.tobytes()),mode=crop.mode,
                   requested_bbox_pt=list(bounds),**origin)
        result['files'][name]=piece
        if name=='body' and clipping:
            piece['caption_overlap_pt']=list(clipping)
            if 'mask_caption_in_body' in r['reason']:
                if info:
                    rect=bounds_in_image(clipping,info['transform'],tuple(origin['source_size']))
                else:
                    rect=(math.floor(clipping[0]*2),math.floor(clipping[1]*2),math.ceil(clipping[2]*2),math.ceil(clipping[3]*2))
                x0,y0,_,_=origin['source_pixel_bbox']
                local=[rect[0]-x0,rect[1]-y0,rect[2]-x0,rect[3]-y0]
                alpha=Image.new('L',crop.size,255);alpha.paste(0,tuple(local))
                p=directory/f'{stem}.body-alpha.png';alpha.save(p)
                result['files']['body_alpha']=dict(file=p.name,sha256=digest_file(p),body_relative_caption_bbox_px=local,
                                                  convention='0 hides embedded caption, 255 retains original raster')
        if name=='body' and with_trace:
            if r['trace_ok']=='1' and mode=='native_raster' and 'mask_caption_in_body' not in r['reason']:
                svg,checks=trace(crop)
                svgpath=directory/f'{stem}.ink.svg';svgpath.write_bytes(svg)
                result['files']['trace']=dict(file=svgpath.name,source_crop_decoded_sha256=piece['decoded_sha256'],**checks)
            else:result['trace_status']='ineligible for a native printed ink silhouette; original raster retained'
    if with_trace and 'body' not in result['files']:result['trace_status']='body unavailable; original leaf retained'
    return result


def export(records, primary, out, component='auto', use_candidates=False, with_trace=False):
    out.mkdir(parents=True,exist_ok=True)
    sources={}
    for r in records:sources.setdefault(r['source_path'],[]).append(r)
    output=[]
    for name,rr in sources.items():
        path=primary/name
        if not path.exists():raise FileNotFoundError(f'{path} missing. Source URL: {rr[0]["source_url"].split("#")[0]}')
        if digest_file(path)!=rr[0]['source_sha256']:raise ValueError(f'{path}: primary source hash differs from indexed witness')
        with fitz.open(path) as doc:
            for r in rr:output.append(export_page(doc,r,out,component,use_candidates,with_trace))
    return output


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('primary',type=Path,help='Leg138 directory containing archived original PDF paths')
    parser.add_argument('item_id',help='numbered figure ID from the reproduction register')
    parser.add_argument('out',type=Path)
    parser.add_argument('--page',type=int,help='only this source PDF page (1-based)')
    parser.add_argument('--component',choices=['auto','body','caption','page'],default='auto')
    parser.add_argument('--accept-candidate',action='store_true',help='opt in to unconfirmed machine bounds')
    parser.add_argument('--trace',action='store_true',help='render approved monochrome printed ink as aligned SVG')
    parser.add_argument('--index',type=Path,default=BASE/'data/artwork_pages.csv')
    a=parser.parse_args()
    matched=[r for r in rows(a.index) if r['item_id'].upper()==a.item_id.upper() and (a.page is None or int(r['source_pdf_page'])==a.page)]
    if not matched:parser.error('Figure or source page not found')
    out=export(matched,a.primary,a.out,a.component,a.accept_candidate,a.trace)
    manifest=a.out/f"{matched[0]['item_id']}.manifest.json"
    manifest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(manifest)
