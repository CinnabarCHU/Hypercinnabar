"""Preserve printed ruling geometry and candidate row spans of taxon-matrix grouping labels."""
import argparse,csv,gzip,io,json,re
from collections import defaultdict
from pathlib import Path
import fitz
import numpy as np
from scipy import ndimage as nd
from build import csvrows

def lines(im,vertical,scale):
    if vertical:im=im.T
    mask=im<201
    mask=nd.maximum_filter1d(mask,3,axis=0)
    mask=nd.minimum_filter1d(nd.maximum_filter1d(mask,3,axis=1),3,axis=1)
    k=int(scale*28)
    mask=nd.maximum_filter1d(nd.minimum_filter1d(mask,k,axis=1),k,axis=1)
    cc,total=nd.label(mask);ans=[]
    for yy,xx in nd.find_objects(cc):
        if yy.stop-yy.start>10*scale:continue
        y=(yy.start+yy.stop-1)/(2*scale)
        ans.append((xx.start/scale,y,xx.stop/scale))
    return ans

def gzipcsv(path,fields,rr):
    with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as gz,io.TextIOWrapper(gz,encoding='utf8',newline='') as out:
        w=csv.writer(out,lineterminator='\n');w.writerow(fields);w.writerows(rr)
def main():
    p=argparse.ArgumentParser();p.add_argument('core',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    ss={r['segment']:r for r in csvrows(a.output/'segments.csv') if r['review'].startswith('matrix_region_checked')}
    cells=defaultdict(list)
    with gzip.open(a.output/'cells.jsonl.gz','rt') as inp:
        for line in inp:
            r=json.loads(line)
            if r['segment'] in ss and r['role']=='body': cells[r['segment']].append(r)
    rules=[];groups=[];scale=2.2
    for seg,r in ss.items():
        pg=fitz.open(a.core.parent/'primary'/r['source'])[int(r['pdf_page'])-1]
        rect=fitz.Rect(*json.loads(r['body_bbox_pt']))
        pix=pg.get_pixmap(matrix=fitz.Matrix(scale,scale),clip=rect,colorspace=fitz.csGRAY);im=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width);allrules=[]
        for vertical in [False,True]:
            for u,z,v in lines(im,vertical,scale):
                xy=[z,u,z,v] if vertical else [u,z,v,z]
                x0,y0,x1,y1=[xy[k]+(pix.y if k%2 else pix.x)/scale for k in range(4)]
                coords=[round(c,2) for c in (x0,y0,x1,y1)]
                rules.append([r['item_id'],seg,r['pdf_page'],'vertical' if vertical else 'horizontal',*coords,'raster_stroke_candidate'])
                if not vertical:allrules.append((x0,y0,x1))
        cc=cells[seg];rows=defaultdict(list)
        for c in cc:rows[c['row']].append((c['bbox'][1]+c['bbox'][3])/2)
        yy={k:np.median(v) for k,v in rows.items()}
        for c in cc:
            x=(c['bbox'][0]+c['bbox'][2])/2;y=(c['bbox'][1]+c['bbox'][3])/2
            if x>rect.x0+rect.width*.31 or not re.search(r'[A-Za-z]{3}',c['text']) or re.search(r'\d',c['text']):continue
            crossing=[z for l,z,rgt in allrules if l<=x<=rgt]
            top=max((z for z in crossing if z<y-2),default=None);bottom=min((z for z in crossing if z>y+2),default=None)
            if top is None or bottom is None or bottom-top<14:continue
            covered=[k for k,z in yy.items() if top<z<bottom]
            if len(covered)<2:continue
            groups.append([r['item_id'],seg,r['pdf_page'],c['row'],c['col'],c['text'],min(covered),max(covered),round(top,2),round(bottom,2),'candidate ruled interval; inheritance unverified'])
    gzipcsv(a.output/'grid_rulings.csv.gz',['item_id','segment','pdf_page','orientation','x0','y0','x1','y1','status'],rules)
    gzipcsv(a.output/'row_span_candidates.csv.gz',['item_id','segment','pdf_page','label_row','col','label_text','covered_row_first','covered_row_last','upper_rule_y_pt','lower_rule_y_pt','scope_status'],groups)
if __name__=='__main__':main()
