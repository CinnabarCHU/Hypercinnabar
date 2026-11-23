"""Verify source hashes, rendered vector plates and original-ink alignment."""
import argparse
import csv
import io
import json
from pathlib import Path

import fitz
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

import farrell_special
from kernel_calibration import calibrate
import redraw

ISO_GEOMETRY = {
    1:(152,565,60,164,119.7), 2:(186,599,60,164,119.7),
    5:(175,608,59,168,125.1), 6:(153,586,67,175,125.5)
}
CROPS = {
    15: {1:(100,44,470,567), 2:(122,43,486,565), 5:(115,42,493,696), 6:(94,47,475,677)},
    35: {2:(105,43,506,299), 5:(47,45,561,417), 6:(20,45,540,435),
         7:(45,44,553,423), 8:(19,44,538,391),9:(46,44,563,445),
         10:(21,44,540,445),11:(19,214,537,608),12:(43,42,558,422),
         13:(22,48,541,458),14:(45,40,551,425),15:(52,40,511,603),
         26:(53,50,496,378),27:(53,45,571,452)}
}


def summarize(distance, x, y):
    if not len(x):
        return {"probes":0}
    px=np.rint(x).astype(int)
    py=np.rint(y).astype(int)
    a=distance[py,px]
    b=distance[py+6,px]
    return {"probes":int(len(a)), "within_2px_fraction":round(float(np.mean(a<=2)),5),
            "median_px":round(float(np.median(a)),3), "p90_px":round(float(np.quantile(a,.9)),3),
            "shift_down_6px_fraction":round(float(np.mean(b<=2)),5)}


def polyline(x,y,left,right,top,bottom,xmin,xmax,ymin,ymax,dist,exclude_edges=True):
    start=max(xmin+0.04,x[0]); stop=min(xmax-.04,x[-1])
    grid=np.arange(start,stop,(xmax-xmin)/(right-left)/2)
    values=np.interp(grid,x,y)
    px=left+(right-left)*(grid-xmin)/(xmax-xmin)
    py=bottom-(bottom-top)*(values-ymin)/(ymax-ymin)
    use=(py>top+2)&(py<bottom-2) if exclude_edges else np.ones(len(grid),dtype=bool)
    return summarize(dist,px[use],py[use])


def distance(page, scale, threshold):
    pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),colorspace=fitz.csGRAY,alpha=False)
    raster=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width)
    return distance_transform_edt(raster>threshold)


def isotope_score(f,data,dist,raw=False):
    x,y=redraw.points15(data,f,raw=raw)
    left,right,top,bot,spacing=ISO_GEOMETRY[f]
    dep=f<=2
    panel=np.floor((x-60)/40).astype(int) if dep else np.floor(x-1).astype(int)
    start=60+40*panel if dep else 1+panel
    yr=(y-2)/3 if f in (1,5) else ((1-y)/3 if f==2 else (2-y)/4)
    px=left+(right-left)*(x-start)/(40 if dep else 1)
    py=top+panel*spacing+yr*(bot-top)
    return summarize(dist,px,py)


def stack_score(f,data,dist):
    g=redraw.GEO[str(f)]; output={}
    for i,site in enumerate(range(844,855)):
        x,y=redraw.panel_data(data,g,site)
        xs=[];ys=[]
        for a,b in redraw.visible_segments(x,y,site,13):
            q=np.arange(max(a[0],.08),min(a[-1],12.99),.0125)
            xs.extend(g["x0"]+(g["x13"]-g["x0"])*q/13)
            ys.extend(g["baseline_by_site"][i]-g["y_pixels_per_unit"][i]*np.interp(q,a,b))
        output[str(site)]=summarize(dist,xs,ys)
    return output


def special_score(f,data,dist):
    out={}
    if f==2:
        ds="SR.C35.APPENDIXB"
        x,y,n=redraw.pairs(data,ds,"age_ma","opal_pct",847)
        labels=np.array([data[ds][int(i)-1][1]["opal_source"] for i in n])
        for lab in ["Murray","Janecek","Levitan"]:
            mask=(labels==lab)&(x<=3)
            a,b=x[mask],y[mask]
            out[lab]=summarize(dist,136+(498-136)*a/3,252-(252-52)*b/50)
            out[lab]["number_of_rows"]=len(a)
    elif f==26:
        for site in (846,850):
            x,y,_=redraw.pairs(data,"SR.C35.APPENDIXB","age_ma","opal_mar",site)
            a,b=farrell_special.five_point(x,y)
            result=polyline(a,b,85,489,55,298,0,12,0,2,dist)
            result["bin_means"]=[round(float(np.mean(y[(x>=i)&(x<i+1)])),5) for i in range(12)]
            out[str(site)]=result
    else:
        lefts=[94,94,94,345,345,345]
        for i,(field,app,ylabel,ylim,step) in enumerate(farrell_special.PANELS):
            left=lefts[i];top=[54,167,282][i%3];bottom=[160,273,388][i%3]
            for site in (846,850):
                for k in [1,5]:
                    x,y,_=redraw.pairs(data,"SR.C35.APPENDIX"+app,"age_ma",field,site)
                    a,b=(x,y) if k==1 else farrell_special.five_point(x,y)
                    out[f"{field}.{site}.window{k}"]=polyline(a,b,left,left+212,top,bottom,0,12,*ylim,dist)
    return out


def review_page(book,original,doc,chapter,f,manifest):
    page=book.new_page(width=864,height=560)
    page.insert_text((25,24),manifest["item_id"]+"   |   PRINT / DATA REDRAW",fontsize=12,fontname="hebo")
    page.insert_text((25,43),f"Printed witness, PDF page {manifest['source_page']}",fontsize=9)
    page.insert_text((445,43),"Vector reconstruction",fontsize=9)
    rect=fitz.Rect(CROPS[chapter][f])
    # Retain only the printed chart/caption region in this compact visual QA book.
    pix=original.get_pixmap(matrix=fitz.Matrix(1.65,1.65),clip=rect,colorspace=fitz.csGRAY)
    img=Image.frombytes('L',(pix.width,pix.height),pix.samples)
    buf=io.BytesIO();img.save(buf,format="JPEG",quality=83,optimize=True)
    panel=fitz.Rect(20,55,426,533);page.insert_image(panel,stream=buf.getvalue(),keep_proportion=True)
    page.show_pdf_page(fitz.Rect(438,55,844,533),doc,0)
    page.insert_link({"kind":fitz.LINK_URI,"from":fitz.Rect(22,31,235,48),"uri":manifest["source_url"]})
    page.insert_text((25,549),"Farrell et al. / Shackleton et al., ODP Scientific Results 138 (1995). See manifest and validation for scope.",fontsize=7.5)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source_root",type=Path,help="Parent of sr/primary/official")
    ap.add_argument("--comparison",action="store_true")
    args=ap.parse_args()
    data=redraw.load()
    report={"method":"Distances from positions predicted by table values to any printed ink. Page scale 1.25 display px per PDF point (threshold 160); C35 special figures use 1.00 (threshold 180); C15 points use threshold 170. Fractions include matches to nearby text, other traces and axes. A six-pixel vertical shift is a local control, not a confidence interval.",
            "figures":{}}
    manifests=list(csv.DictReader((redraw.HERE/"manifest.csv").open()))
    book=fitz.open()
    for r in manifests:
        ch=int(r["item_id"][4:6]);f=int(r["item_id"].split("FIGURE")[1])
        for name,h in zip(r["inputs"].split("|"),r["input_sha256"].split("|"),strict=True):
            assert redraw.sha(args.source_root/name)==h,name
        if r["calibration_source"]:
            assert redraw.sha(args.source_root/r["calibration_source"])==r["calibration_sha256"]
        original=args.source_root/r["source_path"]
        assert redraw.sha(original)==r["source_sha256"],r["item_id"]
        op=fitz.open(original)
        page=op[int(r["source_page"])-1]
        vector=redraw.LEG/r["output"]
        assert redraw.sha(vector)==r["output_sha256"]
        with fitz.open(vector) as doc:
            assert len(doc)==1 and not doc[0].get_images(),r["item_id"]
            assert doc[0].get_drawings(),r["item_id"]
            if args.comparison:review_page(book,page,doc,ch,f,r)
        if ch==15:
            d=distance(page,1.25,170)
            result={"point_field":isotope_score(f,data,d)}
            if f<=2:result["alternative_raw_field"]=isotope_score(f,data,d,True)
        elif f in farrell_special.SOURCE:
            result=special_score(f,data,distance(page,1,180))
        elif f==15:
            result={};g=redraw.GEO["15"];d=distance(page,1.25,160)
            for site,top,bottom in zip(g["sites"],g["top"],g["bottom"]):
                for key,scale in [("caco3_pct",100),("caco3_mar",5)]:
                    x,y,_=redraw.pairs(data,g["dataset"],"age_ma",key,site)
                    for k in (1,5):
                        a,b=(x,y) if k==1 else farrell_special.five_point(x,y)
                        result[f"{site}.{key}.window{k}"]=polyline(a,b,g["x0"],g["x16"],top,bottom,0,16,0,scale,d)
        else:
            result=stack_score(f,data,distance(page,1.25,160))
        report["figures"][r["item_id"]]=result
        op.close()
    if args.comparison:
        book.set_metadata({"title":"Leg 138 SR: printed and reconstructed figures"})
        book.set_toc([[1,r["item_id"],i+1] for i,r in enumerate(manifests)])
        book.save(redraw.HERE/"comparison.pdf",garbage=4,deflate=True,no_new_id=True)
    book.close()
    (redraw.HERE/"validation.json").write_text(json.dumps(report,indent=2)+"\n")
    kernel=calibrate(data)
    (redraw.HERE/"kernel_calibration.json").write_text(json.dumps(kernel,indent=2)+"\n")
    for series in kernel["series"].values():
        tests=series["sigma_to_full_width"]
        assert tests["1/6"]["fraction_within_0.006"] > 0.85
        assert tests["1/6"]["fraction_within_0.006"] > tests["1/4"]["fraction_within_0.006"]
    for k in ("SR.C15.FIGURE1","SR.C15.FIGURE2","SR.C15.FIGURE5","SR.C15.FIGURE6"):
        assert report["figures"][k]["point_field"]["within_2px_fraction"]>.95
    assert len(manifests)==18
    print(f"{len(manifests)} vector PDFs and their numeric witnesses verified.")


if __name__=="__main__":main()
