"""Replay the printed numeric cell extraction for the long tables using the publisher PDF.
Write every text-layer disagreement with the maintained reading and PDF rectangle.
PyMuPDF is only required for this optional editorial diagnostic.
"""
import argparse
import csv
from decimal import Decimal,InvalidOperation
import hashlib
import sqlite3
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]
CENTRES_27={607:[103,128,155,179,203,228,253,276,302,334,365,391,418,449,483,509],608:[128,152,177,205,230,255,280,302,329,361,392,418,445,476,510,536],609:[104,128,154,181,205,230,255,278,304,336,367,393,421,451,484,510]}
CENTRES_33={688:[204,236,264,289,312,337,360,384,408,436,460,483],689:[168,200,228,253,276,300,324,349,372,401,424,448],690:[204,237,266,290,313,338,362,386,410,439,462,485],691:[176,208,234,257,282,306,330,354,378,401,429,455],692:[199,230,260,284,308,332,356,380,404,427,457,481],693:[171,203,233,257,281,305,329,353,378,400,430,454]}
CENTRES_A={848:([86,122,156,186,210,230,248,272,293],259),849:([52,88,121,152,171,192,211,235,255],260),850:([83,119,150,180,202,223,243,266,286],261),851:([51,87,120,152,170,191,210,234,254],260),852:([83,119,150,178,202,223,242,266,286],261)}
CENTRES_B={853:[[55,84,112],[151,181,209],[248,276,305],[344,372,402],[441,470,499]],854:[[185,211,242],[279,306,337],[379,404,435]]}
def geometry(table,pg,panel):
    if table=="c27_t1_print":return CENTRES_27[pg],2.7,0
    if table.startswith("c33_"):return CENTRES_33[pg],3,0
    if table=="c43_appb_print":return CENTRES_B[pg][panel-1],3.35,0
    xs,shift=CENTRES_A[pg];return [x+shift*(panel-1) for x in xs],3.35,3
def equal(a,b):
    if not a or not b:return a==b
    try:return Decimal(a)==Decimal(b)
    except InvalidOperation:return False
def audit(sources,out):
    with sqlite3.connect(ROOT/'Site846_SR.sqlite') as db,out.open('w',newline='') as fp:
        db.row_factory=sqlite3.Row;writer=csv.writer(fp,lineterminator='\n')
        writer.writerow(['dataset','row_no','print_page','panel','print_row','field','pdf_left_pt','pdf_right_pt','pdf_y_pt','text_layer','edited_reading'])
        checked=0;diff=0
        for table in ['c27_t1_print','c33_app1_print','c33_app2_print','c43_appa_print','c43_appb_print']:
            meta=db.execute('SELECT source,sha256,page_from,pdf_page_from FROM datasets JOIN sources USING(source) JOIN items USING(item) WHERE dataset=?',(table,)).fetchone()
            data=(sources/meta['source']).read_bytes();assert hashlib.sha256(data).hexdigest()==meta['sha256']
            fields=[r[0] for r in db.execute('SELECT field FROM fields WHERE dataset=? ORDER BY position',(table,)) if r[0]!='sample']
            with fitz.open(stream=data,filetype='pdf') as doc:
                by_pg={}
                for row in db.execute('SELECT * FROM "'+table+'" ORDER BY row_no'):
                    pg=row['print_page'];panel=row['panel'];y=row['pdf_y_pt']
                    if pg not in by_pg:by_pg[pg]=sorted(doc[pg-meta['page_from']+meta['pdf_page_from']-1].get_text('words'),key=lambda w:w[0])
                    xs,tol,first=geometry(table,pg,panel);assert len(xs)==len(fields)
                    words=[w for w in by_pg[pg] if abs((w[1]+w[3])/2-y)<tol]
                    for j in range(first,len(xs)):
                        x=xs[j];left=(xs[j-1]+x)/2 if j else x-(17 if table=='c43_appb_print' else 15)
                        right=(x+xs[j+1])/2 if j+1<len(xs) else x+({'c27_t1_print':18,'c43_appa_print':11,'c43_appb_print':14}.get(table,15))
                        token=''.join(w[4] for w in words if left<=(w[0]+w[2])/2<right)
                        name=fields[j];checked+=1
                        if not equal(token,row[name]):
                            diff+=1;writer.writerow([table,row['row_no'],pg,panel,row['print_row'],name,left,right,y,token,row[name]])
    print(f'{checked} printed numeric positions; {diff} text-layer discrepancies written to {out}.')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args();audit(args.sources,args.out)
