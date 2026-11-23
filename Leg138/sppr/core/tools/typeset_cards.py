"""Build the 36-page station-planning section with new text setting and unchanged source plate imagery."""
from pathlib import Path
import argparse,csv,hashlib,io
from xml.sax.saxutils import escape
import fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
ROOT=Path(__file__).resolve().parents[1]
SP_SHA='7934144bec5ec839c5a95c113cec9a266ac2ad5ef4b97b50cd44ffad3d534e37'
SPURL='https://www-odp.tamu.edu/publications/prosp/digital/138prosp.pdf'
def fonts(folder):
    if folder is None:
        folder=next((p for p in [Path('/usr/share/fonts/truetype/liberation2'),Path('/usr/share/fonts/truetype/liberation')] if (p/'LiberationSerif-Regular.ttf').exists()),None)
    if folder is None:raise SystemExit('Specify --fonts, the directory containing the Liberation family TTF files.')
    for key,file in zip(['ReportText','ReportItalic','ReportHead','ReportSans','ReportSansBold'],['LiberationSerif-Regular','LiberationSerif-Italic','LiberationSerif-Bold','LiberationSans-Regular','LiberationSans-Bold']):
        pdfmetrics.registerFont(TTFont(key,str(folder/(file+'.ttf'))))
def banner(c,w,h,folio,title,kind):
    left=48
    c.setFillColorRGB(.21,.28,.30);c.setFont('ReportSans',9);c.drawString(left,h-31,'OCEAN DRILLING PROGRAM   /   LEG 138')
    c.drawRightString(w-left,h-31,'Eastern Equatorial Pacific   ·   Scientific Prospectus')
    c.setLineWidth(.5);c.setStrokeColorRGB(.61,.65,.66);c.line(left,h-40,w-left,h-40)
    c.setFillColorRGB(.06,.1,.12);c.setFont('ReportHead',26);c.drawString(left,h-77,title)
    c.setFont('ReportItalic',12);c.drawRightString(w-left,h-76,kind)
    c.setStrokeColorRGB(.69,.71,.7);c.line(left,38,w-left,38);c.setFillColorRGB(.23,.28,.30);c.setFont('ReportSans',8)
    c.drawString(left,26,folio)
def draw_paragraph(c,txt,x,top,w,font='ReportText',size=12,leading=15.8):
    style=ParagraphStyle('card',fontName=font,fontSize=size,leading=leading,textColor='#1b2426')
    par=Paragraph(escape(txt),style);_,height=par.wrap(w,765);par.drawOn(c,x,top-height);return top-height
def single_text(r,w,h):
    stream=io.BytesIO();c=canvas.Canvas(stream,pagesize=(w,h),invariant=1)
    n=int(r['pdf_page']);p=int(r['print_page'])
    banner(c,w,h,f'January 1991   ·   Printed p. {p}   ·   Source PDF p. {n}   ·   Scan-collated station card',r['proposed_site'],'Proposed drilling site')
    x=48;col=158;span=w-col-48;top=h-110
    records=[('Priority',r['priority']),('Position',r['position_printed']),('Water depth',r['water_depth_printed']),('Seismic record',r['seismic_record'])]
    records += [(label,r[colname]) for label,colname in [('Primary site','primary_site'),('Crossing','crossing'),('Secondary site','secondary_site')] if r[colname]]
    records += [('Sediment record',r['sediment_record']),('Sediment thickness',r['sediment_thickness_printed']),('Proposed drilling',r['proposed_drilling_program']),('Logging',r['logging'])]
    for label,txt in records:
        c.setFillColorRGB(.22,.27,.29);c.setFont('ReportSansBold',9.3);c.drawString(x,top-10.5,label)
        top=draw_paragraph(c,txt,col,top,span,size=12,leading=14.3)-8.2
    top-=3;c.setStrokeColorRGB(.70,.72,.72);c.line(x,top,w-48,top);top-=17
    c.setFont('ReportHead',15);c.setFillColorRGB(.1,.12,.13);c.drawString(x,top-12,'Objectives')
    top=draw_paragraph(c,r['objectives'],x,top-22,w-96)-14
    c.setFont('ReportSansBold',9.2);c.setFillColorRGB(.2,.24,.25);c.drawString(x,top-9,'Nature of sediment/rocks anticipated')
    top=draw_paragraph(c,r['anticipated_sediment_rocks'],x,top-15,w-96,size=12,leading=15)
    if top < 48:raise ValueError((r['proposed_site'],'Overflow',top))
    c.linkURL(SPURL+f'#page={n}',(x,18,w-48,38),relative=0,thickness=0)
    c.showPage();c.save();return fitz.open('pdf',stream.getvalue())
def single_plate(r,src,n,kind,w,h):
    stream=io.BytesIO();c=canvas.Canvas(stream,pagesize=(w,h),invariant=1)
    banner(c,w,h,f'January 1991   ·   Source PDF p. {n}   ·   Original map/profile imagery',r['proposed_site'],kind)
    c.linkURL(SPURL+f'#page={n}',(48,18,w-48,38),relative=0,thickness=0);c.showPage();c.save()
    image=fitz.open('pdf',stream.getvalue());p=image[0]
    # Preserve all plotted content and original scan resolution. The adopted viewport includes
    # the complete source leaf; the modern page provides publication and source locators.
    viewport=fitz.Rect(22,91,w-22,h-48);p.show_pdf_page(viewport,src,n-1,keep_proportion=True)
    return image
def create(primary,fontdir):
    fonts(fontdir)
    with (primary/'SP.pdf').open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==SP_SHA
    src=fitz.open(primary/'SP.pdf');output=fitz.open();bookmarks=[]
    with (ROOT/'data/sp_site_cards.csv').open() as f:
        for r in csv.DictReader(f):
            site=r['proposed_site'];n=int(r['pdf_page'])
            bookmarks.append([1,site,len(output)+1]);output.insert_pdf(single_text(r,612,792))
            for page,kind in [(n+1,'Site-survey map'),(n+2,'Survey profile')]:
                w,h=(792,612) if src[page-1].rect.width>src[page-1].rect.height else (612,792)
                bookmarks.append([2,kind,len(output)+1]);output.insert_pdf(single_plate(r,src,page,kind,w,h))
    output.set_toc(bookmarks);output.set_metadata(dict(title='ODP Leg 138 · Scientific Prospectus · Proposed drilling sites',subject='Modern station cards and original survey plates',author='Ocean Drilling Program (source); editorial digital collation'))
    assert len(output)==36
    dest=ROOT/'publication'/'Leg138_SP_Proposed_Sites.pdf';dest.parent.mkdir(exist_ok=True);output.save(dest,garbage=4,deflate=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path);p.add_argument('--fonts',type=Path);a=p.parse_args();create(a.primary,a.fonts)
