"""Compare table-derived vertical plateaus with native scan ink in a calibrated frame."""
import argparse
import json
from pathlib import Path

import fitz
import numpy as np

from render import HERE, LEG, digest, extract_tables, rows, save_csv, series

SCALE = 3
# Tolerance expressed as a fraction of the printed x-axis range.
TOLERANCE = .0125


def analyze(spec, segs, page):
    l,t,r,b=spec["frame_pdf_xyxy_pt"]
    clip=fitz.Rect(l,t,r,b)
    pix=page.get_pixmap(matrix=fitz.Matrix(SCALE,SCALE),clip=clip,colorspace=fitz.csGRAY,alpha=False)
    darkness=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width)<150
    h,w=darkness.shape
    darkness[:, :max(3,round(.006*w))]=False
    darkness[:, -max(3,round(.006*w)):]=False
    # Horizontal tick marks must not count as matches to a plateau.
    for i in range(int(spec["y_max"]*2/spec["y_major"])+1):
        pos=round(i*spec["y_major"]/2/spec["y_max"]*(h-1))
        darkness[max(0,pos-3):min(h,pos+4), :round(.032*w)]=False
        darkness[max(0,pos-3):min(h,pos+4), -round(.032*w):]=False
    details=[]
    probes=[]
    for v,a,z,i in segs:
        if not v or v>=spec["x_max"]:
            continue
        top=round(a/spec["y_max"]*(h-1))
        base=round(min(z,spec["y_max"])/spec["y_max"]*(h-1))
        # Leave 2 native points at horizontal joins to avoid mistaking a
        # connector for evidence of the correct plateau value.
        inside=range(max(top+2*SCALE,2*SCALE),min(base-2*SCALE+1,h-2*SCALE))
        errs=[]
        for j in inside:
            ink=np.flatnonzero(darkness[max(0,j-1):j+2].any(axis=0))
            if len(ink):
                err=float(np.min(abs(ink/(w-1)-v/spec["x_max"])))
            else:
                err=1.0
            errs.append(err)
        if not errs:
            continue
        probes.extend(errs)
        details.append(dict(item_id=spec["item_id"],interval=i,published_rate=v,
            coordinate_top=a,coordinate_base=z,probes=len(errs),
            median_abs_deviation_fraction_x=f"{np.median(errs):.5f}",
            p90_abs_deviation_fraction_x=f"{np.percentile(errs,90):.5f}",
            agreement_fraction=f"{np.mean(np.asarray(errs)<=TOLERANCE):.4f}"))
    return dict(item_id=spec["item_id"],source_page=spec["source_page"],probes=len(probes),
        intervals_probed=len(details),plotted_intervals=sum(v is not None for v,*_ in segs),
        abs_x_tolerance_fraction=TOLERANCE,agreement_fraction=f"{np.mean(np.asarray(probes)<=TOLERANCE):.4f}",
        median_abs_deviation_fraction_x=f"{np.median(probes):.5f}",
        p95_abs_deviation_fraction_x=f"{np.percentile(probes,95):.5f}"),details


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source_root",type=Path,help="Directory containing ir/primary/VOLUME/CHAPTERS")
    p.add_argument("--out",type=Path,default=HERE)
    args=p.parse_args()
    specs=json.loads((HERE/"layout.json").read_text())
    tables,_=extract_tables(specs)
    inventory={r["local_path"]:r for r in rows(LEG/"data/source_inventory.csv.gz") if r["series"]=="IR"}
    details=[]
    stats=[]
    for s in specs:
        ch=s["item_id"][2:4]
        witness="ir/primary/VOLUME/CHAPTERS/ir138_"+ch+".pdf"
        path=args.source_root/witness
        sha=digest(path.read_bytes())
        if sha!=inventory[witness]["sha256"]:
            raise ValueError("Witness hash mismatch: "+witness)
        with fitz.open(path) as doc:
            stat,it=analyze(s,series(s,tables[s["table_id"]]),doc[s["source_page"]-1])
        stat.update(source_pdf_sha256=sha,plot_sha256=digest((args.out/"plots"/(s["item_id"]+".pdf")).read_bytes()))
        details.extend(it)
        stats.append(stat)
    save_csv(args.out/"scan_comparison.csv",stats)
    save_csv(args.out/"interval_comparison.csv",details)


if __name__=="__main__":
    main()
