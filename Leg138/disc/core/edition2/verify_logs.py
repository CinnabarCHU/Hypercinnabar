"""Check logging tokens against native physical lines and test independently stated product relations."""
import argparse
import csv
import gzip
import json
from collections import Counter
from decimal import Decimal as D
from pathlib import Path
from extract_fields import write_rows
RATIOS={"LIR":("CSI",("CCA","CSI")),"IIR":("CFE",("CCA","CSI")),"SIR":("CCHL",("CHY",)),"PIR":("CHY",("CCA","CSI"))}
HALF=D(".00005")
def valid(t):
    return t and "*" not in t and t!="-999.2500"
def ratio_checked(num,dens,published,scale):
    # Independent rounding envelope for published four-decimal channel readings.
    lo=D(num)-HALF;hi=D(num)+HALF;total=sum(map(D,dens))
    dmin=total-HALF*len(dens);dmax=total+HALF*len(dens)
    if dmin<=0<=dmax:return None
    v=[a/b*scale for a in (lo,hi) for b in (dmin,dmax)]
    mid=D(published)
    return min(v)<=mid+HALF and max(v)>=mid-HALF
def rows(path):
    with gzip.open(path,"rt") as f:yield from csv.DictReader(f)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("primary",type=Path);p.add_argument("output",type=Path);a=p.parse_args()
    manifest=list(csv.DictReader((a.output/"log_sources.csv").open()))
    cnt=Counter();tot=Counter();bounds=[]
    for rec in manifest:
        fname=rec["source_file"]
        src=(a.primary/fname).read_text().splitlines()
        colsrc={x["field_key"]:x for x in rows(a.output/"log_dictionary.csv.gz") if x["source_file"]==fname}
        for row in rows(a.output/rec["extract_path"]):
            ids=[int(row[k]) for k in ["source_line_1","source_line_2","source_line_3"] if row[k]]
            rebuilt=[]
            for line in ids:
                original=src[line-1].rstrip()
                for i in range(0,len(original),11):rebuilt.append(original[i:i+11].strip())
            assert rebuilt==[row[k] for k in colsrc]
            tot["physical_data_lines"]+=len(ids);tot["cell_roundtrip"]+=len(rebuilt)
            if rec["file_series"]=="ACT_GST":
                for field,(num,dens) in RATIOS.items():
                    vals=[row[k] for k in (field,num,*dens)]
                    if not all(map(valid,vals)):
                        cnt[(fname,field,"native_marker")]+=1
                        continue
                    s1=ratio_checked(vals[1],vals[2:],vals[0],1)
                    s100=ratio_checked(vals[1],vals[2:],vals[0],100)
                    if s1 is None:cnt[(fname,field,"denominator_spans_zero")]+=1
                    else:
                        cnt[(fname,field,"testable")]+=1
                        cnt[(fname,field,"ratio_consistent_with_printed_precision")]+=s1
                        cnt[(fname,field,"hundred_times_ratio_consistent")]+=s100
        if rec["file_series"]!="OX_ERROR":continue
        site=rec["directory_site"]
        product={r["DEPTH"]:r for r in rows(a.output/"logs"/("OXIDES."+site+".csv.gz"))}
        fieldsets=[("SIO2",("SIO2","SI02")),("CACO3/CAO",("CACO3/CAO","CACAO3/CAO","CACO3")),("FEO*",("FEO*",)),("TIO2",("TIO2",)),("K2O",("K2O",)),("AL2O3",("AL2O3",))]
        c=[Counter() for x in fieldsets]
        for r in rows(a.output/rec["extract_path"]):
            found=product.get(r["DEPTH"]);keys=list(colsrc)
            for i,(native,aliases) in enumerate(fieldsets):
                if not found:
                    c[i]["no_matching_depth"]+=1;continue
                k,=[k for k in aliases if k in found]
                low=r[keys[3+2*i]];high=r[keys[4+2*i]];v=found[k]
                if not all(map(valid,[v,low,high])):
                    c[i]["source_marker"]+=1;continue
                c[i]["valid"]+=1
                c[i]["inside_closed_bounds"]+=D(low)<=D(v)<=D(high)
                c[i]["reversed_bounds"]+=D(low)>D(high)
        for (field,aliases),cc in zip(fieldsets,c):
            bounds.append((site,field,"|".join(aliases),cc["valid"],cc["inside_closed_bounds"],cc["reversed_bounds"],cc["source_marker"],cc["no_matching_depth"]))
    assert tot["cell_roundtrip"]==sum(int(r["data_cells"]) for r in manifest)
    keys=sorted({(f,k) for f,k,s in cnt});write_rows(a.output/"log_ratio_tests.csv",["file","field","source_marker","denominator_rounding_interval_spans_zero","testable","within_printed_input_precision","within_precision_if_times_100"],[[f,k,*[cnt[(f,k,s)] for s in ["native_marker","denominator_spans_zero","testable","ratio_consistent_with_printed_precision","hundred_times_ratio_consistent"]]] for f,k in keys])
    write_rows(a.output/"log_oxide_bounds.csv",["site","oxide","oxide_field_variants_allowed","paired_valid_by_depth","published_value_inside_closed_bounds","inverted_bounds","source_markers","no_equal_DEPTH_token"],bounds)
    result=dict(tot); result["oxide_numeric_pairs"]=sum(r[3] for r in bounds);result["oxide_values_within_bounds"]=sum(r[4] for r in bounds)
    result["indicator_ratios"]={k:{s:sum(v for (path,f,stat),v in cnt.items() if f==k and stat==s) for s in ["testable","ratio_consistent_with_printed_precision","hundred_times_ratio_consistent"]} for k in RATIOS}
    (a.output/"logging_verification.json").write_text(json.dumps(result,indent=2)+"\n")
    print(result)
if __name__=="__main__":
    main()
