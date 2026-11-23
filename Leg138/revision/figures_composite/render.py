"""Generate the two supported physical-property tracks of Site 846 IR Figure 7."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import sys
from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageChops
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

HERE = Path(__file__).resolve().parent
LEG = HERE.parents[1]
COLLECT = LEG/"figures/core/composite_v2/tools"
sys.path.insert(0,str(COLLECT))
from collect_tracks import read_schema, site_tracks
from render_composites import gaussian20, compare_print

WITNESS = "ir/primary/VOLUME/CHAPTERS/ir138_11.pdf"
HASH = "9029db07c07283a3d30eb8ddb9ed4c075771f31cc48927876a5d6ee9f4cbc268"
REL = "revision/figures_composite"
QUANTITIES = ("grape","susceptibility")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,records):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,records[0].keys(),lineterminator="\n")
        w.writeheader()
        w.writerows(records)


def collect(source_root,out):
    primary=source_root/"disc/primary"
    core=LEG/"disc/core"
    manifest={r["path"]:r for r in csv.DictReader((core/"sources.csv").open())}
    expected=["SITE_846/SPLICE.846","SITE_846/GRAPE/GR846.MCD"]+[
        f"SITE_846/SUS/SUS846{hole}.FIN" for hole in "ABCD"]
    for key in expected:
        if sha(primary/key)!=manifest[key]["sha256"]:
            raise ValueError("Input mismatch: "+key)
    raw,sources,_summary=site_tracks(846,primary,read_schema(core),manifest)
    save(out/"source_tracks.csv", [s for s in sources if s["source_path"] in expected])
    records=[]
    all_traces={}
    for kind in QUANTITIES:
        blocks=[]
        for r in raw[kind]:
            if (not blocks or r[0]!=blocks[-1][-1][0] or
                r[2]<blocks[-1][-1][2] or r[2]-blocks[-1][-1][2]>.300001):
                blocks.append([])
            blocks[-1].append(r)
        traces=[]
        for bi,block in enumerate(blocks,1):
            values=np.array([r[2:] for r in block])
            if kind=="grape":
                displayed=gaussian20(values[:,1])
            else:
                displayed=.63*gaussian20(values[:,1])
            traces.append(np.column_stack((values[:,0],displayed)))
            for r,val in zip(block,displayed):
                (switch,source,hole,core_number,section),ln,depth,*readings=r
                records.append(dict(track=kind,segment=bi,source_path="disc/primary/"+source,
                    native_line=ln,splice_interval=switch+1,hole=hole,core=core_number,section=section,
                    depth_mcd=f"{depth:.3f}",native_value=f"{readings[0]:.4f}",
                    released_smoothed_density=f"{readings[1]:.4f}" if kind=="grape" else "",
                    display_value=f"{val:.8f}"))
        all_traces[kind]=traces
    with (out/"series.csv.gz").open("wb") as handle, gzip.GzipFile(fileobj=handle,mode="wb",filename="",mtime=0) as compressed, io.TextIOWrapper(compressed,encoding="utf-8",newline="") as text:
        w=csv.DictWriter(text,records[0].keys(),lineterminator="\n")
        w.writeheader()
        w.writerows(records)
    return all_traces,expected


def trapezoid(layout,idx,inset=.65):
    y0=layout["top_y_pt"]+inset
    y1=layout["base_y_pt"]-inset
    xt=layout["panel_edges_at_top_pt"]
    xb=layout["panel_edges_at_base_pt"]
    return [(xt[idx]+inset,y0),(xt[idx+1]-inset,y0),
            (xb[idx+1]-inset,y1),(xb[idx]+inset,y1)]


def print_background(page,spec,alter):
    # Extract the actual distributed JPEG. Outside the two masked interiors,
    # the raster is a lossless integer-pixel crop from this decoded witness.
    info, = page.get_image_info(xrefs=True)
    x0,y0,x1,y1=info["bbox"]
    dx=(x1-x0)/info["width"]
    dy=(y1-y0)/info["height"]
    source=Image.open(io.BytesIO(page.parent.extract_image(info["xref"])["image"]))
    bands=source.convert("RGB").split()
    if not ImageChops.difference(bands[0],bands[1]).getbbox() and not ImageChops.difference(bands[0],bands[2]).getbbox():
        source=bands[0]
    bounds=spec["figure_crop_xyxy_pt"]
    box=(int(np.floor((bounds[0]-x0)/dx)),int(np.floor((bounds[1]-y0)/dy)),
         int(np.ceil((bounds[2]-x0)/dx)),int(np.ceil((bounds[3]-y0)/dy)))
    im=source.crop(box)
    rect=fitz.Rect(x0+box[0]*dx,y0+box[1]*dy,x0+box[2]*dx,y0+box[3]*dy)
    if alter:
        draw=ImageDraw.Draw(im)
        for ix in range(2):
            draw.polygon([(round((x-rect.x0)/dx),round((y-rect.y0)/dy)) for x,y in trapezoid(spec,ix)],fill="white")
    return im,rect


def pdf_point(rect,x,y):
    return x-rect.x0,rect.y1-y


def draw_tracks(canvas,spec,rect,segs,idx):
    d0=spec["depth_top_mcd"]
    d1=spec["depth_base_mcd"]
    vt=spec["top_y_pt"]
    vb=spec["base_y_pt"]
    left0,right0=spec["panel_edges_at_top_pt"][idx:idx+2]
    left1,right1=spec["panel_edges_at_base_pt"][idx:idx+2]
    amin,amax=spec["header_rate_bounds"][idx]
    def xy(depth,value):
        f=(depth-d0)/(d1-d0)
        l=left0*(1-f)+left1*f
        r=right0*(1-f)+right1*f
        return pdf_point(rect,l+(r-l)*(value-amin)/(amax-amin),vt+(vb-vt)*f)
    canvas.saveState()
    clip=canvas.beginPath()
    coords=[pdf_point(rect,x,y) for x,y in trapezoid(spec,idx)]
    clip.moveTo(*coords[0])
    for xy0 in coords[1:]:
        clip.lineTo(*xy0)
    clip.close()
    canvas.clipPath(clip,stroke=0)
    canvas.setLineWidth(.70)
    canvas.setLineJoin(1)
    nrows=sum(int(np.count_nonzero((s[:,0]>=d0)&(s[:,0]<d1))) for s in segs)
    for seg in segs:
        array=seg[(seg[:,0]>=d0-.3)&(seg[:,0]<=d1+.3)]
        if len(array)<2:
            continue
        path=canvas.beginPath()
        path.moveTo(*xy(*array[0]))
        for pair in array[1:]:
            path.lineTo(*xy(*pair))
        canvas.drawPath(path)
    # Preserve the ruler styles inside the two cleared track interiors.
    canvas.setLineWidth(.35)
    for depth in range(d0+5,d1,5):
        x,y=xy(depth,amin)
        canvas.line(x,y,x+(4 if depth%10==0 else 2.3),y)
    canvas.restoreState()
    return nrows


def compare_page(page,spec,all_series):
    results=[]
    d0=spec["depth_top_mcd"]
    d1=spec["depth_base_mcd"]
    for ix,k in enumerate(QUANTITIES):
        s=all_series[k]
        edges=np.mean([spec["panel_edges_at_top_pt"],spec["panel_edges_at_base_pt"]],axis=0)
        rect=fitz.Rect(edges[ix],spec["top_y_pt"],edges[ix+1],spec["base_y_pt"])
        frame=(rect,(*spec["header_rate_bounds"][ix],d0,d1))
        options={"displayed":s}
        if k=="grape":
            options["GRAPECOR.F, corrected density"]=[np.column_stack((r[:,0],1.025+(r[:,1]-1.128)*1.06997)) for r in s]
        else:
            options["without SI conversion"]=[np.column_stack((r[:,0],r[:,1]/.63)) for r in s]
        for formula,tracks in options.items():
            result=compare_print(page,frame,tracks)
            results.append(dict(item_id="IR11.F07",source_page=spec["source_page"],panel=k,calculation=formula,**result))
    return results


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source_root",type=Path)
    p.add_argument("--out",type=Path,default=HERE)
    args=p.parse_args()
    out=args.out
    out.mkdir(parents=True,exist_ok=True)
    source=args.source_root/WITNESS
    if sha(source)!=HASH:
        raise ValueError("Site 846 IR witness hash differs")
    traces,paths=collect(args.source_root,out)
    specs=json.loads((HERE/"regions.json").read_text())
    qual=("GRAPE and susceptibility reconstructed independently across three printed continuations. "
        "Density retains systematic differences from print. The optical, stratigraphic, lithologic and legend layers retain IR print evidence. "
        "The original 20-point Gaussian coefficients and production input stages are unresolved.")
    output=out/"IR11.F07.pdf"
    c=Canvas(str(output),invariant=1,pageCompression=1)
    c.setTitle("Site 846 | IR Figure 7 | data-derived GRAPE and magnetic susceptibility")
    c.setAuthor("Leg 138 digital collation")
    c.setSubject(qual)
    outcomes=[]
    layers=[]
    source_doc=fitz.open(source)
    for spec in specs:
        pg=spec["source_page"]; page=source_doc[pg-1]
        im,rect=print_background(page,spec,True)
        c.setPageSize((rect.width,rect.height))
        c.drawImage(ImageReader(im),0,0,rect.width,rect.height)
        for ix,k in enumerate(QUANTITIES):
            count=draw_tracks(c,spec,rect,traces[k],ix)
            layers.append(dict(source_page=pg,layer=k,role="independent data + code curve",samples=count,
                stage=("column 2 of GR846.MCD, measured density with independent 20-point display Gaussian" if k=="grape" else "FIN values, independent published-control splice, 20-point display Gaussian and 0.63 conversion")))
        if note:=spec["magnetic_scale_note_rect"]:
            pm=page.get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(note),colorspace=fitz.csGRAY)
            x,y=pdf_point(rect,note[0],note[3])
            c.drawImage(ImageReader(Image.frombytes("L",(pm.width,pm.height),pm.samples)),x,y,note[2]-note[0],note[3]-note[1])
        for k,desc in [("color reflectance","three overlapping printed bands and their legend; no independently identified band-by-band scan readings"),
            ("magnetics","published polarity/indeterminacy interpretation"),("age","printed epoch and numeric boundary interpretation"),
            ("lithology","shipboard authorial graphic lithology"),("lithologic unit","printed divisions and unit labels"),
            ("frame, headers, captions","original visible typography, page-specific ticks and legend")]:
            layers.append(dict(source_page=pg,layer=k,role="retained IR print layer",samples="",stage=desc))
        outcomes.extend(compare_page(page,spec,traces))
        c.showPage()
    c.save()
    save(out/"scan_comparison.csv",outcomes)
    save(out/"layers.csv",layers)
    with fitz.open(output) as replacement,fitz.open() as atlas:
        for ix,(r,sp) in enumerate(zip(replacement,specs)):
            pg=sp["source_page"]
            src=source_doc[pg-1]
            orig,rect=print_background(src,sp,False)
            w,h=rect.width,rect.height
            plate=atlas.new_page(width=2*w+60,height=h+94)
            plate.insert_text((16,20),f'Site 846 / IR Figure 7 / printed page {sp["printed_page"]}',fontsize=12,fontname="hebo")
            plate.insert_text((16,38),"Published figure",fontsize=9)
            plate.insert_text((w+43,38),"Data redraw of GRAPE and susceptibility; remaining IR layers in print",fontsize=8)
            a=fitz.Rect(16,46,16+w,46+h)
            bb=fitz.Rect(43+w,46,43+2*w,46+h)
            buf=io.BytesIO(); orig.save(buf,format="PNG")
            plate.insert_image(a,stream=buf.getvalue())
            plate.show_pdf_page(bb,replacement,ix)
            plate.insert_link({"kind":fitz.LINK_URI,"from":fitz.Rect(12,24,110,42),"uri":f"https://www-odp.tamu.edu/publications/138_IR/VOLUME/CHAPTERS/ir138_11.pdf#page={pg}"})
            row={r["panel"]:r for r in outcomes if r["source_page"]==pg and r["calculation"]=="displayed"}
            msg=f"Median absolute deviation / printed axis span: GRAPE {row['grape']['median_abs_percent_span']}%, susceptibility {row['susceptibility']['median_abs_percent_span']}%. The original figure filter remains unresolved."
            plate.insert_text((16,h+68),msg,fontsize=8)
            plate.insert_text((16,h+83),"The three-band optical track, magnetics, age, lithology and lithologic units retain the original printed evidence.",fontsize=8)
        atlas.set_metadata(dict(title="Site 846 IR Figure 7: published and reconstructed physical tracks"))
        atlas.save(out/"IR11_F07_Comparison.pdf",garbage=4,deflate=True,no_new_id=True)
    source_doc.close()
    save(out/"manifest.csv",[dict(item_id="IR11.F07",source_page=12,source_pages="12|13|14",
        source_kind="released shipboard GRAPE MCD, susceptibility FIN files and published SPLICE controls; audited IR specimen",
        inputs="|".join("disc/primary/"+name for name in paths)+"|"+REL+"/regions.json",
        table_ids="",renderer=REL+"/render.py",output=REL+"/IR11.F07.pdf",redraw_extent="grape_and_susceptibility_tracks_only",
        qualification=qual,source_pdf_sha256=HASH,plot_sha256=sha(output),evidence_file=REL+"/scan_comparison.csv")])

if __name__=="__main__":
    main()
