"""Redraw chapter 6 Figure 11 from the publisher's numerical tables and compare both editions."""
import argparse
import csv
import gzip
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
from matplotlib.ticker import FixedLocator, MultipleLocator
import fitz

CORE = Path(__file__).resolve().parents[1]
CHAPTER = 'official/VOLUME/CHAPTERS/sr138_06.pdf'
CROP = (48, 48, 299, 573)
CAPTION = [
    'Figure 11. Sedimentation rates from Tables 18 through 28. Estimates are',
    'plotted at 0.1-m.y. intervals; each estimate plotted represents the mean for the',
    '0.2-m.y. interval centered on that age, derived by interpolating a depth point',
    'every 0.1 Ma from the table. Note that the values given are probably greater',
    'than the true in-situ sedimentation rates by about 10%, and somewhat more in',
    'the intervals recovered by the XCB (Hagelberg et al., 1992; Fig. 3; Harris et',
    'al., this volume).'
]

def source_records():
    sites = {site: [] for site in range(844, 855)}
    lookup = {f'SR.C06.TABLE{site-826}':site for site in sites}
    with gzip.open(CORE/'records.jsonl.gz', 'rt') as file:
        for line in file:
            record = json.loads(line)
            site = lookup.get(record['d'])
            if site is None:
                continue
            age, depth, rate = record['v']
            sites[site].append((record['n'], record['lo'], age, depth, rate))
    return sites

def redraw(out):
    out.mkdir(parents=True,exist_ok=True)
    sites=source_records()
    with (out/'SR06_Figure11_data.csv').open('w',newline='') as fh:
        writer=csv.writer(fh)
        writer.writerow(['site','source_table','row','source_line','age_ma','depth_mcd','rate_m_per_myr','panel_in_print','within_printed_age_range'])
        for site,records in sites.items():
            for row,src,age,depth,rate in records:
                writer.writerow([site,site-826,row,src,age,depth,rate,int(site<=853),int(0<=float(age)<=10)])
    left,top,right,bottom=CROP
    width,height=right-left,bottom-top
    pyplot.rcParams.update({'font.family':'Liberation Sans','font.size':6.2,'axes.linewidth':.56,
        'pdf.fonttype':42,'svg.fonttype':'none','path.simplify':False})
    figure=pyplot.figure(figsize=(width/72,height/72))
    # Source figure has two columns and five rows. The axis heights vary to maintain a common scale.
    rows=[(54.6,117.5,100),(133.3,196.1,100),(208.6,284.3,120),(295.8,390.8,150),(414,477.2,100)]
    columns=[(69.7,167),(194.8,292.5)]
    for panel,site in enumerate(range(844,854)):
        ytop,ybottom,ymax=rows[panel//2];xleft,xright=columns[panel%2]
        ax=figure.add_axes(((xleft-left)/width,(bottom-ybottom)/height,(xright-xleft)/width,(ybottom-ytop)/height))
        data=sites[site]
        ages=[float(q[2]) for q in data];rates=[float(q[4]) if q[4] else float('nan') for q in data]
        ax.plot(ages,rates,color='black',linewidth=.53,solid_joinstyle='round')
        ax.set(xlim=(0,10),ylim=(0,ymax))
        ax.yaxis.set_major_locator(FixedLocator([0,100]))
        ax.yaxis.set_minor_locator(MultipleLocator(20))
        ax.xaxis.set_major_locator(FixedLocator([0,10]))
        ax.xaxis.set_minor_locator(MultipleLocator(2))
        ax.tick_params(direction='in',which='both',left=True,bottom=True,top=False,right=False,pad=1.9,width=.42,length=1.65)
        ax.tick_params(which='major',length=2.2)
        ax.set_ylabel('m/m.y.',labelpad=-1.7,fontsize=6.1)
        if panel//2==4:
            ax.set_xlabel('Ma',labelpad=0.9,fontsize=6.1)
        ax.text(.09,1-6.5/(ybottom-ytop),f'Site {site}',ha='left',va='top',transform=ax.transAxes,fontsize=6.05)
    for i,line in enumerate(CAPTION):
        figure.text((50.5-left)/width,(bottom-506-i*9.95)/height,line,fontfamily='Liberation Serif',fontsize=7.85)
    figure.savefig(out/'SR06_Figure11.pdf',metadata={'CreationDate':None,'Title':'Shackleton et al. | Leg 138, Chapter 6, Figure 11 | reconstruction'})
    pyplot.close(figure)

def compare(out,source):
    with fitz.open(out/'SR06_Figure11.pdf') as edited,fitz.open(source) as original,fitz.open() as output:
        c=fitz.Rect(*CROP)
        page=output.new_page(width=c.width*2+35,height=c.height+47)
        for i,(pdf,pg,clip,title) in enumerate([(original,25,c,'Publisher scan | printed p. 98'),(edited,0,None,'Reconstruction | Tables 18-27')]):
            x=10+i*(c.width+15)
            page.insert_text((x,14),title,fontsize=8,fontname='hebo')
            page.show_pdf_page(fitz.Rect(x,21,x+c.width,21+c.height),pdf,pg,clip=clip)
        page.insert_text((10,c.height+38),'Table 28 (Site 854) is included in the distributed data. The printed figure has ten panels, Sites 844-853.',fontsize=7,fontname='helv')
        output.save(out/'SR06_Figure11_comparison.pdf',garbage=4,deflate=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=CORE/'figures')
    parser.add_argument('--source-pdf',type=Path)
    args=parser.parse_args()
    redraw(args.output)
    source=args.source_pdf or CORE.parent/'primary'/CHAPTER
    if source.exists():
        compare(args.output,source)
