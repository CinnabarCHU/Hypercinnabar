"""Per-chapter PDF compositor. Each witness leaf is grafted without cropping or resampling."""
import io, re, textwrap
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import fitz
from structured_updates import value

SERIF='LegSerif';SANS='LegSans';BOLD='LegBold'
W,H=595.28,841.89
class Reader:
    def __init__(self,docid,title,fonts):
        for key,name in [(SERIF,'DejaVuSerif.ttf'),(SANS,'DejaVuSans.ttf'),(BOLD,'DejaVuSans-Bold.ttf')]:
            if key not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont(key,str(fonts/name)))
        self.buffer=io.BytesIO();self.cv=canvas.Canvas(self.buffer,pagesize=(W,H),pageCompression=1,invariant=1)
        self.cv.setTitle(docid+' · '+title);self.cv.setAuthor('Ocean Drilling Program / Leg 138 digital edition')
        self.docid=docid;self.title=title;self.num=0;self.y=0;self.source=0
    def label(self,x,y,txt,font,size,c='#1e3638'):
        self.cv.setFont(font,size);self.cv.setFillColor(HexColor(c));self.cv.drawString(x,y,str(txt))
    def header(self,source,folio,url,section='Reading text'):
        self.num+=1;self.source=source;self.folio=folio;self.url=url;self.section=section
        c=self.cv;c.setStrokeColor(HexColor('#73a39a'));c.setLineWidth(.9);c.line(48,800,W-48,800)
        self.label(48,781,'OCEAN DRILLING PROGRAM   /   LEG 138',BOLD,8.1,'#276760')
        self.label(48,757,self.docid+'   /   '+section,SERIF,16)
        self.label(48,740,f'Source PDF page {source}'+(f'   ·   printed folio {folio}' if folio else ''),SANS,8.6,'#59716f')
        self.y=713
    def end(self):
        self.cv.setStrokeColor(HexColor('#d1dfd9'));self.cv.line(48,43,W-48,43)
        self.label(48,29,'Source PDF online',SANS,8.0,'#28695f');self.cv.linkURL(self.url,(46,24,141,39),relative=0,thickness=0)
        self.label(197,29,'See source-page witness',SANS,8.0,'#28695f')
        self.label(W-88,29,str(self.num),SANS,8.0,'#637b74');self.cv.showPage()
    def renew(self):
        self.end();self.header(self.source,self.folio,self.url,self.section)
    def room(self,h):
        if self.y-h<60:self.renew()
    def line(self,txt,font,size,color):
        self.label(48,self.y,txt,font,size,color)
    def paragraph(self,txt,role='body'):
        if not txt:return
        style={'body':(SERIF,11.0,15.2,'#243335'),'heading':(BOLD,10.2,14.5,'#173f40'),
               'caption':(SANS,9.0,12.8,'#305752'),'notice':(SANS,8.6,12,'#536a65')}[role]
        font,size,lead,color=style
        lines=wrap(txt,font,size,W-96);self.room(lead*min(2,len(lines))+4)
        for line in lines:
            self.room(lead);self.line(line,font,size,color);self.y-=lead
        self.y-=6 if role=='body' else 4
    def table(self,asset,rows):
        cols=asset['display_columns'] or [c for c in rows[0] if c not in ('item_id','pdf_page','print_page')]
        cols=[c for c in cols if c in rows[0]]
        if not cols:raise ValueError(asset['item_id'])
        chunks=[cols[i:i+7] for i in range(0,len(cols),7)]
        for i,group in enumerate(chunks):
            self.paragraph(asset['item_id']+'  ·  '+asset['label']+(f'   [{i+1}/{len(chunks)}]' if len(chunks)>1 else ''),'heading')
            if asset.get('editorial_note'):self.paragraph(asset['editorial_note'],'notice')
            self.paragraph('Field values follow this editorial dataset. The Row column identifies its CSV data rows; full field names and provenance accompany the file.','notice')
            heads=['Row']+[c.replace('_',' ') for c in group]
            values=[[str(idx)]+[value(r,k) for k in group] for idx,r in enumerate(rows,1)]
            totals=[4]+[max(6,min(26,max(len(heads[j+1]),max((len(v[j+1]) for v in values),default=0)))) for j in range(len(group))]
            floors=[29]
            for j in range(len(group)):
                vals=[v[j+1] for v in values if v[j+1]]
                numeric=vals and all(re.fullmatch(r'[-+\d.,°′–/% ]+',v) for v in vals)
                floors.append(min(73,max(28,max(pdfmetrics.stringWidth(v,SANS,7.7)+7 for v in vals))) if numeric else 43)
            extra=W-96-sum(floors)
            widths=[floor+extra*weight/sum(totals) for floor,weight in zip(floors,totals)]
            def cells(fields,head=False):
                font=BOLD if head else SANS;size=7.3 if head else 7.7
                parts=[wrap(str(t),font,size,max(8,w-6)) or [''] for t,w in zip(fields,widths)]
                return parts,font,size,(max(map(len,parts))*10+4)
            def draw(row,head=False):
                parts,font,size,h=cells(row,head);x=48
                if head:self.cv.setFillColor(HexColor('#e6f0eb'));self.cv.rect(x,self.y-h+3,sum(widths),h,fill=1,stroke=0)
                for partscol,w in zip(parts,widths):
                    for j,txt in enumerate(partscol):self.label(x+3,self.y-6-j*10,txt,font,size,'#274c45' if head else '#253635')
                    x+=w
                self.y-=h;self.cv.setStrokeColor(HexColor('#d5e0d9'));self.cv.setLineWidth(.28);self.cv.line(48,self.y+3,W-48,self.y+3)
            self.room(cells(heads,True)[3]+20);draw(heads,True)
            for data in values:
                rh=cells(data)[3]
                if self.y-rh<59:self.renew();draw(heads,True)
                draw(data)
            self.y-=14
    def finish(self):
        self.cv.save();return self.buffer.getvalue()


def wrap(text,font,size,width):
    def w(t):return pdfmetrics.stringWidth(t,font,size)
    output=[];line=''
    for word in text.split():
        if w(word)>width:
            if line:output.append(line);line=''
            piece=''
            for ch in word:
                if piece and w(piece+ch)>width:output.append(piece);piece=''
                piece+=ch
            line=piece;continue
        proposal=line+' '+word if line else word
        if line and w(proposal)>width:output.append(line);line=word
        else:line=proposal
    if line:output.append(line)
    return output

def merge(reader_bytes,source,out,pages,assets_dir):
    textdoc=fitz.open(stream=reader_bytes,filetype='pdf');doc=fitz.open();toc=[];cache={}
    for r in pages:
        src=r['source_page'];r['edition_first']=len(doc)+1
        doc.insert_pdf(textdoc,from_page=r['reader_first']-1,to_page=r['reader_last']-1,final=0)
        r['edition_reading_last']=len(doc)
        for entry in r['graphics']:
            path=assets_dir/entry['file']
            if path not in cache:cache[path]=fitz.open(path)
            plot=cache[path];ap=entry['asset_page']-1
            doc.insert_pdf(plot,from_page=ap,to_page=ap,final=0)
        r['edition_witness']=len(doc)+1
        doc.insert_pdf(source,from_page=src-1,to_page=src-1,final=0)
        toc.extend([[1,f"Source PDF {src}"+(f" | print {r['printed_page']}" if r['printed_page'] else ''),r['edition_first']],
                    [2,'Reading text and structured evidence',r['edition_first']],
                    [2,'Original page witness',r['edition_witness']]])
        for j,e in enumerate(r['graphics'],1):
            toc.insert(-1,[2,e['item_id']+' | '+e['label'],r['edition_reading_last']+j])
    for r in pages:
        for idx in range(r['edition_first']-1,r['edition_reading_last']):
            page=doc[idx];page.insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(192,H-40,325,H-22),'page':r['edition_witness']-1,'to':fitz.Point(0,0)})
    doc.set_toc(toc);doc.set_metadata({'title':out.stem+' · ODP Leg 138 paired edition','author':'Ocean Drilling Program / Leg 138 digital edition','subject':'Reflowed reading text, associated data and original source-page witnesses'})
    doc.save(out,garbage=3,deflate=True,no_new_id=True)
    doc.close();textdoc.close()
    for p in cache.values():p.close()
