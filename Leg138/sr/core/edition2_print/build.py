"""Locate print table bodies by their ruling, map visible words to table rows and columns."""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import subprocess
from collections import Counter,defaultdict
from functools import lru_cache
from pathlib import Path
import fitz
import numpy as np
from scipy import ndimage

def csvrows(file):
    with file.open() as inp:return list(csv.DictReader(inp))
def jsonlines(file):
    with gzip.open(file,'rt') as inp:return [json.loads(line) for line in inp]
def writecsv(path,keys,rows):
    with path.open('w',newline='') as out:
        w=csv.DictWriter(out,keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def in_box(box,point):
    return box[0]<=point[0]<=box[2] and box[1]<=point[1]<=box[3]
def rounded(box):
    return [round(v,2) for v in box]
def center(w):
    return (w[0]+w[2])/2,(w[1]+w[3])/2
def united(words):
    return [min(w[0] for w in words),min(w[1] for w in words),max(w[2] for w in words),max(w[3] for w in words)]
def orient(b,height,angle,inverse=False):
    if not angle:return list(b)
    x0,y0,x1,y1=b
    return [y0,height-x1,y1,height-x0] if inverse else [height-y1,x0,height-y0,x1]

def scan_rules(im,scale):
    # Thickening in y allows small scan skew without closing word spaces in x.
    black=im<224
    strokes=ndimage.maximum_filter1d(black,size=5,axis=0)
    closed=ndimage.minimum_filter1d(ndimage.maximum_filter1d(strokes,3,axis=1),3,axis=1)
    length=int(scale*40)
    long=ndimage.maximum_filter1d(ndimage.minimum_filter1d(closed,length,axis=1),length,axis=1)
    features,ct=ndimage.label(long)
    rules=[]
    for yc,xc in ndimage.find_objects(features):
        if (yc.stop-yc.start)/scale>11:continue
        x0,x1=xc.start/scale,xc.stop/scale
        y=(yc.start+yc.stop-1)/(2*scale)
        rules.append((x0,y,x1))
    # Parallel panels sometimes have separate rulings separated by a narrow gutter.
    original=sorted(rules,key=lambda b:(b[1],b[0]))
    for l,y,r in original:
        joined=r
        for lx,yy,rx in sorted((rr for rr in original if abs(rr[1]-y)<2),key=lambda z:z[0]):
            if lx<=joined+26 and rx>joined and lx>l:
                joined=rx
        if joined>r+8:
            rules.append((l,y,joined))
    return sorted(rules,key=lambda b:b[1])

@lru_cache(maxsize=14)
def scanned(pdf_file,pagenum,angle):
    doc=fitz.open(pdf_file);p=doc[pagenum-1];scale=1.6
    pix=p.get_pixmap(matrix=fitz.Matrix(scale,scale).prerotate(angle),colorspace=fitz.csGRAY,alpha=False)
    im=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width)
    rules=scan_rules(im,scale)
    if angle:
        hires=p.get_pixmap(matrix=fitz.Matrix(2.7,2.7).prerotate(angle),colorspace=fitz.csGRAY)
        res=subprocess.run(['tesseract','stdin','stdout','--psm','6','tsv'],input=hires.tobytes('png'),capture_output=True,check=True)
        vv=csv.DictReader(io.StringIO(res.stdout.decode('utf8',errors='replace')),delimiter='\t');words=[]
        for v in vv:
            if v['level']!='5' or not v['text'].strip():continue
            x,y,w,h=[float(v[k])/2.7 for k in ('left','top','width','height')]
            words.append((x,y,x+w,y+h,v['text']))
    else:
        words=[(*v[:4],v[4]) for v in p.get_text('words')]
    return words,rules,p.rect.height,im.shape[1]/scale,im.shape[0]/scale

def anchors(core):
    objects=[r for r in csvrows(core/'edition2/data/objects.csv') if r['status']=='accepted']
    active={r['item_id']:r for r in objects if r['kind']=='table'}
    result=[]
    for r in active.values():
        result.append(dict(item_id=r['item_id'],chapter=int(r['chapter']),source=r['source'],page=int(r['pdf_page']),printed=int(r['print_page']) if r['print_page'].isdigit() else '',angle=int(r['reading_orientation_deg']),caption=json.loads(r['source_bbox_pt']),part='starts',title=r['caption_or_heading_first_line']))
    used={(s['item_id'],s['page'],tuple(s['caption'])) for s in result}
    for r in jsonlines(core/'edition2/data/candidate_lines.jsonl.gz'):
        if r['item_id'] not in active or not re.match(r'^\s*table\s+[\dIl]+[A-Za-z]?[.\s(,-]*(?:contin|cont\.)',r['text'],re.I):continue
        key=(r['item_id'],r['pdf_page'],tuple(r['bbox']))
        if key in used:continue
        used.add(key)
        result.append(dict(item_id=r['item_id'],chapter=int(r['chapter']),source=r['source'],page=int(r['pdf_page']),printed=r['print_page'],angle=0,caption=r['bbox'],part='continued',title=r['text']))
    return active,result,objects

@lru_cache(maxsize=14)
def actual_caption_blocks(pdf,page):
    p=fitz.open(pdf)[page-1]
    lines=p.get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks']
    result={}
    for block in lines:
        if 'lines' not in block:continue
        ll=block['lines']
        for i,line in enumerate(ll):
            tx=''.join(x['text'] for x in line['spans']).strip()
            if not re.match(r'^table\s+[\dIl]+',tx,re.I):continue
            x0,y0,x1,y1=line['bbox'];end=y1
            for other in ll[i+1:]:
                ox,oy,ex,ey=other['bbox']
                if abs(ox-x0)>18 or oy<end-4 or oy>end+7 or ey-y0>90:break
                if other['spans'][0]['font']!=line['spans'][0]['font']:break
                end=ey
            result[(round(x0),round(y0))]=end
    return result

def body_region(s,words,rules,H,W,height,neighbours,override,caption_end=0):
    cap=orient(s['caption'],H,s['angle']);x0,y0,x1,y1=cap
    if override:
        return (*override,'visually_pinned')
    y1=max(y1,caption_end)
    near=[]
    for left,y,right in rules:
        overlap=min(x1,right)-max(x0,left)
        if y>=y1-1.5 and y<y1+76 and ((left<=x0+18 and right>=x0+38) or overlap>min(x1-x0,right-left)*.55):
            near.append((y-y1+abs(left-x0)*.025-min(3,(right-left)/80),(left,y,right)))
    if not near:return None
    l,t,r=min(near,key=lambda c:c[0])[1]
    # Stop before another accepted caption overlapping the current horizontal footprint.
    limit=height-21
    for n in neighbours:
        if n==s:continue
        nb=orient(n['caption'],H,s['angle'])
        if nb[1]>t+10 and min(r,nb[2])-max(l,nb[0])>min(r-l,nb[2]-nb[0])*.45:
            limit=min(limit,nb[1]-1)
    similar=[(a,y,b) for a,y,b in rules if t+5<y<limit and abs(a-l)<max(11,(r-l)*.07) and abs(b-r)<max(11,(r-l)*.07)]
    mid=similar[0][1] if similar and similar[0][1]-t<=70 else None
    trailing=[q for q in similar[1:] if mid and q[1]>mid+6]
    if mid and trailing:
        return l,t,r,trailing[0][1],mid,'rule_candidate'
    # Some continuations and mini-tables lack a full-width closing rule.
    bands=baselines([w for w in words if in_box((l-1,t+2,r+1,limit-1),center(w))])
    lines=[]
    for row in bands:
        aa=united(row);yy=center(aa)[1];tt=[w[4] for w in row]
        numeric=sum(bool(re.search(r'\d',v)) for v in tt)
        codes=sum(bool(re.fullmatch(r'(?:NA|ND|TR|[ABCFPR?+×-]|[+−-]?\d[\d.,-]*)',v)) for v in tt)
        tableline=(numeric>=2 and (numeric+codes>=len(tt)*.60 or len(tt)<9)) or (codes>=3 and codes>=len(tt)*.40)
        lines.append((aa,yy,tableline,' '.join(tt)))
    if not mid:
        starts=[j for j,v in enumerate(lines[:-1]) if v[2] and lines[j+1][2] and 9<v[1]-t<90]
        if not starts:return None
        j=starts[0];mid=(lines[j-1][0][3]+lines[j][0][1])/2 if j else lines[j][0][1]-.5
    seq=[]
    for bb,yy,good,tt in lines:
        if yy<=mid:continue
        if re.match(r'^(?:Notes?[:.]|Table \d|Figure \d|References$)',tt,re.I):break
        if good:
            if seq and bb[1]-seq[-1][3]>32:break
            seq.append(bb)
        elif seq and len(tt.split())>=8 and not re.search(r'\d',tt):break
    if len(seq)>=2:
        bottom=min(limit,max(b[3] for b in seq)+1)
        return l,t,r,bottom,mid,'rule_and_aligned_rows_candidate'
    return None

def baselines(words):
    lines=[]
    for w in sorted(words,key=lambda a:(center(a)[1],a[0])):
        cy=center(w)[1];h=w[3]-w[1]
        if not lines or abs(cy-np.median([center(x)[1] for x in lines[-1]]))>max(1.75,min(4.0,h*.43)):
            lines.append([])
        lines[-1].append(w)
    return [sorted(row,key=lambda w:w[0]) for row in lines]

def columns(body,l,r):
    # Whitespace persistent through physical baselines. Long table labels can occupy more than one column.
    n=max(1,int(np.ceil(r-l)));occ=np.zeros(n);supports=np.zeros(n)
    for row in body:
        mark=np.zeros(n,dtype=np.uint8)
        for w in row:
            a=max(0,int(w[0]-l));b=min(n,int(np.ceil(w[2]-l)))
            mark[a:b]=1
        occ+=mark; supports+=ndimage.maximum_filter1d(mark,size=min(n,19))
    nrows=len(body)
    if nrows<2:return []
    gap=occ<=max(0,int(nrows*.06))
    groups=[];a=None
    for j,res in enumerate([*gap,False]):
        if res and a is None:a=j
        if a is not None and not res:
            width=j-a
            if a>0 and j<n and width>=2 and np.max(occ[max(0,a-23):a])>=max(2,nrows*.16) and np.max(occ[j:min(n,j+23)])>=max(2,nrows*.16):groups.append(l+(a+j)/2)
            a=None
    return groups

def assign(words,bounds):
    out=defaultdict(list)
    for w in words:
        col=int(np.searchsorted(bounds,center(w)[0]))
        out[col].append(w)
    return out

def generate(core,outdir,only=None):
    active,allsegments,objects=anchors(core)
    known=defaultdict(list)
    for k,file in [('digital','datasets.csv'),('earlier_print','print_datasets.csv'),('edition2_print','edition2/data/print_datasets.csv')]:
        for rec in csvrows(core/file):known[rec['item_id']].append((k,rec['dataset_id'],rec.get('site','')))
    segs=allsegments
    if only:segs=[s for s in allsegments if s['chapter'] in only]
    outdir.mkdir(parents=True,exist_ok=True)
    override_path=Path(__file__).resolve().parent/'visual_regions.csv'
    manual={};review={}
    if override_path.exists():
        for e in csvrows(override_path):
            key=(e['item_id'],int(e['pdf_page']),e['part'])
            if e['reading_frame_ltrb_header_bottom']:
                manual[key]=list(map(float,e['reading_frame_ltrb_header_bottom'].split(',')))
            review[key]=e['review_status'],e['notes']
    locations=defaultdict(list)
    for s in allsegments:locations[(s['chapter'],s['page'])].append(s)
    for r in objects:
        if r['kind']!='table':
            locations[(int(r['chapter']),int(r['pdf_page']))].append(dict(caption=json.loads(r['source_bbox_pt'])))
    collected=defaultdict(list);segments=[];dictionary=[]
    with gzip.GzipFile(filename=str(outdir/'cells.jsonl.gz'),mode='wb',mtime=0) as gz:
        for s in sorted(segs,key=lambda s:(s['chapter'],s['page'],s['caption'][1],s['caption'][0])):
            path=core.parent/'primary'/s['source']
            identifier=s['item_id'];segkey=(identifier,s['page'],s['part'])
            words,rules,H,W,height=scanned(str(path),s['page'],s['angle'])
            capend=actual_caption_blocks(str(path),s['page']).get((round(s['caption'][0]),round(s['caption'][1])),0) if not s['angle'] else 0
            region=body_region(s,words,rules,H,W,height,locations[(s['chapter'],s['page'])],manual.get(segkey),capend)
            review_state,note=review.get(segkey,('pending_visual_review',''))
            rows=0;nc=0;nn=0;head_count=0;span_count=0;tablebox=[];headerbox=[];numwords=0
            state='no_verified_body_region';key_base=f"{identifier}.p{s['page']}.{s['part']}"
            if region:
                l,t,r,b,mid,basis=region
                tablebox=rounded(orient([l,t,r,b],H,s['angle'],True));headerbox=rounded(orient([l,t,r,mid],H,s['angle'],True))
                head=baselines([w for w in words if in_box((l-1,t,r+1,mid),center(w))])
                is_sparse=(identifier=='SR.C12.TABLE14' and s['page']==29)
                token_basis='rotated_scan_tesseract' if s['angle'] else 'publisher_pdf_word_layer'
                if is_sparse:
                    from curate_sparse import read
                    words=[w for w in words if center(w)[1]<=mid]+read(path)
                    token_basis='publisher_headers_and_manual_raster_marks'

                body=baselines([w for w in words if in_box((l-1,mid+0.01,r+1,b),center(w))])
                bounds=[89,133,176] if is_sparse else columns([row for row in body if len(row)>=2],l,r);nc=len(bounds)+1
                rows=len(body);head_count=len(head);numwords=sum(len(row) for row in body)
                state='located_cell_candidates' if body and head and nc>=2 else 'located_body_partial_geometry'
                if body and head and review_state=='sample_geometry_checked' and nc>=2:state='sample_geometry_checked'
                fields=defaultdict(list)
                for role,lines in [('header',head),('body',body)]:
                    for idx,row in enumerate(lines,1):
                        for col,ww in assign(row,bounds).items():
                            bb=united(ww);c0=int(np.searchsorted(bounds,bb[0]));c1=int(np.searchsorted(bounds,bb[2]))
                            text=' '.join(w[4] for w in ww)
                            if role=='header':fields[col].append(text)
                            if c0!=c1:span_count+=1
                            if role=='body':nn+=1
                            rec=dict(item_id=identifier,segment=key_base,pdf_page=s['page'],role=role,row=idx,col=col+1,col_first=c0+1,col_last=c1+1,token_basis=token_basis,text=text,bbox=rounded(orient(bb,H,s['angle'],True)),tokens=[[w[4],*rounded(orient(w[:4],H,s['angle'],True))] for w in ww])
                            gz.write((json.dumps(rec,ensure_ascii=False,separators=(',',':'))+'\n').encode())
                for col in range(nc):
                    domain=([l]+bounds+[r])[col:col+2]
                    dictionary.append(dict(item_id=identifier,segment=key_base,pdf_page=s['page'],col=col+1,header_as_located=' | '.join(fields.get(col,[])),reading_x_interval_pt=json.dumps(rounded(domain)),status='positional_header_candidate'))
            elif review_state=='raster_body_only':
                state='raster_body_only'
            record=dict(item_id=identifier,chapter=s['chapter'],segment=key_base,part=s['part'],source=s['source'],pdf_page=s['page'],print_page=s['printed'],reading_orientation_deg=s['angle'],caption_bbox_pt=json.dumps(s['caption']),body_bbox_pt=json.dumps(tablebox),header_bbox_pt=json.dumps(headerbox),body_locator=(basis if region else ''),status=state,review=review_state,physical_header_rows=head_count,physical_body_rows=rows,position_columns=nc,body_cells=nn,body_words=numwords,cells_crossing_gutter=span_count,notes=note)
            collected[identifier].append(record);segments.append(record)
    coverage=[]
    for item,r in active.items():
        if only and int(r['chapter']) not in only:continue
        ss=collected[item];prior=known.get(item,[])
        coverage.append(dict(item_id=item,chapter=r['chapter'],source=r['source'],start_pdf_page=r['pdf_page'],start_print_page=r['print_page'],pdf_pages='|'.join(map(str,sorted({x['pdf_page'] for x in ss}))),segments=len(ss),located_segments=sum(bool(x['body_cells']) for x in ss),physical_body_rows=sum(x['physical_body_rows'] for x in ss),body_cells=sum(x['body_cells'] for x in ss),prior_dataset_ids='|'.join(x[1] for x in prior),prior_sources='|'.join(dict.fromkeys(x[0] for x in prior)),prior_print_site_scope='|'.join(dict.fromkeys(x[2] for x in prior if x[2])),new_geometry_priority='existing_dataset' if prior else 'previously_unstructured',review='|'.join(dict.fromkeys(x['review'] for x in ss)),status='all_detected_segments_have_cells' if ss and all(x['body_cells'] for x in ss) else ('some_detected_segments_have_cells' if any(x['body_cells'] for x in ss) else 'no_body_cells'),caption=r['caption_or_heading_first_line']))
    writecsv(outdir/'coverage.csv',coverage[0].keys(),coverage)
    writecsv(outdir/'segments.csv',segments[0].keys(),segments)
    with gzip.GzipFile(filename=str(outdir/'field_dictionary.csv.gz'),mode='wb',mtime=0) as gz, io.TextIOWrapper(gz,encoding='utf8',newline='') as outf:
        w=csv.DictWriter(outf,['item_id','segment','pdf_page','col','header_as_located','reading_x_interval_pt','status'],lineterminator='\n');w.writeheader();w.writerows(dictionary)
    print('tables',len(coverage),'segments',len(segments),'with cells',sum(bool(s['body_cells']) for s in segments),'cells',sum(s['body_cells'] for s in segments),flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('core',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--chapters',nargs='+',type=int);a=ap.parse_args();generate(a.core,a.output,a.chapters)
