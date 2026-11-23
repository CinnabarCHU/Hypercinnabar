"""Build provenance manifest and a paired visual comparison from verified witnesses."""
import argparse
import json
from pathlib import Path

import fitz
from render import HERE, LEG, digest, rows, save_csv

REL = "revision/figures_depth"


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source_root",type=Path)
    p.add_argument("--out",type=Path,default=HERE)
    args=p.parse_args()
    specs=json.loads((HERE/"layout.json").read_text())
    stats={r["item_id"]:r for r in rows(args.out/"scan_comparison.csv")}
    notes={r["item_id"]:r for r in rows(HERE/"observations.csv")}
    data={r["item_id"]:r for r in rows(LEG/"ir/core/native_tables.csv")}
    inv={r["local_path"]:r for r in rows(LEG/"data/source_inventory.csv.gz")}
    manifest=[]
    atlas=fitz.open()
    for s in specs:
        key=s["item_id"]
        ch=key[2:4]
        witnesses="ir/primary/VOLUME/CHAPTERS/ir138_"+ch+".pdf"
        native=data[s["table_id"]]
        table="ir/primary/"+native["source_path"]
        rawpath=args.source_root/witnesses
        st=stats[key]
        note=notes[key]
        pdf=args.out/"plots"/(key+".pdf")
        if digest(rawpath.read_bytes())!=st["source_pdf_sha256"] or digest(pdf.read_bytes())!=st["plot_sha256"]:
            raise ValueError(f"{key}: comparison hash is stale")
        scope="all_published_data_panels" if note["comparison_class"]=="print_consistent" else "published_table_reconstruction_with_print_notes"
        manifest.append(dict(item_id=key,source_page=s["source_page"],source_kind="published native tabulation, verified against original printed diagrams",
            inputs="ir/core/native_lines.csv.gz|"+REL+"/layout.json",table_ids=s["table_id"],renderer=REL+"/render.py",
            output=REL+"/plots/"+key+".pdf",redraw_extent=scope,qualification=note["notes"],
            comparison_class=note["comparison_class"],printed_page=s["printed_page"],table_pdf_page=s["table_pdf_page"],
            table_printed_page=s["table_printed_page"],source_pdf_sha256=st["source_pdf_sha256"],
            source_pdf_url=inv[witnesses]["url"]+"#page="+str(s["source_page"]),native_source=table,
            native_url=inv[table]["url"],native_sha256=native["sha256"],plot_sha256=st["plot_sha256"],
            scan_agreement_fraction=st["agreement_fraction"],intervals=st["plotted_intervals"]))
        page=atlas.new_page(width=595,height=510)
        page.insert_text((24,23),f"Site {native['site']}  |  {key}  |  {s['table_id']}",fontname="hebo",fontsize=13)
        l,t,r,b=s["frame_pdf_xyxy_pt"]
        cx,cy=s["caption_pdf_xy_pt"]
        left_margin=max(36.0,l-cx+3)
        original_clip=fitz.Rect(l-left_margin,t-27,r+8,cy+len(s["caption_lines"])*9+8)
        with fitz.open(rawpath) as src, fitz.open(pdf) as redrawn:
            im=src[s["source_page"]-1].get_pixmap(matrix=fitz.Matrix(2,2),clip=original_clip,colorspace=fitz.csGRAY)
            plotw,ploth=redrawn[0].rect.width,redrawn[0].rect.height
            for left,txt in [(24,f"Original print, p. {s['printed_page']}"),(313,"Redrawn from table")]:
                page.insert_text((left,45),txt,fontsize=9,fontname="helv")
            box=fitz.Rect(24,54,24+plotw,54+ploth)
            page.insert_image(box,stream=im.tobytes("png"))
            page.show_pdf_page(box+fitz.Rect(289,0,289,0),redrawn,0)
        summary=f"Plateau probes within 1.25% of rate-axis span: {100*float(st['agreement_fraction']):.1f}% ({st['probes']} probes)."
        page.insert_text((24,449),summary,fontsize=8.7,fontname="hebo")
        text=note["notes"].replace("–","-").replace("−","-")
        page.insert_textbox(fitz.Rect(24,457,567,501),text,fontsize=9,fontname="helv",lineheight=1.17)
        page.insert_link({"kind":fitz.LINK_URI,"from":fitz.Rect(24,32,190,50),"uri":manifest[-1]["source_pdf_url"]})
    atlas.set_metadata(dict(title="Leg 138 sedimentation rates: printed traces and native-table reconstruction",
        author="Leg 138 digital collation",subject="22 paired shipboard age/depth diagrams"))
    atlas.save(args.out/"Sedimentation_Rate_Comparison.pdf",garbage=4,deflate=True,no_new_id=True)
    atlas.close()
    save_csv(args.out/"manifest.csv",manifest)


if __name__=="__main__":
    main()
