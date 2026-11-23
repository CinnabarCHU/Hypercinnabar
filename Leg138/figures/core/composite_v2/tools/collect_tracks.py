"""Follow released composite/FIN rows and archive hole-switch intervals without inferring original PR filter parameters."""
from bisect import bisect_right
from collections import defaultdict
from pathlib import Path
import argparse,csv,gzip,hashlib,json,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
def save(name,rows):
    with (DATA/name).open('w',newline='') as o:
        w=csv.DictWriter(o,list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def read_schema(disc_core):
    sys.path.insert(0,str(disc_core.resolve()))
    import read_disc
    return read_disc
def site_tracks(site,primary,api,manifest):
    root=primary/f'SITE_{site}';cut=root/f'SPLICE.{site}'
    pairs=[line.split() for line in cut.read_text().splitlines() if line.strip()]
    depths=np.array([float(z[0]) for z in pairs]);holes=[chr(64+int(z[1])) for z in pairs]
    if len(pairs)<2 or np.any(np.diff(depths)<0):raise ValueError(cut)
    starts=depths.tolist();series=defaultdict(list);sources=[]
    def reader(path):
        rel=path.relative_to(primary).as_posix();return rel,api.layout(rel),api.data_rows(path,rel)
    def emitted(rel,quantity,stage,valfields,unit,formula,used,total):
        m=manifest[rel]
        sources.append(dict(site=site,quantity=quantity,source_path=rel,source_url=m['url'],source_sha256=m['sha256'],source_stage=stage,
                       native_depth_field='mcd' if quantity!='splice_controls' else 'mcd_start',native_value_field=valfields,
                       source_unit=unit,conversion_to_print_axis=formula,readable_rows=total,selected_rows=used))
    ctl=cut.relative_to(primary).as_posix()
    emitted(ctl,'splice_controls','published hole-switch controls','hole_number','mcd | A=1, B=2, ...','[start,next_start)',len(pairs),len(pairs))
    for quantity,folder,pattern in [('grape','GRAPE',f'GR{site}.MCD'),('susceptibility','SUS','SUS*.FIN'),('reflectance','COLOR','COL*.FIN')]:
        direct=quantity=='grape' or (site==847 and quantity=='susceptibility')
        if site==847 and quantity=='susceptibility':pattern='SUS847.MCD'
        for path in sorted((root/folder).glob(pattern)):
            rel,fields,stream=reader(path); idx={s:i for i,s in enumerate(fields)}
            if api.classification(rel)[0]=='color_binary':
                emitted(rel,'reflectance','parallel binary witness; ASCII counterparts selected','see binary_color844.csv.gz','% reflectance','not duplicated in trace',0,0);continue
            quantity_fields={'grape':['density_g_cm3','smoothed_density_g_cm3'],'susceptibility':['susceptibility_instrument_units'],
                             'reflectance':['blue_450_500_pct','red_650_700_pct','infrared_850_900_pct']}[quantity]
            selected=total=0
            for line,status,raw in stream:
                if status!='data':continue
                total+=1;dep=float(raw[idx['mcd']]);hole=raw[idx['hole']]
                interval=bisect_right(starts,dep)-1
                if not direct and not(0<=interval<len(starts)-1 and hole==holes[interval]):continue
                core=raw[idx['core']];sect=raw[idx['section']]
                if not direct and site==844 and hole=='B' and 18.3<=dep<21.5 and core.lstrip('0')=='4':continue
                vals=[float(raw[idx[k]]) for k in quantity_fields]
                if not np.all(np.isfinite(vals)) or not np.isfinite(dep):raise ValueError((rel,line))
                # The render breaks at every section, source, hole switch, decreasing depth or large gap.
                segment=(interval,rel,hole,core,sect)
                series[quantity].append((segment,line,dep,*vals));selected+=1
            unit={'grape':'g/cm3','susceptibility':'instrument units','reflectance':'reflectance percent'}[quantity]
            conversion={'grape':'use released, uncorrected smoothed density; no additional smoothing',
                      'susceptibility':'multiply by 0.63 for the 10^-5 SI axis; IR2 PDF 20, print p32',
                      'reflectance':'three FIN fields in percent; disk README lines 163–175'}[quantity]
            stage='released composite MCD series' if direct else 'released hole FIN, independently selected with published switch controls'
            emitted(rel,quantity,stage,'|'.join(quantity_fields),unit,conversion,selected,total)
    stats=[]
    for quantity,rr in series.items():
        rr.sort(key=lambda x:(x[0][0],x[0][1],x[1]))
        dd=np.array([r[2] for r in rr]);stats.append(dict(site=site,quantity=quantity,rows=len(rr),min_mcd=round(np.min(dd),3),max_mcd=round(np.max(dd),3),
                produced_quantity='released composite smooth' if quantity=='grape' else 'published raw-unit composite × 0.63' if quantity=='susceptibility' and site==847 else 'independent FIN splice',
                figure_filter_verified='no'))
    return series,sources,stats

def runs(rr):
    result=[];current=[];prev=None
    for r in rr:
        if prev is not None and (r[0]!=prev[0] or r[2]<prev[2] or r[2]-prev[2]>.30):
            if current:result.append(np.array(current));current=[]
        current.append(r[2:]);prev=r
    if current:result.append(np.array(current))
    return result

def write_cache(primary,core,cache):
    api=read_schema(core);mp={r['path']:r for r in csv.DictReader((core/'sources.csv').open())}
    src=[];summary=[];cache.mkdir(parents=True,exist_ok=True)
    for site in range(844,855):
        series,s,st=site_tracks(site,primary,api,mp);src.extend(s);summary.extend(st)
        for kind,rr in series.items():
            seg=runs(rr);np.savez_compressed(cache/f'{site}_{kind}.npz',**{f'r{i}':a for i,a in enumerate(seg)})
    save('source_tracks.csv',src);save('site_series.csv',summary)
    print(len(src),'source mappings;',sum(int(r['rows']) for r in summary),'selected measurements in three series families.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path);p.add_argument('disc_core',type=Path);p.add_argument('cache',type=Path)
    p.add_argument('--export-site',type=int,choices=range(844,855),metavar='SITE')
    p.add_argument('--export-quantity',choices=('grape','susceptibility','reflectance'))
    a=p.parse_args()
    if a.export_site is None:
        write_cache(a.primary,a.disc_core,a.cache)
    else:
        if a.export_quantity is None:p.error('--export-site needs --export-quantity')
        api=read_schema(a.disc_core)
        manifest={r['path']:r for r in csv.DictReader((a.disc_core/'sources.csv').open())}
        data,_,_=site_tracks(a.export_site,a.primary,api,manifest)
        cols={'grape':['density_g_cm3','smoothed_density_g_cm3'],'susceptibility':['susceptibility_instrument_units'],
              'reflectance':['blue_450_500_pct','red_650_700_pct','infrared_850_900_pct']}[a.export_quantity]
        w=csv.writer(sys.stdout);w.writerow(['site','quantity','source_path','source_line','splice_interval','hole','core','section','mcd',*cols])
        for seg,line,mcd,*vals in data[a.export_quantity]:
            ix,path,hole,core,sec=seg;w.writerow([a.export_site,a.export_quantity,path,line,ix+1,hole,core,sec,mcd,*vals])
