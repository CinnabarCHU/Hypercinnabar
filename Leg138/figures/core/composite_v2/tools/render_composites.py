"""Draw released composite tracks on calibrated PR frames and preserve the remaining source layers."""
from collections import defaultdict
from pathlib import Path
import argparse,csv,hashlib,io,math
import fitz
import numpy as np
from matplotlib.path import Path as MplPath
from scipy.stats import spearmanr
from PIL import Image
from collect_tracks import ROOT,DATA,save

PR_SHA='48f7d7e22f672f499c38d610d995ad713874cfd01bc29516cf6b2f4cbe6d18c5'
PUBLIC=ROOT/'vector'
KNOWN_KINDS={'grape','susceptibility','reflectance'}
STYLES=[(.31,(.29,.29,.29),'[] 0'),(.33,(.14,.14,.14),'[2.3 1.5] 0'),(.4,(.10,.10,.10),'[.48 1.35] 0')]

def value(a,*ks):
    for k in ks:
        if k in a and a[k]!='':return a[k]
    raise KeyError((ks,a))
def read_regions():
    return list(csv.DictReader((DATA/'panel_regions.csv').open()))
def gaussian20(v):
    # Explicit editorial display choice. Weights are renormalized at each segment end.
    kern=np.exp(-.5*((np.arange(20)-9.5)/4.)**2)
    return np.convolve(v,kern,'full')[9:len(v)+9]/np.convolve(np.ones(len(v)),kern,'full')[9:len(v)+9]

def data_for(cache,site,kind):
    with np.load(cache/f'{site}_{kind}.npz') as z:
        segs=[z[k] for k in z.files]
    tracks=[]
    for s in segs:
        if kind=='grape':
            tr=s[:,[0,2]]
        elif kind=='susceptibility':
            tr=np.column_stack([s[:,0],gaussian20(s[:,1])*.63])
        else:
            tr=np.column_stack([s[:,0],*[gaussian20(s[:,i]) for i in (1,2,3)]])
        tracks.append(tr)
    return tracks

def get_bounds(a):
    x0,y0,x1,y1=map(float,[value(a,k) for k in ['x0_pt','y0_pt','x1_pt','y1_pt']])
    xmin,xmax,d0,d1=map(float,[value(a,k) for k in ['x_min','x_max','depth_top_m','depth_bottom_m']])
    assert x1>x0 and y1>y0 and xmax!=xmin and d1>d0
    return fitz.Rect(x0,y0,x1,y1),(xmin,xmax,d0,d1)

def vectors(panel,frames,segs,kind):
    rect,axis=frames;w,h=rect.width,rect.height;amin,amax,d0,d1=axis
    sub=fitz.open();p=sub.new_page(width=w,height=h)
    count=[0]*(3 if kind=='reflectance' else 1)
    for vi in range(len(count)):
        shape=p.new_shape()
        for trace in segs:
            depths=trace[:,0];mask=(depths>=d0-.35)&(depths<=d1+.35)
            a=trace[mask]
            if len(a)==0:continue
            points=np.column_stack([(a[:,vi+1]-amin)/(amax-amin)*w,(a[:,0]-d0)/(d1-d0)*h])
            count[vi]+=int(np.count_nonzero((a[:,0]>=d0)&(a[:,0]<=d1)))
            if len(points)<2:continue
            # Reduce vector vertices at sub-point print resolution. Source values remain untouched.
            route=MplPath(points);route.simplify_threshold=.17
            clean=route.cleaned(simplify=True)
            vertices=clean.vertices[clean.codes!=MplPath.STOP].tolist()
            if len(vertices)>=2:shape.draw_polyline(vertices)
        width,color,dash=STYLES[vi] if kind=='reflectance' else (.37,(.12,.12,.12),'[] 0')
        shape.finish(color=color,width=width,dashes=dash,lineCap=0,lineJoin=1);shape.commit()
    # White replaces the original curve interior only; the printed header, frame and legend stay in the original column.
    inner=fitz.Rect(rect.x0+.4,rect.y0+.4,rect.x1-.4,rect.y1-.4)
    panel.draw_rect(inner,color=None,fill=(1,1,1))
    # show_pdf_page clips vector strokes at the calibrated panel boundary.
    if any(count):
        clip=fitz.Rect(.4,.4,w-.4,h-.4);panel.show_pdf_page(inner,sub,0,clip=clip)
    sub.close()
    return count

def compare_print(p,frames,segs,blank_intervals=''):
    rect,axis=frames;amin,amax,d0,d1=axis;s=3
    pm=p.get_pixmap(matrix=fitz.Matrix(s,s),clip=rect,colorspace=fitz.csGRAY)
    im=255.-np.frombuffer(pm.samples,np.uint8).reshape(pm.height,pm.width)
    intervals=[tuple(map(float,q.split('–'))) for q in blank_intervals.split('|') if q and '–' in q]
    pred=[];graph=[];errors=[]
    for d in np.linspace(d0,d1,135)[3:-3]:
        if any(a<=d<=b for a,b in intervals):continue
        options=[np.interp(d,tr[:,0],tr[:,1]) for tr in segs if len(tr)>1 and tr[0,0]<=d<=tr[-1,0]]
        if len(options)!=1:continue
        y=rect.y0+(d-d0)/(d1-d0)*rect.height;j=round(y*s)-pm.y
        # Exclude printing on the vertical frame. Read the dark-trace median at depth.
        line=im[max(j-1,0):j+2,:].max(axis=0)
        line[:8]=line[-8:]=0
        peak=np.max(line)
        xs=np.flatnonzero(line>=max(35,.40*peak)) if peak>=40 else []
        if not 1<=len(xs)<=im.shape[1]*.50:continue
        midpoint=(pm.x+np.median(xs)+.5)/s
        g=amin+(midpoint-rect.x0)/rect.width*(amax-amin);v=options[0]
        if not min(amin,amax)<=v<=max(amin,amax):continue
        pred.append(v);graph.append(g);errors.append(abs(v-g))
    if len(errors)<8:return dict(scan_depths_tested=len(errors),spearman_r='',median_abs_axis_units='',median_abs_percent_span='')
    return dict(scan_depths_tested=len(errors),spearman_r=f'{spearmanr(pred,graph).statistic:.3f}',
        median_abs_axis_units=f'{np.median(errors):.3f}',median_abs_percent_span=f'{100*np.median(errors)/abs(amax-amin):.2f}')

def jpg_image(p,rect):
    pm=p.get_pixmap(matrix=fitz.Matrix(2.45,2.45),colorspace=fitz.csGRAY,clip=rect)
    im=Image.frombytes('L',(pm.width,pm.height),pm.samples);buff=io.BytesIO()
    im.save(buff,format='JPEG',quality=89,optimize=True);return buff.getvalue()
def addtext(p,at,text,size=11,bold=False,color=(.12,.21,.22)):
    p.insert_text(at,text,fontsize=size,fontname='hebo' if bold else 'helv',color=color)
def fitrect(target,source):
    sc=min(target.width/source.width,target.height/source.height)
    w=source.width*sc;h=source.height*sc
    x=target.x0+(target.width-w)/2;y=target.y0+(target.height-h)/2
    return fitz.Rect(x,y,x+w,y+h)
def build(pr,cache):
    if hashlib.sha256(pr.read_bytes()).hexdigest()!=PR_SHA:raise ValueError('Unexpected primary PR PDF')
    regs=read_regions();group=defaultdict(list)
    for a in regs:group[(int(a['site']),int(value(a,'source_page','pdf_page','pr_pdf_page')))].append(a)
    assert len(group)==22
    bench=[];alternatives=[];layers=[];index=[];PUBLIC.mkdir(exist_ok=True)
    data_cache={}
    with fitz.open(pr) as official,fitz.open() as atlas:
        for k,((site,num),rs) in enumerate(sorted(group.items()),1):
            source=official[num-1];fig=value(rs[0],'figure','pr_figure');fid=fig if fig.startswith('PR.F') else 'PR.F'+fig
            layer_name=f'{fid.replace(".","_")}_p{num:03d}'
            by_kind={a['panel']:a for a in rs}
            assert set(by_kind)==KNOWN_KINDS,(site,num,rs)
            with fitz.open() as overlay:
                op=overlay.new_page(width=source.rect.width,height=source.rect.height)
                used_bounds=[];page_counts={}
                for kind in ['grape','susceptibility','reflectance']:
                    a=by_kind[kind];fr=get_bounds(a);used_bounds.append(fr[0]);di=(site,kind)
                    if di not in data_cache:data_cache[di]=data_for(cache,site,kind)
                    series=data_cache[di];count=vectors(op,fr,series,kind)
                    page_counts[kind]=count[0]
                    reported=kind!='reflectance'
                    if reported:
                        stats=compare_print(source,fr,series,a.get('trace_blank_mcd',''))
                        bench.append(dict(site=site,pr_figure=fid,pdf_page=num,panel=kind,**stats))
                        name='GRAPECOR corrected density, calculated from MCD smooth' if kind=='grape' else 'instrument readings without 0.63 conversion'
                        others=[]
                        for tr in series:
                            raw=tr.copy()
                            raw[:,1]=1.025+(raw[:,1]-1.128)*1.06997 if kind=='grape' else raw[:,1]/.63
                            others.append(raw)
                        alternatives.append(dict(site=site,pr_figure=fid,pdf_page=num,panel=kind,alternative_stage=name,
                            plotted_median_abs_percent_span=stats['median_abs_percent_span'],**compare_print(source,fr,others,a.get('trace_blank_mcd',''))))
                    n=1 if kind!='reflectance' else 3
                    layers.append(dict(site=site,pr_figure=fid,pdf_page=num,panel=kind,curves=n,source_samples_in_depth_window=count[0],
                         status='independent_data_redraw' if count[0] else 'no_selected_samples_in_printed_depth_window',
                         historical_20_point_filter_reproduced='no',plot_values='published MCD smoothed uncorrected GRAPE' if kind=='grape' else 'independently displayed magnetic susceptibility at 0.63 × instrument units' if kind=='susceptibility' else 'independently displayed 450–500, 650–700, 850–900 nm reflectances',
                         vector_page=f'vector/{layer_name}.pdf',source_index='data/source_tracks.csv'))
                overlay.set_metadata({'title':f'Leg 138 Site {site} | physical-track overlay | PR PDF {num}'})
                overlay.save(PUBLIC/(layer_name+'.pdf'),garbage=4,deflate=True,no_new_id=True)
                # The same overlay is used at exactly the same scale for the comparison page and the download.
                p=atlas.new_page(width=1040,height=768);margin=28
                addtext(p,(margin,28),'OCEAN DRILLING PROGRAM  /  LEG 138',9,True,(.23,.38,.38))
                addtext(p,(margin,58),f'Site {site}   /   Composite stratigraphic summary',22,True)
                addtext(p,(margin,80),f'{fid}  -  Preliminary Report PDF page {num}     |     Age, polarity, lithology and units retained as printed in both columns.',10)
                p.draw_line((margin,88),(1012,88),color=(.63,.73,.72),width=.7)
                addtext(p,(margin,105),'Published figure',12,True);addtext(p,(534,105),'Released numerical series redrawn in the original frames',12,True)
                end=max(u.y1 for u in used_bounds)
                cut=fitz.Rect(24,58,source.rect.x1-19,min(source.rect.y1-24,max(end+155,497)))
                a1=fitrect(fitz.Rect(margin,111,506,690),cut);a2=fitz.Rect(a1.x0+506,a1.y0,a1.x1+506,a1.y1)
                srcbytes=jpg_image(source,cut);xref=p.insert_image(a1,stream=srcbytes);p.insert_image(a2,xref=xref)
                p.show_pdf_page(a2,overlay,0,clip=cut)
                p.draw_line((margin,700),(1012,700),color=(.62,.70,.70),width=.7)
                addtext(p,(margin,715),f'Data rows in this depth window   GRAPE {page_counts["grape"]:,}    |    susceptibility {page_counts["susceptibility"]:,}    |    each reflectance band {page_counts["reflectance"]:,}',10,True)
                addtext(p,(margin,731),'GRAPE uses the published smoothed density. Susceptibility and reflectance use a documented editorial Gaussian. The original PR filter is unresolved.',9)
                if site==845 and num==38:
                    addtext(p,(margin,759),'PR reflectance is blank below about 232 mcd on this page; the right column includes later released measurements.',8,False,(.24,.35,.34))
                addtext(p,(margin,746),'Reflectance styles     solid = blue (450-500 nm)     dashed = red (650-700 nm)     dotted = near-infrared (850-900 nm).  Gaps retain the source limits.',8.5)
                addtext(p,(978,749),f'{k} / 22',8.5)
                index.append(dict(site=site,pr_figure=fid,pdf_page=num,atlas_page=k,vector_overlay=f'vector/{layer_name}.pdf',published_source_sha256=PR_SHA))
        atlas.set_metadata({'title':'ODP Leg 138 | Composite stratigraphic summaries | released numerical series and original figures'})
        atlas.save(ROOT/'Leg138_PR_Composite_Atlas.pdf',garbage=4,deflate=True,no_new_id=True)
    save('figure_layers.csv',layers);save('scan_trace_checks.csv',bench);save('alternative_scale_checks.csv',alternatives);save('figure_index.csv',index)
    print(f'Wrote {len(index)} paired pages, {len(layers)} physical panels and {len(bench)} single-trace checks.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('pr_pdf',type=Path);p.add_argument('cache',type=Path);a=p.parse_args();build(a.pr_pdf,a.cache)
