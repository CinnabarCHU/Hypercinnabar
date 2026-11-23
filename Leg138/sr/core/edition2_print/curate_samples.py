"""Write the independent manual numerical readings from Chapter 4 Table 2 with print coordinates."""
import argparse,csv,hashlib,json
from pathlib import Path
import fitz
from build import writecsv
TABLE=[
("846","−2.91","0.14","0.81","0.02","0.89"),
("847","−2.86","0.16","0.82","0.03","0.84"),
("849","−1.74","0.21","0.55","0.04","0.54"),
("850","−2.52","0.12","0.68","0.02","0.88"),
("851","−1.81","0.15","0.54","0.03","0.72"),
("Average of all sites","−2.37","0.08","0.68","0.01","0.73"),
("Average of 846, 847, 850","−2.76","0.09","0.77","0.02","0.85")]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('core',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    rel='official/VOLUME/CHAPTERS/sr138_04.pdf';f=a.core.parent/'primary'/rel;doc=fitz.open(f);pg=doc[7]
    native=[]
    # Row centers selected in the page image, then verify unique depth/slope tokens via word boxes.
    words=pg.get_text('words',clip=fitz.Rect(73,392,282,465))
    rowcenters=[]
    for r in TABLE[:5]:
        w,=[w for w in words if w[4]==r[0] and w[0]<125];rowcenters.append((w[1]+w[3])/2)
    rowcenters.extend([(w[1]+w[3])/2 for w in words if w[4]=='Average'])
    assert len(rowcenters)==7
    for n,(row,y) in enumerate(zip(TABLE,rowcenters),1):
        selected=[w for w in words if abs((w[1]+w[3])/2-y)<3.6]
        bb=[round(min(w[0] for w in selected),2),round(min(w[1] for w in selected),2),round(max(w[2] for w in selected),2),round(max(w[3] for w in selected),2)]
        native.append(dict(item_id='SR.C04.TABLE2',source=rel,pdf_page=8,print_page=54,row=n,row_bbox_pt=json.dumps(bb),site_or_summary_printed=row[0],slope=row[1],slope_plusminus=row[2],y_intercept=row[3],y_intercept_plusminus=row[4],correlation=row[5],status='visually_read_and_field_mapped'))
    writecsv(a.output/'verified_c04_table2.csv',native[0].keys(),native)
    pg.get_pixmap(clip=fitz.Rect(64,345,289,466),matrix=fitz.Matrix(2.4,2.4)).save(a.output/'verified_c04_table2.png')
if __name__=='__main__':main()
