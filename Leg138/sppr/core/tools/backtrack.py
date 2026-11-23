"""Rebuild approximate coordinates digitized from PR Fig. 15 and inspect them against the original scan."""
from pathlib import Path
import argparse,csv,json,hashlib,math
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
PDF_HASH='48f7d7e22f672f499c38d610d995ad713874cfd01bc29516cf6b2f4cbe6d18c5'
SOURCE='https://www-odp.tamu.edu/publications/prelim/138PREL.PDF#page=50'
# Coordinates in original PDF points, measured against a fourfold raster.
# Ages 1–9 label the small tick across the trajectory. The present location is the dot centre.
TRACK=[(0,252.75,394.75),(1,273.50,401.50),(2,291.75,408.25),(3,310.25,414.25),
       (4,329.75,420.25),(5,348.25,425.50),(6,366.75,431.50),(7,386.50,436.75),
       (8,404.75,441.75),(9,423.00,447.50)]
XTICKS=[(128.00,-115),(251.75,-110),(375.00,-105),(498.50,-100)]
YTICKS=[(454.25,0),(331.75,5)]
def dump(name,rows):
    with (DATA/name).open('w',newline='') as f:
        out=csv.DictWriter(f,fieldnames=list(rows[0]));out.writeheader();out.writerows(rows)
def line(anchors):
    mx=sum(x for x,_ in anchors)/len(anchors); my=sum(y for _,y in anchors)/len(anchors)
    slope=sum((x-mx)*(y-my) for x,y in anchors)/sum((x-mx)**2 for x,y in anchors)
    return lambda x:my+slope*(x-mx)
def great_circle(lat,lon,a,b):
    lat,lon,a,b=map(math.radians,[lat,lon,a,b])
    return 12742.0176*math.asin(math.sqrt(math.sin((lat-a)/2)**2+math.cos(lat)*math.cos(a)*math.sin((lon-b)/2)**2))
def generate(primary):
    import fitz
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from PIL import Image
    pdf=primary/'PR.pdf'
    with pdf.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==PDF_HASH
    f=fitz.open(pdf);page=f[49]
    cal=[dict(item_id='PR.F15',pdf_page=50,axis=ax,tick_value_deg=v,coordinate_pt=p) for ax,ticks in [('longitude',XTICKS),('latitude',YTICKS)] for p,v in ticks]
    dump('pr_fig15_axis_ticks.csv',cal)
    lat,lon=line(YTICKS),line(XTICKS)
    reading=[dict(item_id='PR.F15',site='851',age_ma=k,age_label='modern station symbol' if k==0 else 'labelled age tick',x_pdf_pt=x,y_pdf_pt=y,longitude_deg_approx=f'{lon(x):.2f}',latitude_deg_approx=f'{lat(y):.2f}',value_status='editorial_graphic_reading',pdf_page=50,print_page=52,source_url=SOURCE) for k,x,y in TRACK]
    dump('pr_fig15_backtrack.csv',reading)
    with (DATA/'site_holes.csv').open() as inp:
        ref=next(r for r in csv.DictReader(inp) if r['hole']=='851A')
    diff=great_circle(lat(TRACK[0][2]),lon(TRACK[0][1]),float(ref['latitude_deg']),float(ref['longitude_deg']))
    (DATA/'pr_fig15_check.json').write_text(json.dumps(dict(item_id='PR.F15',scope='one illustrated track, Site 851',positions=len(reading),printed_age_labels=9,zero_label='present-day symbol',table_reference_hole=ref['hole'],table_latitude=ref['latitude_printed'],table_longitude=ref['longitude_printed'],distance_from_drawn_modern_symbol_km=round(diff,1),calibration='longitude OLS on four printed ticks; latitude linear between printed 0 and 5 N',graphic_reference='PDF points from top left; no plate model or reference-frame transformation'),indent=2)+'\n')
    fig=plt.figure(figsize=(10.5,6.5))
    fig.text(.028,.95,'Site 851: published backtrack',weight='bold',size=17)
    fig.text(.028,.91,'Leg 138 Preliminary Report  |  Figure 15  |  printed p. 52 / PDF p. 50',size=9.5)
    box=fitz.Rect(77,148,515,593)
    pix=page.get_pixmap(matrix=fitz.Matrix(1.7,1.7),clip=box,colorspace=fitz.csGRAY)
    im=Image.frombytes('L',(pix.width,pix.height),pix.samples)
    ax=fig.add_axes([.02,.094,.60,.793]);ax.imshow(im,cmap='gray',vmin=0,vmax=255,extent=(box.x0,box.x1,box.y1,box.y0))
    ax.plot([p[1] for p in TRACK],[p[2] for p in TRACK],linestyle='none',marker='o',mfc='none',mec='#a22d14',mew=1,ms=5.5)
    ax.axis('off')
    ax=fig.add_axes([.66,.082,.306,.792]);ax.axis('off')
    ax.text(0,1,'Graphic readings',weight='bold',size=13,va='top')
    ax.text(0,.915,'Age (Ma)       Latitude        Longitude',size=10,weight='bold',family='Liberation Mono')
    for i,r in enumerate(reading):
        ax.text(0,.861-i*.053,f"{r['age_ma']:8d}       {float(r['latitude_deg_approx']):5.2f}°N       {abs(float(r['longitude_deg_approx'])):6.2f}°W",size=9.2,family='Liberation Mono')
    ax.text(0,.288,f"At the present-day symbol, the map reading is\nabout {diff:.0f} km from the published Hole 851A\ncoordinates. The graphic positions are kept\nseparately from the drilling coordinates.",fontsize=9,linespacing=1.38,va='top')
    ax.text(0,.120,"The map marks Sites 848–854. Its caption's\nfirst sentence prints “Sites 881”; the map\nlabels the illustrated track Site 851.",fontsize=8.5,linespacing=1.38,va='top')
    fig.text(.03,.034,'Circles locate the source markers. The table is an editorial reading of the printed map. A geodynamic rotation model was not used.',size=8.4)
    (ROOT/'figures').mkdir(exist_ok=True)
    fig.savefig(ROOT/'figures'/'pr_fig15_graphic_check.pdf',metadata={'CreationDate':None});plt.close(fig)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('primary',type=Path)
    generate(parser.parse_args().primary)
