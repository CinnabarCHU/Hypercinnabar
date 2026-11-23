"""Compare optical file bytes, data sections and channel strings without equating repeat scans."""
import argparse
import csv
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from extract_fields import write_rows
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("primary",type=Path);p.add_argument("output",type=Path);a=p.parse_args()
    groups=defaultdict(list)
    checks={r["ref_file"]:r for r in csv.DictReader(gzip.open(a.output/"spectrum_file_checks.csv.gz","rt"))}
    for f in sorted(a.primary.glob("SITE_*/COLOR/DATA/*.REF")):
        path=f.relative_to(a.primary).as_posix();r=checks[path];raw=f.read_bytes()
        lines=raw.splitlines()[int(r["first_data_line"])-1:int(r["last_data_line"])]
        assert lines and len(lines[0].rstrip())==3111
        obj=(path,len(lines),int(r["unpaired_REF"]))
        for mode,data in [("download_bytes",raw),("data_lines_lf",b"\n".join(lines)),("511_channels_printed_lf",b"\n".join(l[45:].rstrip() for l in lines))]:
            groups[(mode,hashlib.sha256(data).hexdigest())].append(obj)
    out=[];report={}
    for (mode,sha),objects in groups.items():
        if len(objects)>1:
            for obj in objects:out.append((mode,sha,len(objects),*obj))
            report[mode]=report.get(mode,0)+1
    write_rows(a.output/"spectrum_duplicate_groups.csv",["equality_basis","sha256","group_size","file","rows","unpaired_REF_using_strict_identity_and_order"],out)
    variants=["SITE_854/COLOR/DATA/854C06H6.REF","SITE_854/COLOR/DATA/854X06H6.REF"]
    data=[(a.primary/file).read_text().splitlines() for file in variants]
    assert data[0][:4]==data[1][:4]
    variants_rows=[]
    for i,(first,second) in enumerate(zip(*data),1):
        if len(first.rstrip())==3111 and len(second.rstrip())==3111:
            assert first[:45]==second[:45]
            v1=list(map(float,first[45:].split()))
            v2=list(map(float,second[45:].split()))
            deltas=[abs(x-y) for x,y in zip(v1,v2)]
            variants_rows.append((i,i,first[:45].strip(),len(deltas),sum(d==0 for d in deltas),round(max(deltas),3)))
    assert len(variants_rows)==49
    write_rows(a.output/"spectrum854_variant_rows.csv",["854C06H6_REF_line","854X06H6_REF_line","same_source_sample_and_offset","channels","identical_published_channel_values","largest_difference_pct_points"],variants_rows)
    report={"exact_file_groups":report,"compared_REF_files":len(checks),"site854_variant_files":variants,"variant_source_scan_metadata_equal":True,"variant_rows_same_sample_and_offset":len(variants_rows),"variant_rows_all_511_values_equal":sum(x[4]==511 for x in variants_rows),"largest_variant_difference_pct_points":max(x[5] for x in variants_rows)}
    (a.output/"spectrum_duplicate_summary.json").write_text(json.dumps(report,indent=2)+"\n")
    print(report)
if __name__=="__main__":main()
