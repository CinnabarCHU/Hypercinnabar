"""Trace the 22 sparse printed marks in the continuation of Chapter 12 Table 14."""
from pathlib import Path
import json
import fitz
import numpy as np
from scipy import ndimage as nd
# The letters were read in the publisher scan, corresponding to component order by top and left.
LETTERS=['R','R','R','F','R','F','F','F','F','F','F','F','R','C','F','F','R','C','F','R','R','R']
HEADERS=['Thoracosphaera','T. milowi','T. serratus','Umbilicosphaera spp']
def read(pdf):
    p=fitz.open(pdf)[28]
    px=p.get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(40,88,241,705),colorspace=fitz.csGRAY)
    im=np.frombuffer(px.samples,np.uint8).reshape(px.height,px.width)
    cc,count=nd.label(nd.maximum_filter(im<178,size=(3,3)))
    boxes=[]
    for yy,xx in nd.find_objects(cc):
        width=(xx.stop-xx.start)/3;height=(yy.stop-yy.start)/3
        if 1.9<width<10 and 3.5<height<11:
            boxes.append([(px.x+xx.start)/3,(px.y+yy.start)/3,(px.x+xx.stop)/3,(px.y+yy.stop)/3])
    assert len(boxes)==len(LETTERS)
    marks=[(*bb,letter) for bb,letter in zip(boxes,LETTERS)]
    return marks
def main():
    import argparse,csv
    parser=argparse.ArgumentParser();parser.add_argument('core',type=Path);parser.add_argument('output',type=Path);a=parser.parse_args()
    file='official/VOLUME/CHAPTERS/sr138_12.pdf';doc=a.core.parent/'primary'/file;marks=read(doc)
    with (a.output/'verified_c12_table14_p29_marks.csv').open('w',newline='') as out:
        w=csv.writer(out,lineterminator='\n');w.writerow(['item_id','source','pdf_page','print_page','visible_mark_index','printed_column','printed_mark','bbox_pt','sample_assignment'])
        for j,m in enumerate(marks,1):
            k=int(np.searchsorted([89,133,176],(m[0]+m[2])/2));w.writerow(['SR.C12.TABLE14',file,29,261,j,HEADERS[k],m[4],json.dumps([round(x,2) for x in m[:4]]),'unassigned_lateral_continuation'])
    pg=fitz.open(doc)[28];pg.get_pixmap(matrix=fitz.Matrix(1.8,1.8),clip=fitz.Rect(40,64,241,710)).save(a.output/'verified_c12_table14_p29.png')
if __name__=='__main__':main()
