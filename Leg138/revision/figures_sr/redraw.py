"""Rebuild the Leg 138 SR figure plates from the distributed numerical tables."""
import argparse
import csv
import gzip
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter, MultipleLocator
import farrell_special

HERE = Path(__file__).resolve().parent
LEG = HERE.parents[1]
FIGDIR = HERE / "pdf"
GEO = json.loads((HERE / "farrell_layout.json").read_text())
SOURCE = {r["source"]: r for r in csv.DictReader((LEG / "sr/core/source_manifest.csv").open())}
DATA = {r["dataset_id"]: r for r in csv.DictReader((LEG / "sr/core/datasets.csv").open())}
INPUT = {
    "sr/core/records.jsonl.gz": "dc7905a000bb800c0f1cff8ac8d22be3724e08503acaf1a60058bb685c5b531c",
    "sr/core/edition2/data/row_apparatus.jsonl": "cd746a36a306db5ebd66e6fa1fe312aaf633a1017c84cb0fe032cd8d3b3b1195",
}
plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42, "axes.linewidth": .55,
                     "path.simplify": False, "lines.solid_joinstyle": "round"})
META = {"CreationDate": datetime(2000, 1, 1, tzinfo=timezone.utc), "Creator": "Leg 138 SR figure reconstruction"}

ISO_CAPTIONS = {
    1: "Oxygen isotope record for benthic foraminifers from Site 846 vs. depth rmcd. All data are shown; the line, a Gaussian interpolation at 10 cm with a 59.99 cm window, is solely to guide the eye.",
    2: "Carbon isotope record for benthic foraminifers from Site 846 vs. depth rmcd. All data are shown; the line (as Fig. 1) is to guide the eye.",
    5: "Oxygen isotope record from Site 846 vs. age. The line shows an interpolation at 3-k.y. intervals smoothed using a Gaussian filter having a total width of 8.99 k.y. The data points show the average where replicate analyses were made in the same sample. Gaps in the line show where no measurement falls within the interpolation window; note that the time series analysis was performed using a narrower smoothing window than that used for this figure.",
    6: "Carbon isotope record from Site 846 vs. age, generated as Figure 5.",
}
ISO_PAGES = {1: 5, 2: 6, 5: 10, 6: 11}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load():
    for path, expected in INPUT.items():
        if sha(LEG / path) != expected:
            raise ValueError("Review changed numerical input: " + path)
    columns = {key: json.loads(d["fields_json"]) for key, d in DATA.items()}
    fixes = {(r["dataset_id"], r["ordinal"]): r["proposed_field_values"]
             for line in (LEG / "sr/core/edition2/data/row_apparatus.jsonl").read_text().splitlines()
             if (r := json.loads(line))["dataset_id"] == "SR.C35.APPENDIXB"}
    data = defaultdict(list)
    selected = {"SR.C15.TABLE3", "SR.C15.TABLE5", "SR.C15.TABLE7"} | {g["dataset"] for g in GEO.values()}
    with gzip.open(LEG / "sr/core/records.jsonl.gz", "rt") as handle:
        for line in handle:
            row = json.loads(line)
            key = row["d"]
            if key not in selected:
                continue
            fields = dict(zip(columns[key], row["v"], strict=True)) if row["v"] is not None else fixes[key, row["n"]]
            data[key].append((row["n"], fields))
    for key, records in data.items():
        assert len(records) == int(DATA[key]["records"])
    return data


def pairs(data, dataset, xfield, yfield, site=None):
    # Keep author ordering and replicate coordinates. A numeric token suffixed s
    # is the author's suspect-value flag in Appendix B, retained in the table.
    points = []
    for ordinal, row in data[dataset]:
        if site is not None and int(row["hole"][:3]) != site:
            continue
        values = [row[xfield], row[yfield]]
        if any(s.strip().upper() in ("", "NA", "N.A.", "N/A", "-9999.00") for s in values):
            continue
        # The CD doubles the minus sign for one analysis. The printed Table 3,
        # PDF page 4, resolves it; keep the distributed lexeme in records.jsonl.
        if (dataset, ordinal, yfield, values[1]) == ("SR.C15.TABLE3", 39, "d13c_adjusted", "--0.19"):
            values[1] = "-0.19"
        x, y = (float(s.rstrip("s")) for s in values)
        if x == -9999 or y == -9999:
            continue
        points.append((x, y, ordinal))
    return np.array(points).T


def visible_segments(x, y, site, end):
    # The authors leave the Site 854 hiatus open. Drop only that single connecting
    # segment. All other differences in temporal sample spacing remain visible.
    cuts = np.flatnonzero((x[:-1] < 4.5) & (x[1:] > 4.5)) + 1 if site == 854 else []
    for xx, yy in zip(np.split(x, cuts), np.split(y, cuts)):
        if not len(xx) or xx[0] > end:
            continue
        if np.any(np.diff(xx) < 0):
            raise ValueError("Distributed age ordering changed")
        stop = np.searchsorted(xx, end, side="right")
        xv, yv = xx[:stop], yy[:stop]
        if stop < len(xx) and xv[-1] < end:
            xv = np.append(xv, end)
            yv = np.append(yv, np.interp(end, xx[stop-1:stop+1], yy[stop-1:stop+1]))
        yield xv, yv


def gaussian_guide(x, y, grid, width):
    # Figure support is specified; the separately published 5.99 kyr analytical
    # series favors a width of six sigma (see kernel_calibration.py).
    out = np.full(len(grid), np.nan)
    sigma = width / 6
    for i, center in enumerate(grid):
        select = abs(x - center) <= width / 2
        if np.any(select):
            w = np.exp(-.5 * np.square((x[select] - center) / sigma))
            out[i] = np.average(y[select], weights=w)
    return out


def points15(data, f, raw=False):
    depth = f <= 2
    dataset = "SR.C15.TABLE3" if depth else "SR.C15.TABLE5"
    isotope = "d18o" if f in (1, 5) else "d13c"
    col = isotope + ("_raw" if raw else "_adjusted") if depth else isotope
    x, y, _ = pairs(data, dataset, "depth_rmcd" if depth else "age_ma", col)
    mask = (x >= (60 if depth else 1)) & (x < (260 if depth else 7))
    return x[mask], y[mask]


def caption(fig, text, y=.018, width=105, x=.055, size=8.3):
    for i, line in enumerate(reversed(textwrap.wrap(text, width))):
        fig.text(x, y + i * (size+1.8)/72/fig.get_figheight(), line,
                 fontfamily="DejaVu Serif", fontsize=size, va="bottom")


def save(fig, item, fdir=FIGDIR):
    fdir.mkdir(parents=True, exist_ok=True)
    fig.savefig(fdir / (item+".pdf"), metadata={**META, "Title": item})
    plt.close(fig)


def isotope_figure(data, f):
    depth, oxygen = f <= 2, f in (1, 5)
    n = 5 if depth else 6
    x, y = points15(data, f)
    starts = list(range(60, 260, 40)) if depth else list(range(1, 7))
    fig, axes = plt.subplots(nrows=n, figsize=(5.9, 7.8 if depth else 9.4))
    fig.subplots_adjust(left=.14, right=.965, top=.985, bottom=.112, hspace=.20)
    step, width = (.10, .5999) if depth else (.003, .00899)
    origin = 60 if depth else 1.763
    grid = np.round(np.arange(origin, starts[-1]+(40 if depth else 1)+step/2, step), 8)
    guide = gaussian_guide(x, y, grid, width)
    for ax, a in zip(axes, starts):
        end = a+(40 if depth else 1)
        ax.set(xlim=(a,end), ylim=(5,2) if oxygen else (-2, 1 if depth else 2))
        between=(x>=a)&(x<end)
        ax.plot(x[between], y[between], ".", ms=1.55, color="black")
        seg=(grid>=a-step)&(grid<=end+step)
        ax.plot(grid[seg], guide[seg], color="black",lw=.44)
        ax.xaxis.set_major_locator(MultipleLocator(5 if depth else .2))
        ax.xaxis.set_major_formatter(FormatStrFormatter("%d" if depth else "%.1f"))
        ax.yaxis.set_major_locator(MultipleLocator(.5))
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
        ax.spines[["top","right"]].set_visible(False)
        ax.tick_params(axis="both",direction="in",length=2,width=.45,labelsize=6,pad=1.5)
        ax.set_ylabel("$\\delta^{%s}$ to PDB ‰" % ("18" if oxygen else "13"), fontsize=7,labelpad=1)
    axes[-1].set_xlabel("depth m (rmcd)" if depth else "Age (Ma)",fontsize=8,labelpad=2)
    caption(fig, f"Figure {f}. "+ISO_CAPTIONS[f], width=83, size=7.4, x=.06)
    save(fig, "SR.C15.FIGURE"+str(f))


def stroke(ax, x, y, w=.65, **kw):
    ax.plot(x,y,lw=w,color="black",**kw)


def label(ax, x, y, s, size=6.6, align="center", **kw):
    ax.text(x,y,s,ha=align,va="center",fontsize=size,color="black",**kw)


def panel_data(data, geometry, site):
    return pairs(data, geometry["dataset"], "age_ma", geometry["field"], site)[:2]


def stacked(data, f):
    g = GEO[str(f)]
    x0, right, y_top = g["x0"], g["x13"], g["interval_header"]
    baseline, scale = g["baseline_by_site"],g["y_pixels_per_unit"]
    low, high, ymin, ymax = x0-76, right+67, y_top-20, baseline[0]+81
    # Match width to the 1.25x physical-page witness render. Cropping removes
    # the neighboring article text, without changing chart aspect.
    fig=plt.figure(figsize=((high-low)/90,(ymax-ymin)/90))
    ax=fig.add_axes([0,0,1,1]); ax.set(xlim=(low,high),ylim=(ymax,ymin));ax.set_axis_off()
    X=lambda age:x0+(right-x0)*age/13
    boundaries = [2,4.5,6.7,11.2] if f<=8 else [4.5,6.7,9.5,11.2]
    for cut in boundaries:
        stroke(ax,[X(cut)]*2,[y_top-4,baseline[0]],.40,ls=(0,(1.1,1.3)))
    for i,(l,r) in enumerate(zip([0]+boundaries,boundaries+[13])):
        label(ax,X((l+r)/2),y_top,"Interval "+str(5-i),6.5)
    for j,site in enumerate(range(844,855)):
        x,y=panel_data(data,g,site)
        segs=list(visible_segments(x,y,site,13))
        for xx,yy in segs:
            stroke(ax,X(xx),baseline[j]-yy*scale[j],.62)
            if f<=8:
                use=(x<=13)&(x>=xx[0])&(x<=xx[-1])
                ax.plot(X(x[use]),baseline[j]-y[use]*scale[j],".",color="black",ms=1.35)
        label_x,label_y=g["site_label_centers"][j]
        label(ax,label_x,label_y,str(site),7)
    # The independently offset vertical axes carry a numeric scale at each site.
    # Put overlapping rulers in three narrow lanes left of the graph.
    levels=2 if f<=8 else 50 if f in (9,11) else 25 if f==10 else 4 if f==12 else 1
    lane_tops=[1e6]*3
    for j,(b,s) in enumerate(zip(baseline,scale)):
        lower, upper = 0, levels
        if f<=8:
            xx,yy=panel_data(data,g,844+j)
            visible=yy[xx<=13]
            if f in (5,6):
                lower=2 if visible.min()>=2 else 0
                upper=4
            else:
                upper=4 if visible.max()>2 else 2
        bottom_y=b-lower*s
        top_y=b-upper*s
        lane=next((i for i,t in enumerate(lane_tops) if bottom_y<t-3), min(range(3),key=lambda i:-lane_tops[i]))
        lane_tops[lane]=top_y
        xpos=x0-lane*13
        stroke(ax,[xpos,xpos],[bottom_y,top_y],.45)
        ticks=[(bottom_y,lower),(top_y,upper)]
        if upper-lower>levels: ticks.insert(1,(b-(lower+levels)*s,lower+levels))
        for yp,number in ticks:
            stroke(ax,[xpos-2.5,xpos],[yp,yp],.45)
            if j==0 or number!=0:
                label(ax,xpos-3.5,yp,str(number),5.2,align="right")
    stroke(ax,[x0,right],[baseline[0]]*2,.55)
    for t in range(14):
        stroke(ax,[X(t)]*2,[baseline[0],baseline[0]+3],.45)
        label(ax,X(t),baseline[0]+10,str(t),6.7)
    label(ax,(x0+right)/2,baseline[0]+23,"Age (Ma)",7.5)
    label(ax,low+9,(y_top+baseline[0])/2,g["label"],7.1,rotation=90)
    regions=["Equatorial\nTransect\n(~110°W)", "Galápagos\nRegion", "Guatemala\nBasin"]
    # Equatorial transect comprises Sites 848–854. Bracket ends follow the
    # interval occupied by the group, not a site-depth transformation.
    div1=(baseline[4]+baseline[3])/2-15
    div2=(baseline[2]+baseline[1])/2-15
    for (top,bottom),text in zip([(y_top+5,div1),(div1+5,div2),(div2+5,baseline[0]-2)],regions):
        ax.annotate("",xy=(right+7,bottom),xytext=(right+7,top),arrowprops={"arrowstyle":"<|-|>","mutation_scale":6,"lw":.55,"color":"black"})
        label(ax,right+12,(top+bottom)/2,text,6.4,align="left",linespacing=1.05)
    # Site 854 hiatus arrow is bounded by the specific available records.
    xs,ys=panel_data(data,g,854); gap=np.flatnonzero((xs[:-1]<4.5)&(xs[1:]>4.5))[0]
    xa,xb=X(xs[gap]),X(xs[gap+1])
    yp=baseline[-1]-scale[-1]*(ys[gap]+ys[gap+1])/2-1
    ax.annotate("",xy=(xb-2,yp),xytext=(xa+2,yp),arrowprops={"arrowstyle":"<|-|>","mutation_scale":6,"lw":.45,"color":"black"})
    label(ax,(xa+xb)/2,yp-2,"hiatus",5.5,bbox={"fc":"white","ec":"none","pad":0.2})
    if f==9:
        label(ax,X(9.5),baseline[6]+99,"carbonate\ncrash",5.4,
              bbox={"fc":"white","ec":"none","pad":.3})
    elif f==10:
        label(ax,X(11.9),y_top+33,"diatom mat\nat Site 850\nis 82% opal",5.5)
        ax.annotate("",xy=(X(10.501),baseline[6]-82.17*scale[6]),xytext=(X(11.5),y_top+42),
                    arrowprops={"arrowstyle":"-|>","mutation_scale":6,"lw":.4,"color":"black"})
    caption(fig,"Figure %d. "%f+g["caption"],y=.018,width=104,size=7.3,x=.045)
    save(fig,"SR.C35.FIGURE"+str(f))


def farrell15(data):
    g=GEO["15"]
    fig,axes=plt.subplots(4,1,figsize=(6.35,7.6),sharex=True)
    fig.subplots_adjust(left=.12,right=.875,top=.985,bottom=.116,hspace=.09)
    areas={844:"Guatemala Basin",845:"Guatemala Basin",846:"Galápagos region",849:"110°W equatorial site"}
    for ax,site in zip(axes,g["sites"]):
        alt=ax.twinx()
        for field,axis,dash in [("caco3_pct", ax, "-"),("caco3_mar",alt,(0,(1,1.6)))]:
            x,y,_=pairs(data,g["dataset"],"age_ma",field,site)
            yy=np.convolve(y,np.ones(5)/5,mode="valid")
            axis.plot(x[2:-2],yy,color="black",ls=dash,lw=.67,
                      label="%CaCO₃" if field=="caco3_pct" else "CaCO₃ mass accumulation rate")
        ax.set(xlim=(0,16),ylim=(0,100),ylabel="%CaCO₃");alt.set(ylim=(0,5),ylabel="CaCO₃ MAR (g/cm² k.y.)")
        ax.yaxis.set_major_locator(MultipleLocator(20));alt.yaxis.set_major_locator(MultipleLocator(1))
        ax.xaxis.set_major_locator(MultipleLocator(2));ax.xaxis.set_minor_locator(MultipleLocator(.5))
        for a in [ax,alt]:
            a.tick_params(labelsize=6.7,length=3,width=.45,direction="out")
            a.yaxis.label.set_size(7.3)
        ax.tick_params(axis="x",which="both",length=2,top=True,bottom=True)
        ax.text(.97,.12,f"Site {site}\n"+areas[site],ha="right", va="center",fontsize=6.9,
                transform=ax.transAxes)
        if site==845:
            handles=ax.get_lines()+alt.get_lines()
            ax.legend(handles,[p.get_label() for p in handles],loc="upper left",
                      fontsize=6.1,edgecolor="black",framealpha=1)
    axes[-1].set_xlabel("Age (Ma)",fontsize=8)
    caption(fig,"Figure 15. "+g["caption"],width=82,size=7.5)
    save(fig,"SR.C35.FIGURE15")


def manifest():
    records = []
    for ch, figures in [(15,ISO_PAGES),(35,[2,*range(5,16),26,27])]:
        for f in figures:
            if ch==15:
                ds="SR.C15.TABLE3" if f<=2 else "SR.C15.TABLE5"
                isotope="d18o" if f in (1,5) else "d13c"
                columns=("depth_rmcd|"+isotope+"_adjusted") if f<=2 else "age_ma|"+isotope
                q="Points are published values. The printed full Gaussian window and output spacing are applied. One-sixth-width sigma is supported by the Table 7 calibration. Its transfer to this guide and grid phase remain reconstruction choices. See kernel_calibration.json."
                extent="quantitative_panels_with_independent_filter"
                p=ISO_PAGES[f]
            elif f in farrell_special.SOURCE:
                p,dsets,columns=farrell_special.SOURCE[f]
                ds=dsets[0]
                q={2:"Laboratory labels retained; source rows with reported suspect-value flag kept.",
                   26:"Five-point centered moving mean for curves. Inset bars are arithmetic means of published unsmoothed sample values in left-closed 1-Myr bins.",
                   27:"Twelve curves replotted. The five-point mean and Appendix A/B choice per variable were inferred from comparison with the printed curves and are independently specified here."}[f]
                extent="complete_quantitative_panels"
            else:
                geo=GEO[str(f)]; ds=geo["dataset"];p=geo["pdf_page"]
                columns="hole|age_ma|"+"|".join(geo.get("fields",[geo.get("field")]))
                q="All displayed site series generated from reported values. Finite sample intervals joined in source order. Site 854 hiatus left open. Digital layout approximates the printed labels and independent site scales."
                if f==9:q+=" Site 854 differs from the common horizontal scale by approximately 3 display pixels in the print. The common age axis is preserved here."
                if f==15:q="Both curves per site from Appendix A; caption specifies five-point moving mean. Equal weights and centering on row three are explicit reconstruction choices."
                extent="complete_quantitative_panels"
            d=DATA[ds]; item=f"SR.C{ch:02}.FIGURE{f}"
            src="official/VOLUME/CHAPTERS/sr138_%02d.pdf"%ch
            input_path="sr/primary/"+d["source"]
            output="revision/figures_sr/pdf/"+item+".pdf"
            dsets=farrell_special.SOURCE[f][1] if ch==35 and f in farrell_special.SOURCE else [ds]
            input_path="|".join("sr/primary/"+DATA[k]["source"] for k in dsets)
            records.append(dict(item_id=item,source_page=p,source_kind="author-distributed SR electronic table",
                inputs=input_path,table_ids="|".join(dsets),renderer="revision/figures_sr/redraw.py",output=output,
                redraw_extent=extent,qualification=q,columns=columns,input_sha256="|".join(DATA[k]["sha256"] for k in dsets),
                source_path="sr/primary/"+src,source_sha256=SOURCE[src]["sha256"],
                calibration_table="SR.C15.TABLE7" if ch==15 else "",
                calibration_source="sr/primary/"+DATA["SR.C15.TABLE7"]["source"] if ch==15 else "",
                calibration_sha256=DATA["SR.C15.TABLE7"]["sha256"] if ch==15 else "",
                source_url=SOURCE[src]["url"]+f"#page={p}",output_sha256=sha(LEG/output)))
    with (HERE/"manifest.csv").open("w",newline="") as fp:
        writer=csv.DictWriter(fp,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args()
    data=load()
    for f in ISO_PAGES:isotope_figure(data,f)
    for f in range(5,15):stacked(data,f)
    farrell15(data)
    farrell_special.draw(data,pairs,caption,save)
    manifest()


if __name__=="__main__": main()
