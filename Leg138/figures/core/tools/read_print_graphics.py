"""Record visually identified PR print marks and an independent horizontal-ink MAR spot check."""
import argparse
import hashlib
from pathlib import Path

import fitz
import numpy as np

from check_rates import PR_SHA, read
from read_tables import save

# Marker centres were reviewed against 4x crops of the native axes. Positions are pixel
# centres in those crops, where the first column/row has index zero. These are PR graphics
# witnesses only. No sample ID, laboratory measurement or age calibration is inferred.
MARKS = {
    847: [(8,425),(14,382),(47,199),(73,493),(105,562),(126,497),(156,181),(177,227),
          (209,515),(241,565),(270,532),(306,565),(334,532),(376,565),(411,406),
          (421,431),(432,489),(443,425),(454,511),(465,471),(486,381),(515,526),
          (560,644),(582,546),(604,536)],
    852: [(14,330),(46,108),(98,501),(148,343),(195,516),(241,421),(270,343),
          (299,150),(371,494),(414,540),(472,612)],
    853: [(54,550),(119,510),(266,489),(327,334),(409,449),(467,416),(529,481),(590,232)],
}

def build(pr):
    if hashlib.sha256(pr.read_bytes()).hexdigest() != PR_SHA:
        raise ValueError('Unexpected PR checksum')
    panels = read('pr_panel_axes.csv')
    scaled = fitz.Matrix(4,4)
    points = []
    spotchecks = []
    with fitz.open(pr) as doc:
        for panel in panels:
            if panel['quantity'] != 'organic_carbon_mar':
                continue
            site = int(panel['site'])
            if site not in MARKS and site != 848:
                continue
            l,r,t,b = [float(panel[k]) for k in ('left_pt','right_pt','top_pt','bottom_pt')]
            mx,my = float(panel['x_max_Ma']),float(panel['y_max'])
            page = doc[int(panel['pr_pdf_page'])-1]
            pix = page.get_pixmap(matrix=scaled,colorspace=fitz.csGRAY,clip=fitz.Rect(l,t,r,b))
            for index,(x,y) in enumerate(MARKS.get(site,[]),1):
                xp = (pix.x+x+.5)/4
                yp = (pix.y+y+.5)/4
                points.append(dict(site=site,pr_figure=panel['pr_figure'],pr_pdf_page=panel['pr_pdf_page'],
                                   quantity='organic_carbon_mar',graphic_mark=index,mark='+',
                                   doc_x_pt=f'{xp:.3f}',doc_y_pt=f'{yp:.3f}',
                                   age_Ma=f'{mx*(xp-l)/(r-l):.3f}',value=f'{my*(b-yp)/(b-t):.3f}',
                                   unit=panel['unit'],location_allowance_pt='1.0',
                                   age_allowance_Ma=f'{mx/(r-l):.3f}',value_allowance=f'{my/(b-t):.3f}',
                                   category='print_digitized_symbol'))
            if site == 848:
                # Narrow horizontal window on the first visible dark step; exclude the
                # text at the top and the frame at the bottom before searching all y values.
                age0,age1=.42,.57
                x0,x1=[round((l+(r-l)*age/mx)*4)-pix.x for age in [age0,age1]]
                y0,y1=round((t+15)*4)-pix.y,round((b-4)*4)-pix.y
                ink=255.-np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width)
                trace=ink[y0:y1,x0:x1].mean(axis=1)
                idx=int(np.argmax(trace))
                near=np.arange(max(0,idx-2),min(len(trace),idx+3))
                yp=(pix.y+y0+.5+np.average(near,weights=trace[near]))/4
                source=next(a for a in read('ir_mean_intervals.csv') if a['site']=='848')
                spotchecks.append(dict(site=site,pr_figure=panel['pr_figure'],pr_pdf_page=panel['pr_pdf_page'],
                    quantity='organic_carbon_mar',sample_age0_Ma=age0,sample_age1_Ma=age1,graphic_y_pt=f'{yp:.3f}',
                    pr_graphic_value=f'{my*(b-yp)/(b-t):.3f}',ir_interval_young_Ma=source['young_Ma'],
                    ir_interval_old_Ma=source['old_Ma'],ir_mean_table=source['ir_table'],
                    ir_values_source_line=source['values_source_line'],ir_print_page=728,
                    ir_table_value=source['organic_carbon_mar'],unit=panel['unit']))
    save('pr_printed_marks.csv',points)
    save('pr_mar_spotcheck.csv',spotchecks)

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('pr_pdf',type=Path)
    build(p.parse_args().pr_pdf)
