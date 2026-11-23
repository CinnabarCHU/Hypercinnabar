"""Calibrate the printed physical-property axes in the 22 PR composite pages.

Coordinate convention is PyMuPDF points from the upper left of the PDF page.
Printed tick values were transcribed from each individual scan. Edge and tick
locations are measured at 2 pixels/point. Frame-end values are inferred from
printed ticks, whose labels are slightly misregistered on several source pages.
"""
import argparse
import csv
import hashlib
from pathlib import Path

import fitz
import numpy as np

SCALE = 2
PANEL_NAMES = ('grape', 'susceptibility', 'reflectance')
UNITS = ('g/cm³', '10^-5 SI', '% reflectance')
# First physical-property frame x, upper and lower data frame y, start depth,
# and 10 m depth-tick calibration on the separate composite-depth ruler.
# The last two parameters are the measured slope (pt/m) and bottom-most
# explicitly numbered tick within the frame. Continued pages have own seeds.
PAGES = {
    33:(844,3,238,187.5,641,0,3.026,140), 34:(844,3,290.5,193,647,150,3.028,290),
    37:(845,6,257.5,189.5,649,0,3.068,140), 38:(845,6,255.5,192,651.5,150,3.06,290),
    41:(846,9,259.5,190,649,0,3.062,140), 42:(846,9,257,201.5,661,150,3.064,290),
    43:(846,9,257.5,202,661.5,300,3.064,440), 46:(847,12,257,188.5,648,0,3.056,140),
    47:(847,12,252.5,194.5,532.5,150,3.028,260), 51:(848,16,253,198,517.5,0,3.028,100),
    54:(849,19,254,192,650,0,3.054,140), 55:(849,19,249,189.5,648.5,150,3.054,290),
    56:(849,19,238,196,462,300,3.022,380), 59:(850,22,258,192,651,0,3.06,140),
    60:(850,22,239,198.5,657,150,3.054,290), 61:(850,22,278,200.5,526,300,3.02,400),
    64:(851,25,241,187,646,0,3.058,140), 65:(851,25,256,194,653,150,3.058,290),
    66:(851,25,236.5,200.5,464,300,3.028,380), 69:(852,28,240.5,191,651,0,3.066,140),
    72:(853,31,209.5,206,443,0,3.044,70), 75:(854,34,283.5,201,354.5,0,3.046,50),
}
# Minimum/maximum calibrated values at the frame, then the printed tick labels.
G1=(1,2,(1.2,1.4,1.6,1.8))
G2=(1.3,2,(1.5,1.7,1.9))
G3=(1.3,1.9,(1.4,1.6,1.8))
G4=(1.2,1.8,(1.3,1.5,1.7))
C1=(10,80,(30,50,70))
C2=(0,100,(20,40,60,80))
C3=(20,100,(40,60,80))
C4=(20,100,(30,60,90))
AXES = {
    844:(G1,(0,80,(20,40,60)),C1), 845:(G1,(0,60,(10,30,50)),C1),
    846:(G2,(-1,6,(1,3,5)),C1), 847:((1.2,1.7,(1.3,1.4,1.5,1.6)),(-1,5,(0,2,4)),C1),
    848:((1.3,1.8,(1.4,1.5,1.6,1.7)),(-2,30,(5,15,25)),C2),
    849:(G3,(-2,6,(0,2,4)),C3), 850:(G3,(-2,6,(0,2,4)),C3),
    851:(G4,(-2,12,(0,5,10)),C4), 852:(G4,(0,25,(5,10,15,20)),C2),
    853:((1.3,1.7,(1.4,1.5,1.6)),(0,40,(10,20,30)),(0,100,(25,50,75))),
    854:((1.25,1.55,(1.3,1.4,1.5)),(0,100,(20,40,60,80)),(10,70,(20,40,60))),
}
# Three continued susceptibility axes explicitly carry a scale-change notice.
CHANGED = {43:(-10,60,(10,30,50)), 56:(0,25,(5,10,15,20)), 61:(0,20,(5,10,15))}
SHORT = {47,51,56,61,66,72,75}
APPARATUS = {
    (38,'reflectance'):'Printed reflectance ends at about 232 mcd. Lower panel remains blank to 300 mcd.',
    (38,'grape'):'Print gap at about 242–252 mcd. Curve resumes below.',
    (38,'susceptibility'):'Print gap at about 242–252 mcd. Curve resumes below.',
    (69,'grape'):'Site 852 frame extends to 150 mcd. The curve ends around 130 mcd.',
    (69,'susceptibility'):'Site 852 frame extends to 150 mcd. The curve ends around 130 mcd.',
    (69,'reflectance'):'Site 852 frame extends to 150 mcd. The curves end around 130 mcd.',
}
COLUMNS = ['doc_id','site','figure','source_page','panel','x0_pt','y0_pt','x1_pt','y1_pt',
           'x_min','x_max','x_ticks','unit','depth_top_m','depth_bottom_m','ink','spectral_band',
           'status','notes','x_tick_pts','header_bottom_x0_pt','header_bottom_x1_pt','floor_x0_pt',
           'floor_x1_pt','depth_axis','first_numbered_depth_m','last_numbered_depth_m',
           'depth_tick_pitch_pt_per_m','frame_depth_basis','frame_x_basis','trace_blank_mcd',
           'numeric_band_nm','legend_source_page','printed_style','rgb_max_channel_difference','source_pdf_sha256',
           'x_frame_measured_min','x_frame_measured_max','x_tick_fit_max_residual_pt']


def peak_center(signal, estimate, tolerance):
    """Find the ink ridge closest to the seeded location, including its subpixel width."""
    amin = max(1, round(SCALE*(estimate-tolerance)))
    amax = min(len(signal)-2, round(SCALE*(estimate+tolerance)))
    ix = amin + int(np.argmax(signal[amin:amax+1]))
    if signal[ix] < 21:
        raise ValueError(f'Faint or absent printed mark around {estimate} pt ({signal[ix]:.1f})')
    near = np.arange(ix-1,ix+2)
    weights = np.maximum(0, signal[near] - .18*signal[ix])
    return float(np.average(near,weights=weights))/SCALE


def plot_geometry(ink, left_seed, ytop_seed, ybot_seed):
    x = slice(round((left_seed+4)*SCALE), round((left_seed+72)*SCALE))
    y_profile = ink[:,x].mean(axis=1)
    top = peak_center(y_profile,ytop_seed,2.5)
    bottom = peak_center(y_profile,ybot_seed,2.5)
    upper_profile = ink[round((top-29)*SCALE):round((top-7)*SCALE)].mean(axis=0)
    lower_profile = ink[round((bottom-12)*SCALE):round((bottom-1)*SCALE)].mean(axis=0)
    lt = peak_center(upper_profile,left_seed,2.5)
    rt = peak_center(upper_profile,left_seed+76,2.5)
    lb = peak_center(lower_profile,lt,2.5)
    rb = peak_center(lower_profile,rt,2.5)
    return lt,rt,lb,rb,top,bottom


def measured_ticks(ink,top,left,right,axis):
    xmin,xmax,labels = axis
    pixel_slice = slice(round(top*SCALE)-6,round(top*SCALE)-1)
    tick_profile = ink[pixel_slice].mean(axis=0)
    return [peak_center(tick_profile,left+(right-left)*(v-xmin)/(xmax-xmin),2.5) for v in labels]


def blank_ranges(ink,left,right,top,bottom,start_m,end_m):
    """Continuous uninked intervals ≥4 m after a 4 pt crop inside the panel rails."""
    lo = round(top*SCALE)+3
    hi = round(bottom*SCALE)-2
    interior = ink[lo:hi,round((left+4)*SCALE):round((right-4)*SCALE)]
    present = (interior > 65).any(axis=1)
    edges = np.flatnonzero(np.diff(np.pad((~present).astype(int),(1,1))))
    ranges=[]
    for low, high in zip(edges[::2],edges[1::2]):
        a = start_m+((lo+low)/SCALE-top)*(end_m-start_m)/(bottom-top)
        b = start_m+((lo+high)/SCALE-top)*(end_m-start_m)/(bottom-top)
        if b-a>=4:
            ranges.append(f'{a:.1f}–{b:.1f}')
    return '|'.join(ranges)


def calibrate(path):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    output=[]
    with fitz.open(path) as pdf:
        for page_no,(site,fig,x_seed,y_top,y_bottom,z0,pitch,last_depth) in PAGES.items():
            page = pdf[page_no-1]
            gray = page.get_pixmap(matrix=fitz.Matrix(SCALE,SCALE),colorspace=fitz.csGRAY)
            ink = 255.-np.frombuffer(gray.samples,np.uint8).reshape(gray.height,gray.width)
            for i,name in enumerate(PANEL_NAMES):
                try:
                    lt,rt,lb,rb,top,bottom = plot_geometry(ink,x_seed+i*76,y_top,y_bottom)
                except ValueError as e:
                    raise ValueError(f'Page {page_no} {name}: {e}') from e
                axis = CHANGED[page_no] if name=='susceptibility' and page_no in CHANGED else AXES[site][i]
                tick_pts = measured_ticks(ink,top,lt,rt,axis)
                depth_bottom = round(z0+(bottom-top)/pitch,1) if page_no in SHORT else z0+150
                legend_page = min(n for n,values in PAGES.items() if values[0]==site)
                # The PDF encodes an RGB scan, but all three channels of each panel agree.
                rgbpix=page.get_pixmap(colorspace=fitz.csRGB,clip=fitz.Rect(min(lt,lb)+1,top+1,max(rt,rb)-1,bottom-1))
                rgb=np.frombuffer(rgbpix.samples,np.uint8).reshape(-1,3)
                channel_diff=int(np.ptp(rgb,axis=1).max())
                notes=[APPARATUS[page_no,name]] if (page_no,name) in APPARATUS else []
                if name=='susceptibility' and page_no in CHANGED: notes.append('Printed scale-change notice on this continuation.')
                if name=='reflectance' and page_no!=legend_page: notes.append('Three band labels and stroke samples come from the first page of this figure.')
                xmin,xmax,labels=axis
                scale,offset=np.polyfit(labels,tick_pts,1)
                empirical_min,empirical_max=(lt-offset)/scale,(rt-offset)/scale
                fit_error=max(abs(a-(scale*v+offset)) for a,v in zip(tick_pts,labels))
                if page_no==56 and name=='susceptibility':
                    xmin,xmax=round(empirical_min,2),round(empirical_max,2)
                    notes.append('Numbered ticks fit the physical frame at about -0.34 to 23.97. Endpoints are unlabelled.')
                output.append(dict(doc_id='PR',site=site,figure=f'PR.F{fig}',source_page=page_no,panel=name,
                    x0_pt=round(lt,2),y0_pt=round(top,2),x1_pt=round(rt,2),y1_pt=round(bottom,2),
                    x_min=xmin,x_max=xmax,x_ticks='|'.join(map(str,labels)),unit=UNITS[i],depth_top_m=z0,
                    depth_bottom_m=depth_bottom,ink='grayscale',spectral_band='blue|red|infrared' if name=='reflectance' else '',
                    status='print_tick_transcription_and_scan_frame_calibration',notes=' '.join(notes),
                    x_tick_pts='|'.join(f'{v:.2f}' for v in tick_pts),header_bottom_x0_pt=round(lt,2),
                    header_bottom_x1_pt=round(rt,2),floor_x0_pt=round(lb,2),floor_x1_pt=round(rb,2),
                    depth_axis='composite depth (mcd)',first_numbered_depth_m=z0+10,last_numbered_depth_m=last_depth,
                    depth_tick_pitch_pt_per_m=pitch,frame_depth_basis='unlabelled bottom inferred from measured 10 m tick spacing; approximately ±0.5 m' if page_no in SHORT else '150 m page interval checked against printed 10 m ticks',
                    frame_x_basis='linear continuation of numbered tick marks to frame boundaries; use x_tick_pts for original scan registration',
                    trace_blank_mcd=blank_ranges(ink,lt,rt,top,bottom,z0,depth_bottom),numeric_band_nm='',
                    legend_source_page=legend_page if name=='reflectance' else '',
                    printed_style='solid|dashed|dotted' if name=='reflectance' else 'solid',
                    rgb_max_channel_difference=channel_diff,source_pdf_sha256=digest,
                    x_frame_measured_min=round(empirical_min,4),x_frame_measured_max=round(empirical_max,4),
                    x_tick_fit_max_residual_pt=round(fit_error,3)))
    assert len(output)==66 and all(row['rgb_max_channel_difference']==0 for row in output)
    return output


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[4]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf',type=Path,default=root/'sppr/primary/PR.pdf')
    parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'data/panel_regions.csv')
    args=parser.parse_args()
    rows=calibrate(args.pdf)
    with args.out.open('w',encoding='utf8',newline='') as f:
        writer=csv.DictWriter(f,COLUMNS);writer.writeheader();writer.writerows(rows)
    print(f'{len(rows)} calibrated panels on {len(PAGES)} PDF pages')
