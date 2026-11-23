"""Compare each published spectrum to its ten-band release and the three bands in each FIN file.
Comparisons are made at original printed sample intervals, with repeated entries paired in order.
"""
from collections import Counter,defaultdict,deque
from decimal import Decimal
from pathlib import Path
import argparse,csv,gzip,io,re
import numpy as np
from read_disc import sample,fixed
def key(line):
    leg,site,hole,core,ct,section,top,base,_=sample(line)
    return int(leg),int(site),hole,int(core),ct,section.lstrip('0') or '0',Decimal(top),Decimal(base)
def write(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def indexed_ten(site_root,site):
    allten=defaultdict(deque);holes=Counter()
    for p in sorted((site_root/'COLOR').glob('*.TEN')):
        for n,line in enumerate(p.read_text(encoding='latin1').splitlines(),1):
            if not line.strip():continue
            k=key(line);allten[k].append((p.name,n,sample(line)[-1],tuple(float(v) for v in fixed(line,45,6,10))));holes[k[2]]+=1
    return allten,holes
def check_site(disc,site):
    source=disc/f'SITE_{site}';allten,holes=indexed_ten(source,site)
    ten_copy={k:deque(v) for k,v in allten.items()};files=[]
    for p in sorted((source/'COLOR').glob('*.FIN')):
        # Duplicate distribution variants are independently compared with TEN from that hole.
        if b'\x00' in p.read_bytes()[:200]:
            files.append(dict(site=site,fin=p.name,status='native_binary_not_compared',fin_rows='',ten_sample_matches='',three_bands_equal='',fin_no_ten='',unparsed_matched='',mbsf_diff_on_matched=''));continue
        used=Counter();counts=Counter();depth_diff=0
        for n,line in enumerate(p.read_text(encoding='latin1').splitlines(),1):
            if not line.strip():continue
            k=key(line);i=used[k];used[k]+=1;counts['fin_rows']+=1
            if i>=len(allten[k]):continue
            fname,lineno,mbsf,v=allten[k][i]
            vals=line[42:].split()
            if len(vals)!=5:counts['unparsed']+=1;continue
            tri=tuple(float(vv) for vv in vals[:3])
            if tri==(v[0],v[4],v[8]):counts['all_three_equal']+=1
            counts['matched']+=1
            depth_diff+=Decimal(mbsf)!=Decimal(sample(line)[-1])
        files.append(dict(site=site,fin=p.name,status='compared',fin_rows=counts['fin_rows'],ten_sample_matches=counts['matched'],three_bands_equal=counts['all_three_equal'],fin_no_ten=counts['fin_rows']-counts['matched'],unparsed_matched=counts['unparsed'],mbsf_diff_on_matched=depth_diff))
    c=Counter();worst=0.;worst_path='';worst_line='';calib=Counter();miss_cal=[];spectrum_count=0
    for p in sorted((source/'COLOR'/'DATA').glob('*.REF')):
        spectrum_count+=1;lines=p.read_text(encoding='latin1').splitlines()
        m=re.search(r'Lam(?:b)?da\(nm\)\s*=\s*([+-.0-9]+)\(Pixel#\+Offset%\)\s*\+\s*([+-.0-9]+)\s+Offset\s*=\s*([+-.0-9]+)',lines[1],re.I)
        if not m:miss_cal.append(p.name);continue
        slope,b,off=map(float,m.groups());calib[(slope,b,off)]+=1
        waves=b+slope*(np.arange(1,512)+off)
        indices=[np.flatnonzero((waves>=lo)&(waves<lo+50)) for lo in range(450,950,50)]
        start=next(i for i,l in enumerate(lines) if l.strip()=='START OF DATA')+1
        end=next((i for i,l in enumerate(lines) if l.strip()=='END OF DATA'),len(lines));c['missing_end']+=end==len(lines)
        valid=[];linenos=[]
        for ix in range(start,end):
            l=lines[ix];c['ref_rows']+=1
            if len(l.rstrip())==3111 and len(l[45:].split())==511:
                valid.append(l);linenos.append(ix+1)
            else:c['invalid']+=1
        if not valid:continue
        matrix=np.fromstring(' '.join(l[45:] for l in valid),sep=' ').reshape(-1,511)
        means=np.column_stack([matrix[:,ix].mean(axis=1) for ix in indices])
        for j,l in enumerate(valid):
            k=key(l);q=ten_copy.get(k)
            if not q:continue
            fn,ln,mbsf,v=q.popleft();c['matched']+=1
            c['depth_diff']+=Decimal(sample(l)[-1])!=Decimal(mbsf)
            delta=np.abs(means[j]-np.array(v));c['pct05']+=int((delta<=.05+1e-10).sum());c['pct10']+=int((delta<=.1+1e-10).sum());c['n_bands']+=10
            if float(delta.max())>worst:worst=float(delta.max());worst_path=p.relative_to(disc).as_posix();worst_line=linenos[j]
    status=dict(site=site,ref_files=spectrum_count,calibration_versions=len(calib),unrecognized_calibration_files=','.join(miss_cal),
        ref_files_without_end_marker=c['missing_end'],ref_rows=c['ref_rows'],ten_rows=sum(holes.values()),matched_occurrences=c['matched'],ref_only_or_unparsed=c['ref_rows']-c['matched'],ten_only=sum(holes.values())-c['matched'],
        ref_rows_unparsed=c['invalid'],mbsf_diff_on_matched=c['depth_diff'],band_comparisons=c['n_bands'],bands_within_0p05_pctpoint=c['pct05'],bands_within_0p1_pctpoint=c['pct10'],max_abs_pctpoint=f'{worst:.6f}',max_error_ref_path=worst_path,max_error_ref_line=worst_line)
    return status,files
def main():
    ap=argparse.ArgumentParser();ap.add_argument('primary',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--sites',type=int,nargs='+',default=range(844,855));a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    stats=[];fin=[]
    for site in a.sites:
        s,h=check_site(a.primary.resolve(),site);stats.append(s);fin+=h
    write(a.out/'reflectance_511_to_ten.csv',stats);write(a.out/'reflectance_ten_to_three.csv',fin)
if __name__=='__main__':main()
