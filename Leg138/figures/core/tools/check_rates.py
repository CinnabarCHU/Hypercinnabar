"""Read the PR sedimentation staircase independently of the tabular rates, at the IR age intervals."""
from pathlib import Path
import argparse,csv,hashlib,math
from collections import Counter
import fitz
import numpy as np
from read_tables import DATA, save
PR_SHA='48f7d7e22f672f499c38d610d995ad713874cfd01bc29516cf6b2f4cbe6d18c5'
def read(name):
    with (DATA/name).open(newline='') as f:return list(csv.DictReader(f))
def build(pr):
    if hashlib.sha256(pr.read_bytes()).hexdigest()!=PR_SHA:raise ValueError('Unexpected PR PDF hash.')
    panels=read('pr_panel_axes.csv'); intervals=read('ir_mean_intervals.csv')
    results=[]; summaries=[]; s=4
    with fitz.open(pr) as d:
        for ax in (a for a in panels if a['quantity']=='sedimentation_rate'):
            page=d[int(ax['pr_pdf_page'])-1];pm=page.get_pixmap(matrix=fitz.Matrix(s,s),colorspace=fitz.csGRAY)
            ink=255.-np.frombuffer(pm.samples,np.uint8).reshape(pm.height,pm.width)
            l,r,t,b,m,max_y=map(float,(ax[k] for k in ('left_pt','right_pt','top_pt','bottom_pt','x_max_Ma','y_max')))
            checked=[]
            for val in (v for v in intervals if v['site']==ax['site']):
                ya,oa=map(float,(val['young_Ma'],val['old_Ma']));span=(r-l)*(oa-ya)/m
                start=l+(r-l)*(ya+.34*(oa-ya))/m;end=l+(r-l)*(ya+.66*(oa-ya))/m
                start=max(start,l+4.5);end=min(end,r-4.5)
                ypx=peak=diff=rate=None; status='unresolved_width'
                if oa>m or ya<0:status='outside_print_axis'
                elif end-start<1.0 and span>=4.0:status='frame_ticks_overlap_window'
                elif span>=4.0:
                    y0=math.ceil((t+1.1)*s);y1=math.floor((b-1.1)*s)
                    w=ink[y0:y1,int(round(start*s)):int(round(end*s))]
                    if not w.shape[1]:raise ValueError((span,w.shape))
                    trace=np.mean(w,axis=1);k=int(np.argmax(trace));peak=float(trace[k]);idx=np.arange(max(0,k-3),min(len(trace),k+4))
                    if peak<53:status='no_reliable_horizontal_ink'
                    else:
                        ypx=(y0+float(np.average(idx,weights=trace[idx])))/s;rate=max_y*(b-ypx)/(b-t)
                        diff=rate-float(val['sedimentation_rate'])
                        status='within_print_tolerance' if abs(diff)<=max_y*.012 else 'different_at_print_scale'
                fmt=lambda x:'' if x is None else f'{x:.3f}'
                checked.append(dict(site=ax['site'],pr_figure=ax['pr_figure'],pr_pdf_page=ax['pr_pdf_page'],ir_mean_table=val['ir_table'],values_source_line=val['values_source_line'],young_Ma=val['young_Ma'],old_Ma=val['old_Ma'],window_width_pt=fmt(span),sample_x0_pt=fmt(start) if end>start else "",sample_x1_pt=fmt(end) if end>start else "",trace_y_pt=fmt(ypx),peak_ink=fmt(peak),pr_graphic_rate_m_Myr=fmt(rate),ir_mean_table_rate=val['sedimentation_rate'],difference_m_Myr=fmt(diff),tolerance_m_Myr=fmt(max_y*.012),result=status))
            ct=Counter(row['result'] for row in checked); good=ct['within_print_tolerance'];wrong=ct['different_at_print_scale'];n=good+wrong
            diffs=[abs(float(c['difference_m_Myr'])) for c in checked if c['difference_m_Myr']]
            summ=dict(site=ax['site'],pr_figure=ax['pr_figure'],pr_pdf_page=ax['pr_pdf_page'],pr_print_page=ax['pr_print_page'],ir_mean_table=checked[0]['ir_mean_table'],total_intervals=len(checked),evaluated=n,within_tolerance=good,different_at_print_scale=wrong,unresolved=len(checked)-n,median_abs_delta_m_Myr=fmt(float(np.median(diffs))) if diffs else '',max_abs_delta_m_Myr=fmt(max(diffs)) if diffs else '',tolerance_m_Myr=fmt(max_y*.012))
            results+=checked;summaries.append(summ)
    save('pr_rate_check.csv',results);save('pr_rate_summary.csv',summaries)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('pr_pdf',type=Path);build(p.parse_args().pr_pdf)
