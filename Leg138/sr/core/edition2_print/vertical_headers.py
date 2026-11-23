"""Independent readings of vertical species headings, kept separate from the visible PDF words."""
import argparse,csv,gzip,io,json,os,re,subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import fitz
from PIL import Image
def process(args):
    core,r=args;source=r['source'];page=int(r['pdf_page']);segment=r['segment']
    pg=fitz.open(core.parent/'primary'/source)[page-1];q=json.loads(r['header_bbox_pt'])
    if not q or int(r['reading_orientation_deg'])!=0:return []
    rect=fitz.Rect(*q);records=[]
    blocks=pg.get_text('dict',clip=rect,flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks']
    for block in blocks:
        for line in block.get('lines',[]):
            dx,dy=line['dir']
            if abs(dy)>.85:
                text=''.join(s['text'] for s in line['spans']).strip()
                if text:records.append([segment,r['item_id'],source,page,'publisher_pdf_vertical_line',-90 if dy<0 else 90,text,'',json.dumps([round(v,2) for v in line['bbox']])])
    # The raster review established these matrices have species names printed bottom to top.
    chapter=int(r['chapter']);num=r['item_id'].split('TABLE')[-1]
    matrix=(chapter==8 and num in {'3','4','5','6','7','8','9','10'} or chapter==12 and num in {'13','14','15','16'} or chapter==46 and num in {'2','3','4','5','6'})
    if not matrix or rect.height<43:return records
    zoom=2.8
    pix=pg.get_pixmap(matrix=fitz.Matrix(zoom,zoom),clip=rect,colorspace=fitz.csGRAY)
    im=Image.frombytes('L',(pix.width,pix.height),pix.samples).transpose(Image.Transpose.ROTATE_270)
    buf=io.BytesIO();im.save(buf,'PNG')
    env={**os.environ,'OMP_THREAD_LIMIT':'1'}
    sd=subprocess.run(['tesseract','stdin','stdout','--psm','11','tsv'],env=env,input=buf.getvalue(),stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=True)
    mapped=defaultdict(list)
    for v in csv.DictReader(io.StringIO(sd.stdout.decode(errors='replace')),delimiter='\t'):
        if v.get('level')!='5' or not v['text'].strip():continue
        x,y,w,h=(float(v[k]) for k in ['left','top','width','height'])
        bb=[(pix.x+y)/zoom,(pix.y+pix.height-x-w)/zoom,(pix.x+y+h)/zoom,(pix.y+pix.height-x)/zoom]
        mapped[(v['block_num'],v['par_num'],v['line_num'])].append((v['text'],float(v['conf']),bb))
    for words in mapped.values():
        text=' '.join(v[0] for v in words)
        if not re.search(r'[A-Za-z]{2,}',text):continue
        bb=[min(v[2][0] for v in words),min(v[2][1] for v in words),max(v[2][2] for v in words),max(v[2][3] for v in words)]
        records.append([segment,r['item_id'],source,page,'rotated_scan_Tesseract_candidate',-90,text,round(sum(v[1] for v in words)/len(words),1),json.dumps([round(v,2) for v in bb])])
    return records
def main():
    p=argparse.ArgumentParser();p.add_argument('core',type=Path);p.add_argument('output',type=Path);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    with (a.output/'segments.csv').open() as f:rr=list(csv.DictReader(f))
    with gzip.GzipFile(filename=str(a.output/'vertical_header_candidates.csv.gz'),mode='wb',mtime=0) as gz,io.TextIOWrapper(gz,encoding='utf8',newline='') as out,ThreadPoolExecutor(max_workers=a.workers) as pool:
        w=csv.writer(out,lineterminator='\n')
        w.writerow(['segment','item_id','source','pdf_page','reading_source','native_baseline_deg','text_candidate','mean_ocr_confidence','bbox_pt'])
        for rows in pool.map(process,[(a.core,r) for r in rr]):w.writerows(rows)
if __name__=='__main__':main()
