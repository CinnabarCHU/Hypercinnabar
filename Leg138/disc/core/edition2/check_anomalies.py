"""Document how surplus splice records and spectral source-identity exceptions arise."""
import argparse
import csv
import gzip
import json
import re
import sys
from collections import Counter,deque,defaultdict
from pathlib import Path
import numpy as np
import fitz
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check_optics import key,indexed_ten
from read_disc import sample
from extract_fields import writer,write_rows

def spectra(primary,outdir):
    rows=[];candidate_rows=[]
    with writer(outdir/"optical_exceptions.csv.gz",["status","site","ref_file","ref_line","ten_file","ten_line","native_sample","max_abs_difference_pct_points","bands_above_0.1"]) as cases:
        for site in range(844,855):
            d=primary/f"SITE_{site}"
            ten,_=indexed_ten(d,site)
            references={k:deque(v) for k,v in ten.items()}
            for f in sorted((d/"COLOR"/"DATA").glob("*.REF")):
                lines=f.read_text("latin1").splitlines()
                m=re.search(r"Lam(?:b)?da\(nm\)\s*=\s*([+-.0-9]+)\(Pixel#\+Offset%\)\s*\+\s*([+-.0-9]+)\s+Offset\s*=\s*([+-.0-9]+)",lines[1],re.I)
                slope,base,offset=map(float,m.groups())
                w=base+slope*(np.arange(1,512)+offset)
                ix=[np.flatnonzero((w>=lo)&(w<lo+50)) for lo in range(450,950,50)]
                start=next(j for j,l in enumerate(lines) if l.strip()=="START OF DATA")+1
                end=next((j for j,l in enumerate(lines) if l.strip()=="END OF DATA"),len(lines))
                arr=np.fromstring(" ".join(l[45:] for l in lines[start:end]),sep=" ").reshape(end-start,511)
                means=np.column_stack([arr[:,jj].mean(axis=1) for jj in ix])
                counts=Counter();maxdiff=0.0
                rel=f.relative_to(primary).as_posix()
                for j,(mean,line) in enumerate(zip(means,lines[start:end]),start+1):
                    k=key(line)
                    if not references.get(k):
                        counts["ref_only"]+=1
                        cases.writerow(("unmatched_REF",site,rel,j,"","",line[:42].strip(),"",""))
                    else:
                        fname,n,mbsf,vals=references[k].popleft()
                        tenrel=f"SITE_{site}/COLOR/{fname}"
                        delta=np.abs(mean-np.array(vals))
                        high=int(np.sum(delta>.1+1e-10))
                        counts["match"]+=1
                        counts["high_band"]+=high
                        maxdiff=max(maxdiff,float(delta.max()))
                        if high:
                            counts["high_rows"]+=1
                            cases.writerow(("matched_bands_differ",site,rel,j,tenrel,n,line[:42].strip(),f"{delta.max():.6f}",high))
                    if site==849 and f.name=="849C02H2.REF":
                        candkey=(138,849,*k[2:])
                        cc=ten.get(candkey,[])
                        # The section's printed sampling intervals are unique in TEN.
                        assert len(cc)==1
                        fname,n,mbsf,vals=cc[0]
                        delta=np.abs(mean-np.array(vals))
                        twin=primary/"SITE_848/COLOR/DATA/848C02H2.REF"
                        other=twin.read_text().splitlines()
                        twin_line=next((t+1 for t,ll in enumerate(other) if len(ll.rstrip())==3111 and key(ll)[2:]==k[2:]),None)
                        same=other[twin_line-1][45:]==line[45:] if twin_line else ""
                        candidate_rows.append((rel,j,k[0],k[1],f"SITE_849/COLOR/{fname}",n,138,849,f"{delta.max():.6f}",int(sum(delta<=.0500000001)),twin.relative_to(primary).as_posix(),twin_line,same))
                rows.append((rel,site,start+1,end,end==len(lines),counts['match'],counts['ref_only'],counts['high_rows'],counts['high_band'],f"{maxdiff:.6f}"))
            for k,items in references.items():
                for fname,n,mbsf,_ in items:
                    cases.writerow(("unmatched_TEN",site,"","",f"SITE_{site}/COLOR/{fname}",n," ".join(map(str,k)),"",""))
    write_rows(outdir/"spectrum_file_checks.csv.gz",["ref_file","site","first_data_line","last_data_line","no_END_marker","strict_pairs","unpaired_REF","matched_rows_any_band_above_0.1","bands_above_0.1","max_abs_pct_points"],rows)
    write_rows(outdir/"spectrum849_identity_hypothesis.csv",["ref_file","ref_line","printed_leg","printed_site","candidate_ten_file","candidate_line","candidate_leg","candidate_site","max_abs_ten_band_difference","bands_within_0.05","alternative_site848_ref","alternate_line","identical_511_channels"],candidate_rows)
    return {"spectrum_files_checked":len(rows),"unpaired_ref_rows":sum(r[6] for r in rows),"matched_rows_any_band_above_0p1":sum(r[7] for r in rows),"bands_above_0p1":sum(r[8] for r in rows),"site849_hypothesis_rows":len(candidate_rows),"site849_bands_within_0p05_against_TEN":sum(r[9] for r in candidate_rows),"site848_identical_alternative_rows":sum(bool(r[-1]) for r in candidate_rows)}

def splice(primary,outdir,ir):
    core=Path(__file__).resolve().parents[1]
    with gzip.open(core/"replay/grape_source_lines.csv.gz","rt") as f:
        rows=[r for r in csv.DictReader(f) if r["site"]=="844" and r["splice_interval"]=="4"]
    f=primary/"SITE_844/GRAPE/GR844B.FIN"
    fin=f.read_text().splitlines()
    records=[]
    for r in rows:
        n=int(r["fin_line"]);v=fin[n-1].split()
        records.append([r['fin_path'],n,v[3]+v[4],v[8],v[9],v[10],r['release_path'],r['release_line'],r['pairing_basis']])
    write_rows(outdir/"splice844_overlap.csv",["fin_path","fin_line","core","mbsf","mcd","uncorrected_density","mcd_path","mcd_line","status"],records)
    assert Counter((r[2],bool(r[7])) for r in records)=={("3H",True):157,("4H",False):157}
    # Full site recipe with this identified second coring excluded must preserve published order.
    with gzip.open(core/"replay/grape_source_lines.csv.gz","rt") as f:
        chosen=[(int(r['splice_interval']),int(r['fin_line']),int(r['release_line'])) for r in csv.DictReader(f) if r["site"]=="844" and r["release_line"]]
    confirmed=sorted(chosen)==chosen and [r[-1] for r in chosen]==list(range(1,len(chosen)+1))
    assert confirmed
    doc=fitz.open(ir/"primary/VOLUME/CHAPTERS/ir138_09.pdf")
    assert "same sedimentary interval was cored again" in doc[2].get_text()
    return {"splice_cut":"SITE_844/SPLICE.844 lines 4–5, Hole B, 18.3 <= mcd < 21.5","core_offset_source":"COREDATA/844.ADJ lines 5–6 (+2.25 m for 3H, -8.55 m for 4H)","operational_context":"IR09 pp. 121,146 (PDF pages 3,28); 4H re-cored the same interval after 3H","published_3H_rows":157,"additional_4H_rows":157,"published_site844_order_recovered_with_explicit_core_exclusion":len(chosen)}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("primary",type=Path);p.add_argument("ir",type=Path);p.add_argument("output",type=Path)
    a=p.parse_args()
    report=splice(a.primary,a.output,a.ir)
    report.update(spectra(a.primary,a.output))
    (a.output/"anomalies_verification.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(report)
if __name__=="__main__":
    main()
