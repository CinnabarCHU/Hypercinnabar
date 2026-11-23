"""Read physical OCR lines, infer a gutter from prose and order separate columns within vertical bands."""
import re
from collections import Counter
from statistics import median
import fitz

WORDS = re.compile(r"[^\W\d_]+", re.UNICODE)
CAPTION = re.compile(r'^\s*(?:fig(?:ure)?\.?|table|plate|appendix)\s*[A-Z]?\d+\b',re.I)


def prose(line):
    text=line['text']
    words=[w for w in WORDS.findall(text) if len(w)>1]
    return len(words)>=6 and sum(map(len,words))>0.49*len(text)


def find_gutter(lines,width):
    left=[];right=[]
    for line in lines:
        x0,_,x1,_=line['bbox']
        if not prose(line) or not .22*width < x1-x0 < .52*width:continue
        if x0 < .30*width and .36*width < x1 < .60*width:left.append(x1)
        if .40*width < x0 < .66*width and x1>.73*width:right.append(x0)
    if min(len(left),len(right))<3:return None
    edge_left=sorted(left)[int(.75*(len(left)-1))]
    edge_right=sorted(right)[int(.23*(len(right)-1))]
    gap=edge_right-edge_left
    if not 1.5 < gap < .12*width:return None
    return (edge_left+edge_right)/2


def kind(rows):
    text=' '.join(row['text'] for row in rows)
    words=WORDS.findall(text)
    if any(abs(row['direction'][1])>.1 for row in rows):return 'positioned'
    if CAPTION.match(text):return 'caption'
    if re.fullmatch(r'(?:\d+\.\s*)?SITE\s+\d{3}(?:\s*\d)?',text,re.I):
        return 'heading'
    # Shipboard reports have key: value lines, including dates, dimensions and small counts.
    if re.match(r'^[A-Za-z][A-Za-z /()\-.,]{2,66}:\s*\S+',text):
        return 'body'
    if len(text)<110 and 1<=len(words)<=16 and (text.isupper() or (len(rows)==1 and text.istitle())):
        if any(len(w)>2 for w in words) and len(re.findall(r'\d',text))<5 and len(text.strip())>=4:return 'heading'
    letters=sum(len(w) for w in words if len(w)>1)
    if any(prose(l) for l in rows) and letters>len(text)*.45:return 'body'
    if len(words)>=4 and len(text)>18 and letters>len(text)*.62:return 'body'
    return 'positioned'


def runs(source_page):
    lines=[]
    for block in source_page.get_text('dict',flags=fitz.TEXTFLAGS_TEXT)['blocks']:
        if block['type']!=0:continue
        for j,ln in enumerate(block['lines'],1):
            spans=[(s['text'],s['bbox']) for s in ln['spans']]
            raw=''.join(t for t,bbox in spans)
            if not raw.strip():continue
            lines.append(dict(block=block['number'],line=j,text=' '.join(raw.split()),raw=raw,
                              bbox=[round(v,2) for v in ln['bbox']],
                              direction=[round(v,4) for v in ln['dir']],spans=spans))
    seam=find_gutter(lines,source_page.rect.width)
    split=[]
    for row in lines:
        spans=row.pop('spans')
        groups=[spans]
        if seam is not None and row['direction'][0]>.9:
            for i in range(1,len(spans)):
                left,right=spans[i-1][1][2],spans[i][1][0]
                if left<=seam<=right and right-left>9:
                    groups=[spans[:i],spans[i:]];break
        for j,ss in enumerate(groups,1):
            seg=row.copy();seg['part']=j;seg['raw']=''.join(s[0] for s in ss);seg['text']=' '.join(seg['raw'].split())
            if len(groups)>1:
                seg['bbox']=[round(fn(s[1][axis] for s in ss),2) for axis,fn in enumerate((min,min,max,max))]
            if seg['text']:split.append(seg)
    packets=[];groups={}
    for row in split:
        x0,_,x1,_=row['bbox']
        lane='full' if seam is None or (x0<seam-3 and x1>seam+3) else ('left' if (x0+x1)/2<seam else 'right')
        key=(row['block'],lane)
        groups.setdefault(key,[]).append(row)
    for (block,lane),rows in groups.items():
        box=[fn(r['bbox'][axis] for r in rows) for axis,fn in enumerate((min,min,max,max))]
        pk=dict(block=block,lane=lane,role=kind(rows),bbox=box,lines=rows);packets.append(pk)
    # A full-width paragraph or caption divides a page. Labels inside figures never divide narrative columns.
    def xy(p):return (p['bbox'][1],p['bbox'][0],p['block'])
    if seam is None:
        ordered=sorted(packets,key=xy)
    else:
        dividers=sorted((p for p in packets if p['lane']=='full' and p['role']!='positioned'),key=xy)
        rest=[p for p in packets if not(p['lane']=='full' and p['role']!='positioned')]
        ordered=[]
        for div in dividers+[None]:
            end=div['bbox'][1] if div else float('inf')
            section=[p for p in rest if p['bbox'][1]<end]
            rest=[p for p in rest if p['bbox'][1]>=end]
            ordered+=sorted(section,key=lambda p:({'left':0,'right':1,'full':2}[p['lane']],*xy(p)))
            if div:ordered.append(div)
    assert len(split)==sum(len(g['lines']) for g in ordered)
    return seam,ordered


def reflow(packet):
    # Keep lexical hyphens. No dictionary guess and no silent correction of source OCR.
    return ' '.join(line['text'] for line in packet['lines'])
