"""Compare the CHEM and TABLES distributions by sample interval and retain print-only fields."""
import argparse
import csv
from decimal import Decimal
import gzip
import json
import re
from collections import Counter
from pathlib import Path
import fitz
from extract_fields import WATER,write_rows

TABLES={844:13,845:11,846:9,847:9,848:10,849:9,850:11,851:11,852:12,853:9,854:8}
# units observed in main and continuation section of each page raster.
SITE_SAL={844:"mM",847:"‰",849:r"g\kg"}
PAGE={844:(40,158),845:(43,231),846:(34,298),847:(27,361),848:(40,716),849:(40,774),850:(35,843),851:(42,932),852:(31,997),853:(25,1047),854:(20,1082)}
def sample_key(hole,core,ctype,section,start,end):
    return (hole,int(core),ctype,int(section),Decimal(start),Decimal(end))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("ir",type=Path,help="Directory containing sibling core and primary IR trees")
    p.add_argument("output",type=Path)
    a=p.parse_args()
    with gzip.open(a.output/"water.csv.gz","rt") as f: records=list(csv.DictReader(f))
    comparisons=[];diffs=[];depths=[];extra=[];dictionary=[]
    for site,tn in TABLES.items():
        ch=site-835;item=f"IR{ch:02}.T{tn:02}"
        native=f"VOLUME/DATA/TABLES/CHAP_{ch}/TABLE.{tn}"
        pdf=f"VOLUME/CHAPTERS/ir138_{ch:02}.pdf"
        page,printed=PAGE[site]
        doc=fitz.open(a.ir/"primary"/pdf)
        src=a.ir/"core"/"edition2_native/tables"/(item.replace(".","_")+".csv") if site!=846 else a.ir/"core/site846_prior/table-09.csv"
        chapter={}
        for row in csv.DictReader(src.open()):
            if site==846:
                if row.get("row_kind")!="data": continue
                sid,interval=row["sample"].split()
                hole=row["hole_context"]
                row["pH"]=row["ph"]
            else:
                hole=row["reported_hole"][-1]
                sid=row["core_section"]
                interval=row["interval_cm"]
            core,ct,section=re.search(r"(\d+)([HX])-(\d+)$",sid).groups()
            top,bottom=re.split("[-_]",interval)
            k=sample_key(hole,core,ct,section,top,bottom)
            assert k not in chapter
            chapter[k]=row
        flags=Counter();site_rows=[r for r in records if r["directory_site"]==str(site)]
        assert len(chapter)==len(site_rows)
        for r in site_rows:
            k=sample_key(*[r[s] for s in ["hole","core","core_type","section","interval_top_cm","interval_bottom_cm"]])
            cr=chapter.pop(k)
            for field in WATER:
                if field=="ammonia" and site in [844,848]:continue
                v,u=r[field],cr[field]
                flags["cells"]+=1
                if v!=u:
                    diffs.append((site,r['source_file'],r['source_line'],native,cr['source_line'],field,v,u))
                    flags['different']+=1
                if site==844 and field=="depth_mbsf" and v!=u:
                    # Verify the independently printed row includes core-section, interval and depth.
                    line_match=re.compile(r'(?<!\d)'+re.escape(k[1].__str__()+k[2]+'-'+str(k[3]))+r'\s+'+str(int(k[4]))+'-'+str(int(k[5]))+r'\s+'+re.escape(u)+r'\s+')
                    assert line_match.search(doc[page-1].get_text(sort=True))
                    depths.append((r['source_file'],r['source_line'],v,native,cr['source_line'],u,pdf,page,printed,item,u))
        assert not chapter
        comparisons.append((site,item,len(site_rows),flags['cells'],flags['cells']-flags['different'],flags['different']))
        for field in WATER:
            unit=({"depth_mbsf":"mbsf","pH":"","salinity":SITE_SAL.get(site,"")}.get(field,"mM") if field not in ["strontium","lithium","silica","ammonia"] else "µ m" if site==851 else "µM")
            if site==844 and field=="ammonia":continue
            first=page+(1 if (site==845 and field in {"silica","ammonia"} or site==848 and field in {"lithium","silica","ammonia"} or site in {849,850} and field in {"strontium","lithium","silica","ammonia"} or site==851 and field in {"lithium","silica","ammonia"}) else 0)
            dictionary.append((site,field,unit,pdf,first,printed+first-page,item,"absent_in_CHEM" if field=="ammonia" and site==848 else "see verbatim per-site unit/header lines in native_headers.csv.gz"))
        if site==848:
            for j,r in enumerate(site_rows):
                words=doc[page].get_text('words')
                # Printed threshold verified from the page image. OCR spells it <IO.
                thresh=sorted([w for w in words if w[4].upper() in {"<IO","<10","<I0"} and 320<w[0]<400 and w[1]<225],key=lambda w:w[1])
                assert len(thresh)==10
                for field,(left,right) in {"lithium":(266,309),"silica":(309,338)}.items():
                    adjacent=[w[4] for w in words if left<w[0]<right and abs(w[1]-thresh[j][1])<2 and re.fullmatch(r"[0-9.]+",w[4])]
                    assert len(adjacent)==1 and Decimal(adjacent[0])==Decimal(r[field]),(j,field,adjacent)
                sample_reflabel=f"{r['core']}{r['core_type']}-{r['section']}"
                if j<3:hole_printed="848A"
                else:hole_printed="848B"
                extra.append((item,pdf,page+1,printed+1,j+1,sample_reflabel,hole_printed,f"{r['interval_top_cm']}-{r['interval_bottom_cm']}","ammonia","<10","µM",r["source_file"],r["source_line"],r["hole"],"matched on row order, core-section, interval and Li/Si; differing hole retained" if hole_printed[-1]!=r["hole"] else "matched row order and sample"))
    write_rows(a.output/"water_distribution_compare.csv",["site","table","paired_by_sample","compared_fields","exact_tokens_equal","different_tokens"],comparisons)
    write_rows(a.output/"water_distribution_differences.csv",["site","chem_file","chem_line","table_file","table_line","field","chem_token","table_token"],diffs)
    write_rows(a.output/"water_print_depths844.csv",["chem_file","chem_line","chem_depth","table_file","table_line","table_depth","print_file","pdf_page","printed_page","item","print_depth"],depths)
    write_rows(a.output/"water_print_units.csv",["site","field","printed_unit_literal","pdf_file","pdf_page","printed_page","item","electronic_unit_basis"],dictionary)
    write_rows(a.output/"water_print_only848.csv",["item","pdf_file","pdf_page","printed_page","print_row","print_core_section","print_hole_context","interval","field","threshold_as_printed","printed_unit","chem_file","chem_line","chem_hole","link_evidence"],extra)
    print({"paired_samples":sum(x[2] for x in comparisons),"compared_fields":sum(x[3] for x in comparisons),"differences":len(diffs),"site844_three_source_depths":len(depths),"site848_print_only_ammonia":len(extra)})
if __name__=="__main__":
    main()
