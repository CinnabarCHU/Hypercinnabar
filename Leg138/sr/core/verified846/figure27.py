"""Regenerate chapter 27 figure 3 from the edited print table; add an aligned facsimile if supplied."""
import argparse
from pathlib import Path
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FixedLocator, FormatStrFormatter
from matplotlib import font_manager

ROOT=Path(__file__).resolve().parent
BBOX=(80,40,525,425)  # publisher PDF coordinates, points from the upper left
def redraw(target):
    for family in ["Liberation Sans","Liberation Serif"]:
        font_manager.findfont(family,fallback_to_default=False)
    plt.rcParams.update({"font.family":"Liberation Sans","font.size":7,"pdf.fonttype":42,
                         "axes.linewidth":0.77,"mathtext.fontset":"custom","mathtext.rm":"Liberation Sans",
                         "mathtext.cal":"Liberation Serif:italic","mathtext.it":"Liberation Sans:italic","mathtext.bf":"Liberation Sans:bold"})
    with (ROOT/"print/c27_t1.csv").open() as print_table:
        data=[tuple(float(r[key]) if r[key] else None for key in ("rmcd","toc_pct","caco3_pct","dbd","uk37")) for r in csv.DictReader(print_table)]
    left,top,right,bottom=BBOX;w=right-left;h=bottom-top
    fig=plt.figure(figsize=(w/72,h/72))
    def text(x,y,s,**kwargs):
        fig.text((x-left)/w,(bottom-y)/h,s,**kwargs)
    specs=[(109.8,208.2,(0,2.5),[0,1,2],.5,"%.1f","TOC (wt %)"),
           (213.7,309.8,(20,100),[30,50,70,90],10,"%d",r"CaCO$_3$ (wt %)"),
           (316.3,412.2,(.2,.8),[.3,.4,.5,.6,.7],.1,"%.1f",r"Dry-bulk density (g/cm$^3$)"),
           (419.0,515.0,(.7,1.0),[.7,.8,.9,1.0],.05,"%.1f",r"$\mathrm{U}_{37}^{\mathrm{K}\prime}$")]
    for i,(x1,x2,xlim,ticks,minor,fmt,label) in enumerate(specs):
        yt,yb=78.1,391.25
        ax=fig.add_axes([(x1-left)/w,(bottom-yb)/h,(x2-x1)/w,(yb-yt)/h])
        pts=[(row[i+1],row[0]) for row in data if row[i+1] is not None]
        ax.plot([x for x,y in pts],[y for x,y in pts],"-o",color="#191919",lw=.92,ms=2.45,
                markeredgewidth=.12,solid_joinstyle="round")
        ax.set(xlim=xlim,ylim=(50,0))
        ax.xaxis.set_major_locator(FixedLocator(ticks));ax.xaxis.set_minor_locator(MultipleLocator(minor))
        ax.xaxis.set_major_formatter(FormatStrFormatter(fmt))
        ax.yaxis.set_major_locator(MultipleLocator(5));ax.yaxis.set_minor_locator(MultipleLocator(2.5))
        ax.tick_params(axis="both",which="both",direction="in",top=True,bottom=True,left=True,right=True,
                       length=3.4,width=.6,labelsize=6.4)
        ax.tick_params(axis="x",labeltop=True,labelbottom=False,pad=4)
        ax.tick_params(axis="y",labelleft=i==0,pad=3,length=4)
        ax.tick_params(axis="y",which="minor",length=2.2)
        if i==0:ax.set_ylabel("Depth (m composite)",fontsize=7,labelpad=0)
        text(x1+1,56,"ABCD"[i],size=9.8,weight="bold",va="bottom")
        text((x1+x2)/2,59.6,label,size=7.4,ha="center",va="bottom")
    # Match the placement of the original two-line legend. Typography is reset.
    text(87.3,408.5,'Figure 3. A. Organic carbon concentration. B. Calcium carbonate concentration. C. Estimated dry-bulk density.',fontfamily="Liberation Serif",size=7.6)
    text(87.3,418.1,'D. Alkenone unsaturation index in the upper 46 m of revised composite depth at Site 846.',fontfamily="Liberation Serif",size=7.6)
    fig.savefig(target,metadata={"Title":"ODP Leg 138 · Site 846 · Chapter 27, Figure 3","Creator":"Site 846 SR critical edition","CreationDate":None});plt.close(fig)
def compare(redraw_file,source,destination):
    import fitz
    # Only the historical witness is raster. The generated figure stays vector in the comparison.
    with fitz.open(redraw_file) as edited,fitz.open(source) as src,fitz.open() as output:
        r=fitz.Rect(BBOX); box=fitz.Rect(0,0,r.width,r.height);footer=37
        for j in (0,1):
            pg=output.new_page(width=r.width,height=r.height+footer);pageno=5
            if j==0:pg.show_pdf_page(box,edited,0)
            else:pg.show_pdf_page(box,src,pageno,clip=r)
            pg.draw_line((7,r.height+4),(r.width-7,r.height+4),color=(.78,.78,.78),width=.4)
            head="Reconstruction from printed Table 1" if j==0 else "Publisher scan, printed page 610"
            pg.insert_text((8,r.height+17),head,fontsize=8,fontname="hebo",color=(.16,.16,.16))
            pg.insert_text((8,r.height+28),"Emeis et al. (1995)  |  ODP Leg 138, Scientific Results, chapter 27, figure 3",fontsize=6.8,fontname="helv",color=(.28,.28,.28))
        output.set_metadata({"title":"Site 846 | Emeis et al. (1995), Figure 3 | reconstruction and printed witness"});output.save(destination,garbage=4,deflate=True)
if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--source-pdf",type=Path);args=ap.parse_args()
    out=ROOT/"proofs";out.mkdir(exist_ok=True);pdf=out/"Chapter27_Figure3.pdf";redraw(pdf)
    if args.source_pdf:compare(pdf,args.source_pdf,out/"Chapter27_Figure3_Comparison.pdf")
