"""Extract native RGB windows from the single-image source PDF, with strict source and box checks.

optical_regions.csv uses zero-based JPEG pixel coordinates (left/top inclusive, right/bottom exclusive).
The marked image never enters the numeric extraction. Use --whole to emit the original embedded stream.
"""
from pathlib import Path
import argparse,csv,hashlib,io
import fitz
import numpy as np
from PIL import Image,ImageChops
def get_native(path):
    with fitz.open(path) as d:
        if len(d)!=1:raise ValueError(f'Expected one page: {path}')
        data=d[0].get_images(full=True)
        if len(data)!=1:raise ValueError(f'Expected one raster: {path}')
        x=data[0];obj=d.extract_image(x[0])
        if x[1] or obj['colorspace']!=3 or obj['ext']!='jpeg':raise ValueError('Unrecognised source raster; inspect image/soft mask before extracting.')
        raw=obj['image']
        if raw!=d.xref_stream_raw(x[0]):raise ValueError('PDF stream requires another decoding path.')
        im=Image.open(io.BytesIO(raw))
        if im.mode!='RGB':raise ValueError(im.mode)
        im.load()
        return im,raw,x
def region_set(root,primary,output,whole=False):
    data=root/'data';output.mkdir(exist_ok=True,parents=True)
    with (data/'optical_regions.csv').open() as f:regions=list(csv.DictReader(f))
    notes=[];summaries=[]
    for core in dict.fromkeys(r['core_id'] for r in regions):
        pair=[r for r in regions if r['core_id']==core]
        r0=pair[0];p=primary/r0['source_path'];im,stream,obj=get_native(p)
        if hashlib.sha256(p.read_bytes()).hexdigest()!=r0['source_sha256'] or hashlib.sha256(stream).hexdigest()!=r0['jpeg_sha256']:raise ValueError(f'Source changed: {core}')
        if whole:(output/(core+'.jpg')).write_bytes(stream)
        for r in pair:
            b=tuple(int(r[c]) for c in ('left_px','top_px','right_px_exclusive','bottom_px_exclusive'))
            if not (0<=b[0]<b[2]<=im.width and 0<=b[1]<b[3]<=im.height):raise ValueError((core,b))
            patch=im.crop(b)
            dest=output/(core+'_'+r['role']+'.png');patch.save(dest,optimize=True)
            with Image.open(dest) as candidate:
                if ImageChops.difference(candidate,im.crop(b)).getbbox():raise ValueError('Pixel round-trip')
            notes.append([core,r['role'],dest.name,patch.width,patch.height,hashlib.sha256(patch.tobytes()).hexdigest(),hashlib.sha256(dest.read_bytes()).hexdigest()])
            # Values are averages of decoded JPEG sample values; there is no white-balance or radiometric calibration.
            if r['role']=='sediment_interior':
                px=np.asarray(patch)
                for i,(red,green,blue) in enumerate(px.mean(axis=1)):
                    summaries.append([core,3,b[1]+i,f'{red:.3f}',f'{green:.3f}',f'{blue:.3f}',patch.width])
    with (output/'patches.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['core_id','role','file','width_px','height_px','decoded_rgb_sha256','png_sha256']);w.writerows(notes)
    with (output/'row_rgb.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['core_id','printed_section','jpeg_y_px','mean_R8','mean_G8','mean_B8','n_pixels']);w.writerows(summaries)
if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path);p.add_argument('output',type=Path);p.add_argument('--whole',action='store_true');q=p.parse_args();region_set(root,q.primary,q.output,q.whole)
