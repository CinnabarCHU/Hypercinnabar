"""Read plotted carbon anomalies in Kirtland Turner et al. (2014), Fig. 1c."""
from pathlib import Path
import argparse
import fitz
import numpy as np

def extract(source,destination):
    pg=fitz.open(source)[1]
    lines=[]
    for d in pg.get_drawings():
        c=d['color'];r=d['rect']
        if not c or not(c[1]>c[0] and c[1]>c[2] and c[1]>.5):continue
        if r.x0<85 or r.x1>245 or abs(r.y1-318.74)>.12 or r.y0<245:continue
        points=[(p.x,p.y) for item in d['items'] if item[0]=='l' for p in item[1:3]]
        if not points:continue
        points=np.array(points);x=np.unique(points[:,0]);y=np.array([min(points[points[:,0]==a,1]) for a in x])
        t=48+(x-100.636)/( (243.622-100.636)/9 )
        z=(y-318.723)/((318.723-287.512))
        lines.extend([[t[0],0],*zip(t,z),[t[-1],0],[np.nan,np.nan]])
    np.savetxt(destination,lines,delimiter=',',fmt='%.8f',header='age_Ma,excess_delta13C_permil',comments='')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('paper',type=Path);p.add_argument('out',type=Path);a=p.parse_args();extract(a.paper,a.out)
