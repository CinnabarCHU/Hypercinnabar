"""Recover numerical traces from two published vector figures for panel 8.
Coordinates are calibrated in physical units. The tables are graphical
observations; individual plotted vertices are not laboratory measurements.
"""
import argparse
from collections import defaultdict
from pathlib import Path
import fitz
import numpy as np
from scipy.io import savemat
from openpyxl import load_workbook

def profile_from_filled_stroke(d, positions):
    # IGOR's exported lines are filled outlines. The outer intersections
    # at each abscissa enclose the visible ink of this series alone.
    hits=defaultdict(list)
    for item in d['items']:
        if item[0]!='l': continue
        a,b=item[1:];lo,hi=sorted((a.x,b.x))
        i0,i1=np.searchsorted(positions,[lo,hi])
        if a.x==b.x: continue
        for i in range(i0,i1):
            hits[i].append(a.y+(positions[i]-a.x)*(b.y-a.y)/(b.x-a.x))
    return np.array([[min(hits[i]),max(hits[i])] if hits[i] else [np.nan,np.nan] for i in range(len(positions))])

def extract(w18,kt,table,out):
    doc=fitz.open(w18);page=next(p for p in doc if 'Benthic carbon isotope trends for and difference' in p.get_text())
    ds=page.get_drawings();ages=np.arange(45,61.00001,.002)
    x=517.662+(ages-61)*19.428
    records=[]
    for k in [151,152,153,154]:
        bounds=profile_from_filled_stroke(ds[k],x)
        records.append((179.46-bounds)/31.23)
    # Age, thin Atlantic, thin Pacific (min/max), thick Atlantic, thick Pacific.
    curves=np.column_stack((ages,records[0][:,1],records[0][:,0],records[1][:,1],records[1][:,0],
                            records[2].mean(axis=1),records[3].mean(axis=1)))
    doc=fitz.open(kt);p=next(pg for pg in doc if 'Composite stable' in pg.get_text() and 'Experiment 3' in pg.get_text())
    segments=[]
    for d in p.get_drawings():
        col=d['color']; r=d['rect']
        if col is None or not(col[1]>.55 and col[0]<.5 and col[2]<.35) or r.y1>239.5 or r.y1<235:continue
        pts=[]
        for item in d['items']:
            if item[0]=='l':pts.extend([tuple(item[1]),tuple(item[2])])
        if not pts:continue
        pts=np.array(pts); ab=np.unique(pts[:,0])
        ordinates=[min(pts[pts[:,0]==x,1]) for x in ab]
        # Upper plot tick centres at x=82.60 (48 Ma), x=552.41 (57 Ma).
        xy=np.c_[48+(ab-82.60)/52.2011,(np.array(ordinates)-239.08)/102.55]
        segments.append(np.vstack([[xy[0,0],0],xy,[xy[-1,0],0],[np.nan,np.nan]]))
    ws=load_workbook(table,read_only=True,data_only=True).active
    bulk=np.array([[r[11],r[12],r[13]] for r in list(ws.values)[4:] if all(isinstance(r[i],(int,float)) for i in [11,12,13])])
    ot=np.argsort(bulk[:,0]); bulk=bulk[ot]; t=bulk[:,0]/1000; y=bulk[:,1]
    # Transparent independent check from Table S1 only, using a physical
    # 2 Myr centred window over available measurements.
    mean=np.array([np.mean(y[np.abs(t-a)<=1]) for a in t]);res=y-mean;cut=res.mean()-res.std(ddof=1)
    savemat(out,dict(westerhold=curves,kirtland=np.vstack(segments),kt1258=np.c_[t,y,mean,res,np.minimum(res-cut,0)],kt_threshold=cut),do_compression=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('westerhold_pdf',type=Path);p.add_argument('kirtland_supp_pdf',type=Path);p.add_argument('kirtland_xlsx',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();extract(a.westerhold_pdf,a.kirtland_supp_pdf,a.kirtland_xlsx,a.output)
