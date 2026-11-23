"""Check each distributed density splice against the published FIN holes using raw (uncorrected) density.
Cut intervals are left-closed/right-open. Keep original row order within each prescribed hole interval.
"""
from pathlib import Path
from decimal import Decimal as D
from bisect import bisect_right
from collections import defaultdict, deque
import argparse,csv,gzip,io
from read_disc import data_rows
def key(fields):
    return (int(fields[0]),fields[1],int(fields[2]),fields[3],fields[4].lstrip('0') or '0',*[D(x) for x in fields[5:]])
def check(disc,site,detail):
    r=disc/f'SITE_{site}';controls=[l.split() for l in (r/f'SPLICE.{site}').read_text().splitlines() if l.strip()]
    starts=[D(v[0]) for v in controls];holes=[chr(64+int(v[1])) for v in controls]
    if starts!=sorted(starts):raise ValueError('Unsorted published control points '+str(site))
    chosen=[];order_matches=0
    for p in sorted((r/'GRAPE').glob('GR*.FIN')):
        path=p.relative_to(disc).as_posix()
        for n,status,a in data_rows(p,path):
            if status!='data':continue
            depth=D(a[9]);ix=bisect_right(starts,depth)-1
            if 0<=ix<len(starts)-1 and a[2]==holes[ix]:
                chosen.append((ix,n,path,key(a[1:9]),depth,D(a[10]),D(a[12])))
    chosen.sort(key=lambda row:(row[0],row[1]));q=defaultdict(deque)
    for row in chosen:q[row[3]].append(row)
    pub=disc/f'SITE_{site}/GRAPE/GR{site}.MCD';pth=pub.relative_to(disc).as_posix()
    count=paired=equal=smooth=0;worst=D(0)
    for lineno,status,b in data_rows(pub,pth):
        if status!='data':continue
        rk=key(b[3:]);depth,y,sm=map(D,b[:3]);seq=count;count+=1
        if seq<len(chosen):
            candidate=chosen[seq];order_matches+=candidate[3]==rk and candidate[4]==depth and candidate[5]==y
        if not q[rk]:detail.writerow([site,pth,lineno,'','','','','no matched selected sample','','']);continue
        ix,n,path,_,dep,raw,smcorrected=q[rk].popleft();paired+=1;is_equal=dep==depth and y==raw;equal+=is_equal
        predicted=D('1.025')+(sm-D('1.128'))*D('1.06997')
        difference=abs(predicted-smcorrected);worst=max(worst,difference);smooth+=difference<=D('.0005')
        detail.writerow([site,pth,lineno,path,n,ix+1,'identity and occurrence',is_equal,str(difference),difference<=D('.0005')])
    for v in q.values():
        for ix,n,path,*_ in v:detail.writerow([site,'','',path,n,ix+1,'selected FIN only','','',''])
    return [site,len(starts)-1,len(chosen),count,paired,equal,order_matches,smooth,str(worst)]
def main():
    p=argparse.ArgumentParser();p.add_argument('primary',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    with (a.out/'splice_membership.csv').open('w',newline='') as summary,(a.out/'grape_source_lines.csv.gz').open('wb') as out,gzip.GzipFile(fileobj=out,mode='wb',mtime=0) as gz,io.TextIOWrapper(gz,encoding='utf-8',newline='') as det:
        d=csv.writer(det,lineterminator='\n');d.writerow(['site','release_path','release_line','fin_path','fin_line','splice_interval','pairing_basis','depth_and_uncorrected_density_equal','abs_smoothed_correction_difference_g_cm3','within_half_print_unit'])
        s=csv.writer(summary,lineterminator='\n');s.writerow(['site','splice_intervals','fin_selected_rows','released_mcd_rows','paired_samples','paired_mcd_density_equal','in_order_identity_mcd_density_equal','smoothed_within_0p0005','max_abs_smooth_residual_g_cm3'])
        for site in range(844,855):s.writerow(check(a.primary.resolve(),site,d))
if __name__=='__main__':main()
