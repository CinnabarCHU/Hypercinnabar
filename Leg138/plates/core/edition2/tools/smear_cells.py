"""Map the official PDF text layer to the scanned grid of every smear-slide page.

Column names come from the checked ordered headers. Blanks and numerical tokens remain
source-text candidates until a scan reading is entered. PDF coordinates are upper-left points.
"""
import argparse
import csv
import gzip
import io
import json
import re
from collections import defaultdict,Counter
from pathlib import Path

import fitz
import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import binary_closing,label

from export_regions import BASE,rows

SCALE=2


def grid(gray,ncols):
    """Detect horizontal rules, then fit the repeated composition columns to their actual ink peaks."""
    h=(gray[:,40:-45]<215).mean(axis=1)
    ypos,_=find_peaks(h,height=.42,prominence=.16,distance=11)
    split=1+int(np.argmax(np.diff(ypos[:min(8,len(ypos))])))
    y=ypos[split:]
    step=np.diff(y)/SCALE
    if not len(step) or min(step)<9 or max(step)>12:
        raise ValueError(f'Irregular row pitch: {step}')
    profile=(gray[y[0]:y[-1],:]<218).mean(axis=0)
    band=gray[y[0]-5:y[0]+6].min(axis=0)<215
    labelled,groups=label(binary_closing(band,structure=np.ones(13)))
    spans=[np.where(labelled==group)[0] for group in range(1,groups+1)]
    ruled=max(spans,key=len)
    x0=int(ruled[0]);xf=int(ruled[-1])
    if not 490*SCALE<xf-x0<520*SCALE:
        raise ValueError(f'Unexpected ruled width: {(xf-x0)/SCALE} pt')
    # Column one is the wider sample label. Locate the second boundary and a regular lattice
    # from the depth column onward, using the field count read independently from each scan.
    p1=x0+round(43.6*SCALE)
    x1=p1-4+int(np.argmax(profile[p1-4:p1+5]))
    candidates=[]
    for x2 in range(x0+round(59*SCALE),x0+round(80*SCALE)):
        equal=np.rint(np.linspace(x2,xf,ncols-1)).astype(int)
        score=sum(float(profile[v]) for v in equal)
        candidates.append((score,equal))
    _,equal=max(candidates,key=lambda pair:pair[0])
    xpos=[x0,x1]
    for p in equal:
        left,right=max(0,p-3),min(len(profile),p+4)
        xpos.append(left+int(np.argmax(profile[left:right])))
    x=np.array(xpos)
    if len(x)!=ncols+1 or min(np.diff(x))<25:
        raise ValueError(f'Irregular column pitch: {x/SCALE}')
    return x,y


def label_status(field,text,ink):
    if not text:
        return 'ink_without_text' if ink>=4 else 'no_text_low_ink'
    if field=='sample_label':
        return 'source_identifier_token'
    if field=='lithology':
        return 'source_lithology_marker' if text in ('D','M') else 'check_lithology_token'
    if field=='depth_mbsf':
        return 'source_numeric_token' if re.fullmatch(r'\d*\.\d+|\d+',text) else 'check_depth_token'
    if text=='*':
        return 'source_trace_symbol'
    return 'source_numeric_token' if re.fullmatch(r'\d{1,3}',text) and int(text)<=100 else 'check_composition_token'


def write(path,items):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)


def build(primary,source_data,out):
    fieldsets=defaultdict(list)
    for r in rows(out/'smear_field_dictionary.csv'):
        fieldsets[r['site']].append(r['field_key'])
    inherited={(r['printed_page'],r['page_row'],r['field_key']):r for r in rows(out/'smear_846_inherited_review.csv')}
    plates=[p for p in rows(source_data/'plate_sources.csv') if p['document_kind']=='smear_slide_book']
    visual={r['cell_id']:r for r in rows(out/'smear_visual_reviews.csv')}
    folios={(r['site'],int(r['pdf_page'])):r['printed_page'] for r in rows(out/'smear_folio_readings.csv')}
    page_records=[];row_records=[];cells=[];matched=set();registration=[]
    for source in plates:
        site=source['site'];fields=fieldsets[site]
        with fitz.open(primary/source['source_path']) as d:
            for page_n,p in enumerate(d,1):
                pix=p.get_pixmap(matrix=fitz.Matrix(SCALE,SCALE),colorspace=fitz.csGRAY,alpha=False)
                gray=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width)
                try:x,y=grid(gray,len(fields))
                except ValueError as e:raise ValueError(f'{site}/{page_n} {e}') from e
                assigned=defaultdict(list); printed=''
                source_words=p.get_text('words')
                # Anchor the original text layer to the printed body using the first sample's
                # identifier. Some PDF pages place the hidden text about one grid row too low.
                possible_first=[w for w in source_words if x[0]<(w[0]+w[2])*SCALE/2<x[1]
                     and (y[0]-4*SCALE)<(w[1]+w[3])*SCALE/2<y[0]+3*(y[1]-y[0])
                     and re.match(r'^(?:[A-E]-)?[1-9Il]\d?-(?:[0O]?\d|CC)',w[4],flags=re.I)]
                if not possible_first:
                    raise ValueError(f'Missing first sample text-layer anchor: {site}/{page_n}')
                witness=min(possible_first,key=lambda w:w[1])
                estimated=(y[0]+y[1])/(2*SCALE)-(witness[1]+witness[3])/2
                yshift=round(estimated,2) if abs(estimated)>3 else 0.
                source_centres=[];printed_centres=[]
                if yshift:
                    markers=sorted([w for w in source_words if x[0]<(w[0]+w[2])*SCALE/2<x[1]
                           and y[0]/SCALE-5<(w[1]+w[3])/2<y[-1]/SCALE+18
                           and re.match(r'^(?:[A-E]-)?[1-9Il]\d?-(?:[0O]?\d|CC)',w[4],flags=re.I)],
                           key=lambda w:(w[1]+w[3])/2)
                    if len(markers)!=len(y)-1:
                        raise ValueError(f'Incomplete ordered row anchors: {site}/{page_n}')
                    source_centres=[(w[1]+w[3])/2 for w in markers]
                    printed_centres=[(a+b)/(2*SCALE) for a,b in zip(y,y[1:])]
                    for rr,(mark,sy,py) in enumerate(zip(markers,source_centres,printed_centres),1):
                        registration.append(dict(site=site,pdf_page=page_n,page_row=rr,sample_anchor=mark[4],source_y_pt=round(sy,3),printed_y_pt=py,offset_pt=round(py-sy,3)))
                for word in source_words:
                    a,b,c,e,txt=word[:5]
                    if b>p.rect.height*.9 and re.fullmatch(r'\d{3,4}',txt):printed=txt
                    yp=(b+e)/2
                    if source_centres:
                        shifted=yp+float(np.interp(yp,source_centres,np.array(printed_centres)-np.array(source_centres)))
                    else:shifted=yp
                    xc,yc=(a+c)*SCALE/2,shifted*SCALE
                    col,row=np.searchsorted(x,xc,'right')-1,np.searchsorted(y,yc,'right')-1
                    if 0<=row<len(y)-1 and 0<=col<len(x)-1:
                        assigned[(row,col)].append((a,txt))
                printed=printed or folios.get((site,page_n),'')
                assert printed,(site,page_n)
                page_records.append(dict(source_text_y_shift_pt=yshift,registration_method="ordered sample anchors" if yshift else "native coordinates",source_first_sample_anchor=witness[4],site=site,pdf_page=page_n,printed_page=printed,
                     source_path=source['source_path'],source_sha256=source['sha256'],source_url=source['url']+f'#page={page_n}',
                     printed_rows=len(y)-1,printed_columns=len(fields),body_left_pt=x[0]/SCALE,body_top_pt=y[0]/SCALE,
                     body_right_pt=x[-1]/SCALE,body_bottom_pt=y[-1]/SCALE,coordinate_units='PDF points from upper left'))
                for i,(y0,y1) in enumerate(zip(y,y[1:])):
                    row_id=f'S{site}.P{page_n:02}.R{i+1:03}'
                    row_values=[];edition_values=[]
                    for j,(x0,x1,field) in enumerate(zip(x,x[1:],fields)):
                        text=' '.join(tok for _,tok in sorted(assigned[(i,j)]))
                        ink=int(np.sum(gray[y0+3:y1-3,x0+3:x1-3]<145))
                        check=label_status(field,text,ink)
                        rec= dict(cell_id=row_id+f'.C{j+1:02}',row_id=row_id,site=site,pdf_page=page_n,printed_page=printed,
                                  page_row=i+1,column_ordinal=j+1,field_key=field,x0_pt=x0/SCALE,y0_pt=y0/SCALE,
                                  x1_pt=x1/SCALE,y1_pt=y1/SCALE,source_ocr_literal=text,status=check,interior_dark_pixels=ink,
                                  edition_reading=text,reading_evidence='source text layer and located cell')
                        key=(printed,str(i+1),field)
                        if site=='846' and key in inherited:
                            rec['edition_reading']=inherited[key]['prior_edition_reading']
                            rec['reading_evidence']='inherited Site 846 visual cell decision'
                            matched.add(key)
                        correction=visual.get(rec['cell_id'])
                        if correction:
                            rec['edition_reading']=correction['visually_read_value']
                            rec['reading_evidence']='second-edition visual cell decision'
                        cells.append(rec);row_values.append(text);edition_values.append(rec['edition_reading'])
                    row_records.append(dict(row_id=row_id,site=site,pdf_page=page_n,printed_page=printed,page_row=i+1,
                        source_path=source['source_path'],sample_ocr_literal=row_values[0],depth_ocr_literal=row_values[1],
                        lithology_ocr_literal=row_values[2],sample_edition_literal=edition_values[0],depth_edition_literal=edition_values[1],
                        lithology_edition_literal=edition_values[2],y0_pt=y0/SCALE,y1_pt=y1/SCALE))
    if len(matched)!=len(inherited):
        raise ValueError(f'Inherited decisions not matched: {set(inherited)-matched}')
    write(out/'smear_grid_pages.csv',page_records);write(out/'smear_rows.csv',row_records)
    write(out/'smear_text_registration.csv',registration)
    with (out/'smear_cells.csv.gz').open('wb') as target:
        with gzip.GzipFile(filename='',fileobj=target,mode='wb',mtime=0) as bundle:
            with io.TextIOWrapper(bundle,encoding='utf-8',newline='') as output:
                w=csv.DictWriter(output,fieldnames=list(cells[0]));w.writeheader();w.writerows(cells)
    decisions=Counter(c['reading_evidence'] for c in cells)
    report=dict(pages=len(page_records),printed_rows=len(row_records),printed_grid_cells=len(cells),
            sites=len(plates),visually_read_field_counts_by_site={site:len(fs) for site,fs in fieldsets.items()},
            status_counts=dict(Counter(c['status'] for c in cells)),edition_evidence_counts=dict(decisions),
            inherited_visual_decisions=len(matched),new_visual_decisions=len(visual),
            new_visual_decisions_changed_text=sum(c['source_ocr_literal']!=c['edition_reading'] for c in cells if c['reading_evidence']=='second-edition visual cell decision'),
            manually_read_missing_printed_folios=len(folios),
            adjusted_text_layers=[(r['site'],r['pdf_page'],r['source_text_y_shift_pt']) for r in page_records if r['source_text_y_shift_pt']])
    (out/'smear_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(len(page_records),'pages',len(row_records),'rows',len(cells),'cells',len(matched),'inherited decisions')
    print(dict(Counter(c['status'] for c in cells)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path)
    p.add_argument('--catalog',type=Path,default=BASE.parent/'data');p.add_argument('--out',type=Path,default=BASE/'data')
    a=p.parse_args();build(a.primary,a.catalog,a.out)
