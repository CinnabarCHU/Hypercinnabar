"""Locate the rotated Tables 1 from a clockwise scan rendering, then check the original region visually."""
from pathlib import Path
import fitz,subprocess,io,os,csv,re,concurrent.futures
E=Path(__file__).resolve().parents[1];P=E.parent.parent/'primary'
def search(q):
    ch,page=q
    pg=fitz.open(P/f'official/VOLUME/CHAPTERS/sr138_{ch}.pdf')[page-1]
    with_img=pg.get_pixmap(matrix=fitz.Matrix(2,2).prerotate(90),colorspace=fitz.csGRAY)
    out=subprocess.run(['tesseract','stdin','stdout','--psm','6','tsv'],input=with_img.tobytes('png'),capture_output=True,env=dict(os.environ,OMP_THREAD_LIMIT='1')).stdout.decode()
    groups={}
    for row in csv.DictReader(io.StringIO(out),delimiter='\t'):
        if row['level']=='5':groups.setdefault((row['block_num'],row['par_num'],row['line_num']),[]).append(row)
    for rows in groups.values():
        for j,r in enumerate(rows):
            if 'Table' in r['text'] and j+1<len(rows) and re.match('^[1Il][.,]',rows[j+1]['text']):
                # Use the sequence containing Table 1. For the snippet, offset from its first word.
                x=float(r['left'])/2;y=float(r['top'])/2;h=float(r['height'])/2
                original=(round(y-3,1),round(pg.rect.height-x-180,1),round(y+h+3,1),round(pg.rect.height-x+3,1))
                print(q,' '.join(r['text'] for r in rows[j:j+9]),original,flush=True)
                return
    print(q,'no match',flush=True)
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(3) as pool:list(pool.map(search,[(31,5),(37,2),(41,2)]))
