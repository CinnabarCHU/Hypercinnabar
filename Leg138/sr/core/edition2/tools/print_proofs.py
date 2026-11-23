"""Re-render the compact verified printed-table witnesses in original coordinates."""
from pathlib import Path
import csv
import fitz
E=Path(__file__).resolve().parents[1];P=E.parent.parent/'primary'
boxes={'SR.C01.TABLE1':[48,47,300,250], 'SR.C03.TABLE3':[49,365,303,481], 'SR.C03.TABLE4':[292,536,538,657], 'SR.C03.TABLE6':[18,44,283,419],
       'SR.C04.TABLE1':[323,284,508,427], 'SR.C36.TABLE1':[344,41,547,184], 'SR.C41.TABLE3':[50,224,251,427]}
if __name__=='__main__':
    with (E/'data/print_datasets.csv').open() as f:datasets=list(csv.DictReader(f))
    with (E/'data/print_proofs.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['dataset_id','source','pdf_page','bbox_pt','witness_png'])
        for q in datasets:
            key=q['item_id'];bbox=boxes[key];filename=f'print/{key}_scan.png'
            with fitz.open(P/q['source']) as doc:
                pg=doc[int(q['pdf_page'])-1];pg.get_pixmap(matrix=fitz.Matrix(2.25,2.25),colorspace=fitz.csGRAY,clip=fitz.Rect(bbox)).save(E/filename)
            w.writerow([q['dataset_id'],q['source'],q['pdf_page'],str(bbox),filename])
