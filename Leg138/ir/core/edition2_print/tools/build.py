"""Construct source-anchored named cells from each specified print table and record optical disagreements."""
from bisect import bisect_right
from collections import Counter,defaultdict
from pathlib import Path
from statistics import median
import argparse,csv,gzip,hashlib,json,re,unicodedata
import fitz,numpy as np
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'

def load(path,delimiter=','):
    with (gzip.open(path,'rt',newline='') if path.suffix=='.gz' else path.open(newline='')) as src:
        return list(csv.DictReader(src,delimiter=delimiter))
def save(path,rows):
    with (gzip.open(path,'wt',newline='') if path.suffix=='.gz' else path.open('w',newline='')) as out:
        w=csv.DictWriter(out,rows[0].keys());w.writeheader();w.writerows(rows)
def norm(s):
    s=unicodedata.normalize('NFKC',s).replace('–','-').replace('—','-').replace('−','-')
    return ''.join(s.split()).casefold()
def middle(w):return (w[1]+w[3])/2
def display(words):return ' '.join(w[4] for w in sorted(words,key=lambda z:z[0]))
def bounds(words):
    if not words:return ''
    return fmt([min(w[0] for w in words),min(w[1] for w in words),max(w[2] for w in words),max(w[3] for w in words)])
def fmt(coords):return ','.join(f'{v:.2f}' for v in coords)
def group(tokens,eps):
    groups=[]
    for z in sorted(tokens,key=middle):
        if not groups or middle(z)-median(map(middle,groups[-1]))>eps:groups.append([])
        groups[-1].append(z)
    return groups

def run(ir):
    layouts=load(DATA/'layouts.psv','|')
    items={r['item_id']:r for r in load(ROOT.parent/'chapter_items.csv')}
    locs={(r['item_id'],r['pdf_page']):r for r in load(ROOT.parent/'chapter_item_locations.csv')}
    scan=defaultdict(list)
    for r in load(DATA/'optical_tokens.csv.gz'):
        scan[r['item_id'],r['pdf_page']].append(tuple(float(r[k]) for k in ('x0','y0','x1','y1'))+(r['text'],float(r['confidence'])))
    manuals={}
    if (DATA/'manual_readings.csv').exists():
        for r in load(DATA/'manual_readings.csv'):
            manuals[(r['item_id'],r['pdf_page'],r['field'],float(r['row_y_pt']))]=r
    centres=defaultdict(list)
    for ctr in load(DATA/'specified_row_centers.csv'):
        centres[ctr['item_id'],ctr['pdf_page']].append(float(ctr['row_y_pt']))
    rows=[];cells=[];datasets=[];regions=[]
    docs={};hashes={};index=defaultdict(int);st=defaultdict(Counter)
    for spec in layouts:
        item,pg=spec['item_id'],spec['pdf_page']
        ref=items[item];loc=locs[(item,pg)];path=ir/ref['pdf_path']
        if path not in docs:docs[path]=fitz.open(path);hashes[path]=hashlib.sha256(path.read_bytes()).hexdigest()
        page=docs[path][int(pg)-1];l,h,t,b,r=[float(spec[k]) for k in ('x0','header_y','data_y','end_y','x1')]
        cut=[float(q) for q in spec['cuts'].split(',')];fields=spec['fields'].split(',');edges=[l,*cut,r]
        assert len(fields)==len(edges)-1 and all(x<y for x,y in zip(edges,edges[1:])),spec
        source=[w for w in page.get_text('words') if l<=(w[0]+w[2])/2<=r and h<=middle(w)<=b]
        plat=[w for w in source if middle(w)>=t]
        texhead=group([w for w in source if middle(w)<t],2.6)
        # The image reader is calibrated against matching tokens, independently for each rectangle.
        opt=[w for w in scan[(item,pg)] if t+.2<middle(w)<b-.1 and w[5]>=12 and norm(w[4]) not in ['|','_']]
        offsets=[]
        for w in opt:
            matches=[middle(v)-middle(w) for v in plat if norm(v[4])==norm(w[4]) and abs((v[0]+v[2]-w[0]-w[2])/2)<3 and abs(middle(w)-middle(v))<2.8]
            if len(matches)==1:offsets+=matches
        offset=median(offsets) if offsets else .6
        source_rows=group(plat,2.6); rr=[{'y':median(map(middle,v)),'p':v,'o':[]} for v in source_rows]
        if (item,pg) in centres:
            rr=[{'y':v,'p':[],'o':[]} for v in centres[(item,pg)]]
            for w in plat:min(rr,key=lambda a:abs(a['y']-middle(w)))['p'].append(w)
        extra=[]
        for w in opt:
            y=middle(w)+offset;nearest=min(rr,key=lambda z:abs(z['y']-y)) if rr else None
            if nearest is not None and abs(y-nearest['y'])<4.15:nearest['o'].append(w)
            else:extra.append(w)
        for words in group(extra,2.3):
            if not any(w[5]>=40 and re.search(r'[a-zA-Z0-9]',w[4]) for w in words):continue
            y=median(map(middle,words))+offset
            if t<y<b:rr.append({'y':y,'p':[],'o':words})
        rr.sort(key=lambda z:z['y'])
        pix=page.get_pixmap(matrix=fitz.Matrix(3,3),colorspace=fitz.csGRAY,clip=fitz.Rect(l,t,r,b))
        dark=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width)<145
        anchor=list(map(float,loc['caption_bbox_xyxy_pt'].split(',')))
        caption_lines=[]
        for block in page.get_text('dict',flags=fitz.TEXTFLAGS_TEXT)['blocks']:
            for line in block.get('lines',[]):
                x,y=line['bbox'][:2]
                if anchor[1]-1<=y<=h-1 and abs(x-anchor[0])<4:
                    caption_lines.append((y,''.join(span['text'] for span in line['spans'])))
        caption=' '.join(z[1] for z in sorted(caption_lines))
        regions.append(dict(item_id=item,pdf_page=pg,printed_page=loc['printed_page'],pdf_path=ref['pdf_path'],
                    sha256=hashes[path],caption_anchor=loc['caption_bbox_xyxy_pt'],header_bbox=fmt([l,h,r,t]),
                    body_bbox=fmt([l,t,r,b]),caption_text_layer=caption,header_text=' | '.join(display(v) for v in texhead),
                    optical_y_alignment_pt=f'{offset:.2f}',body_lines=len(rr)))
        for j,rec in enumerate(rr):
            index[item]+=1;i=index[item];y=rec['y'];yt=(rr[j-1]['y']+y)/2 if j else max(t,y-4.1)
            yb=(rr[j+1]['y']+y)/2 if j+1<len(rr) else min(b,y+4.1)
            # Blank inter-group spacing is excluded from the image patch for each row.
            yt=max(yt,y-4.2);yb=min(yb,y+4.2)
            ps=defaultdict(list);os=defaultdict(list)
            for w in rec['p']:ps[bisect_right(cut,(w[0]+w[2])/2)].append(w)
            for w in rec['o']:os[bisect_right(cut,(w[0]+w[2])/2)].append(w)
            publications={};statuslist=[]
            for k,(field,x0,x1) in enumerate(zip(fields,edges,edges[1:])):
                pp,oo=ps[k],os[k];a,z=display(pp),display(oo)
                xi=max(0,round((x0+.8)*3-pix.x));xj=min(pix.width,round((x1-.8)*3-pix.x))
                yi=max(0,round((yt+.35)*3-pix.y));yj=min(pix.height,round((yb-.35)*3-pix.y));patch=dark[yi:yj,xi:xj]
                ink=patch.sum()/9
                crossings=[w for w in pp if w[0]<x0-1.0 or w[2]>x1+1.0]
                status='pdf_and_optical_agree' if a and z and norm(a)==norm(z) else 'readers_disagree' if a and z else 'pdf_layer_only' if a else 'optical_only' if z else 'ink_without_string' if ink>=1.55 else 'blank_at_scan_threshold'
                if crossings and a:status='column_assignment_review'
                value=a or z
                manual=[v for (mi,mp,mf,my),v in manuals.items() if (mi,mp,mf)==(item,pg,field) and abs(my-y)<1.6]
                if item=='IR02.T02' and field=='group_margin':
                    status='vertical_label_in_separate_table';value=''
                if manual:
                    assert len(manual)==1,(field,y,item)
                    value=manual[0]['reading'];status='visually_collated'
                publications[field]=value;statuslist.append(status);st[item][status]+=1
                cells.append(dict(item_id=item,pdf_page=pg,printed_page=loc['printed_page'],print_row=i,
                         row_y_pt=f'{y:.2f}',field=field,reading=value,review_status=status,
                         pdf_text=a,optical_text=z,cell_bbox_pt=fmt([x0,yt,x1,yb]),source_word_bbox_pt=bounds(pp),
                         optical_word_bbox_pt=bounds(oo),dark_area_pt2=f'{ink:.2f}'))
            distinct=sum(bool(v) for v in publications.values())
            cell_status=Counter(statuslist)
            rows.append(dict(item_id=item,print_row=i,pdf_page=pg,printed_page=loc['printed_page'],
                         source_row_bbox_pt=fmt([l,yt,r,yb]),row_y_pt=f'{y:.2f}',row_kind='multi_field_print_line' if distinct>1 else 'single_field_or_continuation',
                         reading_status='review_cells' if any(x not in ['pdf_and_optical_agree','visually_collated','blank_at_scan_threshold','vertical_label_in_separate_table'] for x in statuslist) else 'two_readings_agree_or_visually_collated',
                         cell_readings_json=json.dumps({k:v for k,v in publications.items() if v},ensure_ascii=False,separators=(',',':'))))
    for item,n in index.items():
        ref=items[item];gg=[o for o in regions if o['item_id']==item]
        status=st[item];total=sum(status.values());review=total-status['pdf_and_optical_agree']-status['visually_collated']-status['blank_at_scan_threshold']-status['vertical_label_in_separate_table']
        datasets.append(dict(dataset_id=item+'.printcells.v2',item_id=item,chapter=ref['chapter'],site=ref['site'],
             title_as_indexed=ref['title'],caption_text_layer=gg[0]['caption_text_layer'],row_count=n,cell_count=total,visually_collated_cells=status['visually_collated'],
             agreeing_cells=status['pdf_and_optical_agree'],review_cells=review,separately_spanning_slots=status['vertical_label_in_separate_table'],blank_at_scan_threshold=status['blank_at_scan_threshold'],
             pdf_pages=','.join(g['pdf_page'] for g in gg),printed_pages=','.join(g['printed_page'] for g in gg),
             source_pdf_path=ref['pdf_path'],page_source_sha256=gg[0]['sha256'],data_path='edition2_print/data/print_rows.csv.gz',
             cell_data_path='edition2_print/data/print_cells.csv.gz',representation='named_print_cells_with_scan_collation'))
    for path,content in [('datasets.csv',datasets),('regions.csv',regions),('print_rows.csv.gz',rows),('print_cells.csv.gz',cells)]:save(DATA/path,content)
    print(len(datasets),'tables,',len(rows),'physical data lines,',len(cells),'cell slots')
    print(Counter(c['review_status'] for c in cells))
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('ir_primary',type=Path);run(ap.parse_args().ir_primary)
