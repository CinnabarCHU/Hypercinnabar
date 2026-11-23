"""Select candidate caption lines and render a compact review atlas directly from the original pixels."""
from pathlib import Path
import csv,json,gzip,re,collections,math,sys,concurrent.futures
from PIL import Image,ImageFont,ImageDraw
import fitz
E=Path(__file__).resolve().parents[1];C=E.parent;P=C.parent/'primary'
def read(name):return list(csv.DictReader((C/name).open()))
def events(file):return list(map(json.loads,gzip.open(E/'data'/file,'rt')))
def score(x):
    text=x['text']; label=re.match(r'^\s*(?:Figure|Fig\.?|Table|Plate)\s*[.]?\s*[\dIl]+[a-d]?\s*[.,:;)]?\s*',text,re.I)
    after=text[label.end():] if label else text
    s=(3 if x.get('separator') in ('.',':','(continued)') else -4)+(2 if re.match(r'[A-Z0-9Α-Ω]',after) else 0)
    s+=max(-2,min(2,9-x['font_pt']))+('Bold' in x['font'])*1.0
    if 'continued' in text.lower() or '(cont' in after.lower():s-=3
    if not after:s-=4
    if re.match(r'(We |Although |In |The |This |These )',after) and x['font_pt']>8.1:s-=2
    if text.startswith(('fig.','table ','figure ','plate ')):s-=5
    return s
def choose():
    cand=collections.defaultdict(list)
    for x in events('candidate_lines.jsonl.gz'):cand[x['item_id']].append(x)
    apps=collections.defaultdict(list)
    for x in events('appendix_headings.jsonl.gz'):apps[x['id']].append(x)
    existing={x['item_id']:x for x in read('items.csv')}
    # The late-detected Appendix F has a separate original-pixel proof in the supplement.
    keys=list(existing)+sorted(set(apps)-set(existing)-{'SR.C17.APPENDIXF'})
    selected=[]
    for key in keys:
        old=existing.get(key);ch=int(key[4:6]);n=key.split('.')[-1]
        v=cand.get(key)
        if key in apps:
            xs=apps[key]
            candidate=next((a for a in xs if a['text'].isupper()),xs[-1]);basis='appendix_line'
        elif v:
            candidate=max(v,key=score);basis='numbered_line'
        else:
            candidate=None;basis='prior_location_only'
        if candidate:
            record=dict(candidate)
            record['basis']=basis
        else:
            record=dict(chapter=ch,source=old['source'],pdf_page=int(old['pdf_page']),print_page=old['print_page'],bbox=None,direction=[1,0],text=old['label'],basis=basis,font='',font_pt='')
        record['item_id']=key
        record['previous_status']=old['status'] if old else 'new'
        # Rotated headings and the publisher's foldout lack usable horizontal line text.
        if key=='SR.C21.FIGURE17':
            record.update(source=old['source'],pdf_page=1,print_page='',bbox=None,basis='published_foldout')
        selected.append(record)
    def ordering(x):
        key=x['item_id'].split('.')[-1];m=re.fullmatch(r'(FIGURE|TABLE|PLATE|APPENDIX)(\d*)([A-Z]*)',key)
        return int(x['chapter']),['FIGURE','TABLE','PLATE','APPENDIX'].index(m[1]),int(m[2] or 0),m[3]
    return sorted(selected,key=ordering)
def collect(chrows):
    docs={};cache={};result=[]
    for r in chrows:
        s=r['source'];num=int(r['pdf_page'])
        if s not in docs:docs[s]=fitz.open(P/s)
        pg=docs[s][num-1];bbox=r['bbox'];key=r['item_id']
        if bbox:
            x,y,x2,y2=bbox
            box=fitz.Rect(x-2,y-2,min(x+145,pg.rect.width),min(y2+2,pg.rect.height))
            dir=r['direction'];rotation=90 if dir[1]<-.6 else -90 if dir[1]>.6 else 0
            if rotation:
                box=fitz.Rect(x-2,max(0,y2-145),x2+2,y2+2)
        else:
            box=rotation=None
        if box is not None:
            # Render once per leaf for multiple snippets.
            cachekey=(s,num)
            if cachekey not in cache:
                pix=pg.get_pixmap(matrix=fitz.Matrix(2,2),colorspace=fitz.csGRAY)
                im=Image.frombytes('L',(pix.width,pix.height),pix.samples)
                cache={cachekey:im}
            im=cache[cachekey].crop(tuple(int(k*2) for k in box)).rotate(-rotation,expand=True)
        else:
            im=Image.new('L',(287,28),'white')
            ImageDraw.Draw(im).text((2,4),'[separate original-page review]',fill='black')
        im.thumbnail((299,38));result.append((r,im))
    for doc in docs.values():doc.close()
    return result
def run():
    selected=choose();by=collections.defaultdict(list)
    for r in selected:by[int(r['chapter'])].append(r)
    with concurrent.futures.ThreadPoolExecutor(5) as pool:
        rendered=[pair for batch in pool.map(collect,by.values()) for pair in batch]
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',10)
    for start in range(0,len(rendered),48):
        n=min(48,len(rendered)-start);sheet=start//48+1
        canvas=Image.new('L',(842,30+40*math.ceil(n/2)),'white');draw=ImageDraw.Draw(canvas)
        draw.text((4,6),f'SR original print evidence | {sheet:02d} | chapter / object / physical PDF page',font=font,fill='black')
        for j,(r,im) in enumerate(rendered[start:start+n]):
            x=j%2*421;y=25+j//2*40;k=r['item_id'].replace('SR.C','').replace('FIGURE',' F').replace('TABLE',' T').replace('PLATE',' P').replace('APPENDIX',' App')
            draw.text((x+3,y+7),f"{k} p{r['pdf_page']}",font=font,fill='black');canvas.paste(im,(x+113,y+(36-im.height)//2));draw.line((x,y+38,x+420,y+38),fill=221)
            r['sheet']=sheet;r['cell']=j+1
        canvas.save(E/'atlas'/f'sheet{sheet:02d}.png',optimize=True)
    with (E/'data/selected_lines.jsonl.gz').open('wb') as f,gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:
        for r,_ in rendered:z.write((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode())
    print('selected',len(selected),'sheets',math.ceil(len(selected)/48))
if __name__=='__main__':run()
