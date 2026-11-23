"""Render the selected published table row at its anchored print location. Requires PyMuPDF."""
import argparse
import hashlib
import sqlite3
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]
TABLE_BOXES={
 'c15_t2_print':(301,43,538,153),'c15_t4_print':(306,560,547,743),'c15_t8_print':(134,402,548,620),
 'c27_t2_print':(320,42,575,158),'c33_t1_print':(271,425,571,578),'c33_t2_print':(94,47,563,289),
 'c33_t3_print':(274,450,570,707)}
def crop(key,number,sources,target,db=ROOT/'Site846_SR.sqlite'):
 with sqlite3.connect(db) as conn:
  conn.row_factory=sqlite3.Row
  m=conn.execute("SELECT d.source,d.edition,i.page_from,i.pdf_page_from,s.sha256 FROM datasets d JOIN items i USING(item) JOIN sources s ON d.source=s.source WHERE d.dataset=?",(key,)).fetchone()
  if not m or m['edition']!='print':raise ValueError("Choose a dataset ending in _print")
  row=conn.execute('SELECT * FROM "'+key+'" WHERE row_no=?',(number,)).fetchone()
  if row is None:raise ValueError("Row number outside table")
 raw=(sources/m['source']).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=m['sha256']:raise ValueError("Unexpected source hash")
 with fitz.open(stream=raw,filetype='pdf') as doc:
  page_number=row['print_page']-m['page_from']+m['pdf_page_from'];pg=doc[page_number-1]; y=row['pdf_y_pt']
  if y is None:rect=fitz.Rect(TABLE_BOXES[key])
  else:
   x0,x1=20,pg.rect.width-17;printed=row['print_page'];panel=row['panel']
   if key=='c43_appa_print':
    cut=318 if printed in (848,850,852) else 284
    x0,x1=(x0,cut) if panel==1 else (cut,x1)
   if key=='c43_appb_print':
    bounds=([34,132,229,326,424,520] if printed==853 else [161,262,359,454]);x0,x1=bounds[panel-1:panel+1]
   rect=fitz.Rect(x0,y-4.4,x1,y+4.4)
  pg.get_pixmap(matrix=fitz.Matrix(3.5,3.5),clip=rect,alpha=False).save(target)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('dataset');p.add_argument('row',type=int);p.add_argument('--sources',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();crop(a.dataset,a.row,a.sources,a.out)
