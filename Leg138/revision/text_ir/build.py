"""Rebuild Site 846's visually collated text from the exact publisher chapter."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

import fitz

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'edition2'))
from page_text import runs

DOC = 'IR.C11'
SHA = '9029db07c07283a3d30eb8ddb9ed4c075771f31cc48927876a5d6ee9f4cbc268'
URL = 'https://www-odp.tamu.edu/publications/138_IR/VOLUME/CHAPTERS/ir138_11.pdf'

# Visually established reading order. "+" joins pieces of one paragraph across source blocks.
# Colon addresses a line range inside a block. A bare block includes all its lines.
GROUPS = {
    1: 'i0 t1 a2 h3 ' + ' '.join('p'+str(n) for n in range(4,19)) +
       ' h19 ' + ' '.join('p'+str(n) for n in range(20,37)) +
       ' h39 ' + ' '.join('p'+str(n) for n in range(40,55)) +
       ' h55 ' + ' '.join('p'+str(n) for n in range(56,71)) + ' p71+72 n37 n38 f73',
    2: 'r0 p1 p2 p3 p4 p5 p6 p7 c8 f141',
    3: 'r0 p1 h2 p3 p4 p5 p6 p7 h8 h9 p10 p11+12 h13 p14 h15 p16 p17 h18 p19 p20 p21 p22 p23 f24',
    4: 'r0 c4 h5 p6 p7 h8 p9+10+11 p12 p13 h14 h15 p16 f17',
    5: 'r0 c11 p13 p14+15 p16 p17 h18 h19 h20 p21:1 p21:2 p21:3 p21:4 p21:5 p21:6 p22 h23 h24 p25:1 p25:2 p25:3 f26',
    6: 'r0 c6 p7:1 p7:2 p7:3 p7:4-16 p8+9 p10 p11 f12',
    7: 'r0 c2 c3 p35 h36 h37 p38:1 p38:2 p38:3 p39 p40 f41',
    29: 'r0 p1 p2 p3+4 p5 p6+7 p8 p9+10 p11 h12 p13 p14 h15 p16 p17 p18 p19 f20',
    30: 'r0 c6 c16 p17+18 p19+20 p21 f22',
    31: 'r0 c1 c2 n105 p106 p107+108 h109 p110 f111',
    32: 'r0 c13 f14', 33:'r0 c22 c42 p23+24 p25 p26+27 p28+43 p44 p45 f46',
    34: 'r0 c1 c84 f85', 35:'r0 p1 p2 p3 p4 p5 p6 c13 f14',
    36: 'r0 c7 p8 p9 p10 h11:1 h11:2 p12+13 p14+15 p16 f17'
}
ROLE = {'r':'running_head', 'p':'body','c':'caption','h':'heading','i':'imprint','a':'author_affiliation',
        't':'title','n':'notice','f':'folio','k':'table_header','q':'table_row'}
EXCLUSIONS = {
    1: '', 2: 'Table 1 body and its column headings', 3: '',
    4: 'Figure 1 interior, including map labels', 5:'Figure 2 interior, including map labels',
    6:'Figure 3 interior, including map labels', 7:'Figure 4 interior; Table 2 body and its column headings',
    29:'', 30:'Figures 19 and 20 interiors', 31:'Tables 7 and 8 bodies and headers; Table 8 note is included',
    32:'Figure 22 interior', 33:'Figures 23 and 24 interiors',
    34:'Table 9 body and headers; Figure 25 interior', 35:'Figure 26 interior', 36:'Figure 27 interior'
}
EDITS = {
  1: {(1,1): [('8461','846¹')], (2,1): [('Party2','Party²')],
      **{(n,1):[("'S","′S"),("'W","′W")] for n in (7,23,43,59)},
      (37,1):[('1 Mayer', '¹ Mayer')], (38,1):[('Shipboard', '² Shipboard')], (71,1):[("Leg 138's","Leg 138’s")]},
  2: {(2,2):[('0-317','0–317')], (2,4):[('317.0-419.2','317.0–419.2')],
      (5,2):[('"soft"', '“soft”')], (7,4):[('H2S','H₂S')]},
  3: {(1,1):[('"Leadsville"','“Leadsville”'),('Paleomagnetism','paleomagnetism')],
      (1,5):[('"platinum mine"','“platinum mine”')], (16,7):[('197.0-206.5','197.0–206.5')],
      (17,1):[('BOOL','1300L')], (17,2):[('206.5^18.6','206.5–418.6')],
      (21,6):[('"hot spots"','“hot spots”')]},
  4: {(4,4):[('Chile Current','= Chile Current')], (6,4):[('2.5-31.0','2.5–31.0')],
      (9,3):[('(4.0-','(4.0–')]},
  5: {(15,1):[('%CaCO3','%CaCO₃')], (15,11):[('4-8 cm','4–8 cm')], (16,12):[('<l %','<1%')],
      (21,5):[('0-317.0','0–317.0')], (21,6):[('0-10.6','0–10.6')], (22,7):[('7.0-10.6','7.0–10.6')]},
  6: {(7,2):[('0-262.7','0–262.7')], (7,3):[('0-7.0','0–7.0')], (7,9):[('Cores 1-6','Cores 1–6')],
      (7,11):[('(-50%', '(~50%')], (8,1):[('Cores 6-9','Cores 6–9')], (8,3):[('10%-40%','10%–40%')],
      (9,2):[('Plagioclase','plagioclase')], (10,1):[('Cores 9-22','Cores 9–22')], (10,4):[('50%-80%','50%–80%')],
      (10,6):[('"Organic Geochemistry"','“Organic Geochemistry”')], (11,2):[('22X-25X','22X–25X'),('22H-26X','22H–26X')],
      (11,4):[('Plagioclase','plagioclase')]},
  7: {(2,1):[('Seismic Line','Figure 4. Seismic Line'),('80-in.','80-in.³')], (38,2):[('262.7-317.0','262.7–317.0')],
      (38,3):[('7.0-10.6','7.0–10.6')], (39,4):[('262.7-290','262.7–290')], (39,5):[('-3IX','-31X')],
      (40,6):[('10%-30%','10%–30%')]}
}
EDITS.update({
    29: {(1,4):[('mis zone','this zone')],(1,6):[('4,90','4, 90'),('Aon','A on')],
         (3,1):[('4,70','4, 70')],(4,1):[('4,70','4, 70')],(4,2):[('Aof','A of')],
         (4,3):[('4,70','4, 70')],(4,5):[('TV. miocenica','N. miocenica')],(7,2):[('5,103','5, 103')],
         (13,5):[('I0"4','10⁻⁴')],(14,3):[('"soft"','“soft”')]},
    30: {(21,4):[('Nitschiajouseae','Nitschia jouseae')]},
    31: {(107,2):[('40-50','40–50')]},
    33: {(23,2):[('"Lithostratigraphy"','“Lithostratigraphy”')],(24,1):[('370.3-379.9','370.3–379.9')],
         (25,6):[('H2S','H₂S')],(26,1):[('H2S','H₂S')],(26,3):[('H2S','H₂S')],(28,1):[('25 A','25A')],
         (45,5):[('846A- 1H','846A-1H')],(45,11):[('H2S','H₂S')]},
    35:{(3,1):[('27 A','27A')],(6,5):[('"Organic Geochemistry"','“Organic Geochemistry”')]},
    36:{(8,1):[('"Biostratigraphy"','“Biostratigraphy”')],(8,5):[('"Downhole Measurements"','“Downhole Measurements”')],
        (10,5):[('H2S','H₂S')], **{(13,i):[('%CaCO3','%CaCO₃')] for i in (1,7,9,12)},
        (13,2):[('"Explanatory Notes"','“Explanatory Notes”')],(13,6):[('"Sedimentation Rates"','“Sedimentation Rates”')],
        (13,11):[('"Sedimentation Rates"','“Sedimentation Rates”')],(14,2):[('"Lithostratigraphy"','“Lithostratigraphy”')],
        (14,5):[('%CaCO3','%CaCO₃')],(14,6):[('846B-IH','846B-1H')],(16,1):[('6,30cm,to-34X-4,110','6, 30 cm, to -34X-4, 110')],
        (16,2):[('%CaCO3','%CaCO₃')],(16,3):[('%CaCO3','%CaCO₃')]}
})
KEEP_BREAK_HYPHEN = {(3,14,4),(3,16,9),(4,10,1),(5,16,2),(7,35,3),(7,35,7),
                     (29,1,2),(29,3,5),(29,4,2),(29,4,3),(29,7,1),(30,18,4),(30,18,5)}
# Inline styles not carried in plain Unicode. Source line breaks are still in source_lines.
ITALIC = {1: {'i0':['Proceedings of the Ocean Drilling Program, Initial Reports'],
              'n37':['Proc. ODP, Init. Repts.']},
          3: {'p1':['P-wave|0:1'],'p6':['Thomas Washington','JOIDES Resolution'],
              'p10':['JOIDES Resolution','Moby Dick']}, 4: {'p13':['JOIDES Resolution']},
          5: {'h19':['Unit I'],'h23':['Subunit IA']}, 6: {'c6':['Thomas Washington']},
          7: {'c2':['Thomas Washington'],'h36':['Subunit IB']}}

ITALIC.update({
    29:{'p1':['P. doliolus','T. convexa','R. praebergonii','N. jouseae'],
        'p2':['N. jouseae','R. praebergonii'],
        'p3+4':['T. convexa','T. miocenica','N. jouseae','T. praeconvexa','N. miocenica','elongata','Nitzschia porteri'],
        'p5':['T. yabei','D. hustedtii','C. coscinodiscus','C. lewisianus'],
        'p6+7':['T. yabei','Nitzschia cylindrica','Actinocyclus moronensis','D. hustedtii','A. moronensis','C. coscinodiscus'],
        'p8':['Thalassiosira temperi','delicata','C. coscinodiscus','Coscinodiscus gigas','diorama','N. porteri'],
        'p9+10':['C. gigas','diorama','Cestodiscus pulchellus','Coscinodiscus gigas','Actinocyclus ingens'],
        'p11':['Coscinodiscus lewisianus','C. lewisianus']},
    30:{'p21':['Discoaster surculus','Nitschia jouseae','Discoaster quinqueramus','Discoaster berggreni','Coccolithus miopelagicus']},
    31:{'p106':['D. berggreni','Amaurolithus primus','Discoaster hamatus'],
        'p107+108':['Helicosphaera ampliaperta','H. ampliapertura']}
})

from additional import (CAPTIONS, PARTIAL_SCOPE, ADDITIONAL_EXCLUSIONS, ADDITIONAL_EDITS,
                        ADDITIONAL_ITALIC, ADDITIONAL_HYPHENS, MARGINS)

GROUPS.update(CAPTIONS)
GROUPS = dict(sorted(GROUPS.items()))
EXCLUSIONS.update({n:'material outside selected blocks' for n in PARTIAL_SCOPE})
EXCLUSIONS.update(ADDITIONAL_EXCLUSIONS)
EDITS.update(ADDITIONAL_EDITS)
ITALIC.update(ADDITIONAL_ITALIC)
KEEP_BREAK_HYPHEN.update(ADDITIONAL_HYPHENS)

def csv_text(rows, fields):
    buff=io.StringIO()
    writer=csv.DictWriter(buff,fields,lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return buff.getvalue()

def block_rows(group, physical):
    selected=[]
    for piece in group[1:].split('+'):
        bits=piece.split(':')
        block=int(bits[0])
        bounds=[int(x) for x in bits[1].split('-')] if len(bits)>1 else None
        rows=[(k,v) for k,v in physical.items() if k[0]==block and
              (not bounds or bounds[0]<=k[1]<=bounds[-1])]
        if not rows:
            raise ValueError(f'Empty source selection {piece}')
        selected.extend(sorted(rows))
    return selected

def inline_styles(page, group, text):
    styles=[]
    for target in ITALIC.get(page,{}).get(group,[]):
        word, _, scope=target.partition('|')
        last=0
        while (begin:=text.find(word,last))>=0:
            last=begin+len(word)
            a,b=(map(int,scope.split(':')) if scope else (0,len(word)))
            styles.append(dict(begin=begin+a,end=begin+b,style='italic'))
        if last==0:
            raise ValueError(f'Unknown style target: {word}')
    if page==1 and group.startswith('p') and ':' in text and group not in {'p18','p34','p36','p54','p70'}:
        styles.append(dict(begin=0,end=text.index(':')+1,style='bold'))
    if page in {36,37,38,39,41,42,43,52,53}:
        start=0
        while (at:=text.find('Corg',start))>=0:
            start=at+4
            styles.append(dict(begin=at+1,end=at+4,style='subscript'))
    if (page,group) in {(32,'c13'),(34,'c84'),(35,'c13'),(36,'c7')}:
        import re
        for match in re.finditer(r'(?<![A-Za-z])[A-D]\.', text):
            styles.append(dict(begin=match.start(),end=match.end(),style='bold'))
    if page in CAPTIONS:
        import re
        if group.startswith('c') and text.startswith('Table ') or page==54 and group in {'n1','n2'}:
            styles.append(dict(begin=0,end=len(text),style='bold'))
        if group.startswith('c') and page in {39,41,42,43,45,46,47,48,49,59,60}:
            for m in re.finditer(r'\([A-D]\)|(?<![A-Za-z])[A-D]\.',text):
                a,b=m.span()
                if text[a]=='(':a+=1;b-=1
                styles.append(dict(begin=a,end=b,style='bold'))
        for m in re.finditer('UK′37',text):
            styles.append(dict(begin=m.start()+1,end=m.start()+3,style='superscript'))
            styles.append(dict(begin=m.start()+3,end=m.end(),style='subscript'))
    return styles

def compile_page(doc, n):
    page=doc[n-1]
    _,packets=runs(page)
    physical={(r['block'],r['line'],r['part']):r for pk in packets for r in pk['lines']}
    ords={(b['number'],j):i for i,(b,j) in enumerate(
        ((b,j) for b in page.get_text('dict',flags=fitz.TEXTFLAGS_TEXT)['blocks']
             if b['type']==0 for j in range(1,len(b['lines'])+1)),1)}
    publisher_segments=len(physical)
    if n in MARGINS:
        for block,bbox in zip((-1,-2),MARGINS[n]):
            physical[(block,1,1)]=dict(text='',bbox=list(bbox))
    used=set()
    lines=[];blocks=[];variants=[]
    for bi,group in enumerate(GROUPS[n].split(),1):
        block_id=f'{DOC}.p{n:03d}.b{bi:02d}'
        block_lines=[]; boxes=[]; addresses=[]; ids=[]
        text=''
        previous=None
        for key,original in block_rows(group,physical):
            if key in used: raise ValueError(f'Duplicate use: {n} {key}')
            used.add(key)
            value=original['text']
            pdf_ordinal=ords.get(key[:2])
            if key[0]<0:
                value='SITE 846' if key[0]==-1 else str(n+264)
                variants.append(dict(doc_id=DOC,source_page=n,pdf_line='',reader_block=block_id,
                                     publisher_reading='',print_reading=value,decision='supplied_from_scan'))
            for old,new in EDITS.get(n,{}).get(key[:2],[]):
                if value.count(old)!=1: raise ValueError((n,key,old,value))
                value=value.replace(old,new,1)
                variants.append(dict(doc_id=DOC,source_page=n,pdf_line=pdf_ordinal,
                                     reader_block=block_id,publisher_reading=old,
                                     print_reading=new,decision=('editorial_restoration' if (n,*key[:2])==(37,58,2) else 'printed_reading')))
            if text.endswith('-'):
                if (n,*previous[:2]) not in KEEP_BREAK_HYPHEN: text=text[:-1]
                text+=value
            elif text.endswith('–') or value.startswith(('³,','³.','³ ')):
                text+=value
            else:
                text+=(' ' if text else '')+value
            previous=key
            lines.append(dict(doc_id=DOC,source_page=n,block=key[0],line=key[1],part=key[2],raw=original['text'],
                              reading=value,status=('restored_damaged_character' if (n,*key[:2])==(37,58,2) else 'visual_scan_reading'),bbox_pt=json.dumps(original['bbox'],separators=(',',':')),
                              witness_sha256=SHA,order=len(lines)+1))
            if pdf_ordinal is not None: ids.append(pdf_ordinal)
            block_lines.append(value.replace('density','de□sity') if (n,*key[:2])==(37,58,2) else value);boxes.append(original['bbox']);addresses.append(list(key))
        box=[fn(v[i] for v in boxes) for i,fn in enumerate([min,min,max,max])]
        blocks.append(dict(id=block_id,role=ROLE[group[0]],text=text,source_lines=block_lines,
                           line_ordinals=ids,line_bboxes_pt=boxes,source_addresses=addresses,
                           bbox_pt=box,inline_styles=inline_styles(n,group,text)))
    missing=set(EDITS.get(n,{}))-{k[:2] for k in used}
    assert not missing,missing
    if not EXCLUSIONS[n]: assert set(physical)==used,(n,set(physical)-used)
    obj=page.get_images()
    assert len(obj)==1,(n,obj)
    im=doc.extract_image(obj[0][0])
    scope='all printed text' if not EXCLUSIONS[n] else 'all narrative, captions, headings, running head and folio; excludes '+EXCLUSIONS[n]
    scope=PARTIAL_SCOPE.get(n,scope)
    page_record=dict(doc_id=DOC,source_page=n,witness_sha256=SHA,source_url=URL+f'#page={n}',
                     printed_folio=264+n,review_scope=scope,overlay_only=n in PARTIAL_SCOPE,
                     coverage_kind=("selected_blocks" if n in PARTIAL_SCOPE else
                                    "all_narrative_and_captions" if EXCLUSIONS[n] else "all_printed_text"),review_method='visual scan collation by an AI editor; no independent human sign-off',
                     native_image_sha256=hashlib.sha256(im['image']).hexdigest(),
                     native_image_size_px=[im['width'],im['height']],blocks=blocks)
    summary=dict(doc_id=DOC,source_page=n,printed_page=n+264,source_lines=len(lines),publisher_segments=publisher_segments,
                 edited_lines=sum(x['reading']!=x['raw'] for x in lines),scope=scope,witness_url=page_record['source_url'])
    return page_record,lines,variants,summary

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path,help='Publisher IR chapter 11 PDF')
    parser.add_argument('--out',type=Path,default=HERE)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    raw=args.source.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('Different digital witness')
    with fitz.open(stream=raw,filetype='pdf') as pdf:
        data=[compile_page(pdf,n) for n in GROUPS]
    payload={}
    payload['pages.jsonl']=''.join(json.dumps(p[0],separators=(',',':'),ensure_ascii=False)+'\n' for p in data)
    for name,rows in [('lines.csv',[r for p in data for r in p[1]]),('variants.csv',[r for p in data for r in p[2]]),
                      ('pages.csv',[p[3] for p in data])]:
        payload[name]=csv_text(rows,list(rows[0]))
    epochs=next(p[0] for p in data if p[0]['source_page']==21)
    table_rows=[b for b in epochs['blocks'] if b['role']=='table_row']
    rows=[]
    for b in table_rows:
        boundary,hole,depth,composite,event=b['source_lines']
        rows.append(dict(boundary_as_printed=boundary,hole=hole,mbsf=depth,mcd=composite,event_as_printed=event,
                         reader_block=b['id'],witness_sha256=SHA,source_page=21,printed_page=285))
    payload['epoch_boundaries.csv']=csv_text(rows,list(rows[0]))
    findings=dict(doc_id=DOC,source_pages=list(GROUPS),full_printed_text_pages=[n for n in GROUPS if not EXCLUSIONS[n]],
                  reviewed_line_segments=sum(len(p[1]) for p in data),corrected_print_readings=sum(len(p[2]) for p in data),
                  changed_lines=sum(p[3]['edited_lines'] for p in data),reader_blocks=sum(len(p[0]['blocks']) for p in data),
                  source_sha256=SHA,coverage_kind_counts={
                      k:sum(p[0]['coverage_kind']==k for p in data) for k in sorted({p[0]['coverage_kind'] for p in data})},
                  supplied_scan_only_segments=sum(v['decision']=='supplied_from_scan' for p in data for v in p[2]),
                  editorial_restorations=sum(v['decision']=='editorial_restoration' for p in data for v in p[2]))
    payload['verification.json']=json.dumps(findings,indent=2)+'\n'
    args.out.mkdir(exist_ok=True,parents=True)
    for name,s in payload.items():
        path=args.out/name
        if args.check:
            if path.read_bytes()!=s.encode('utf-8'):raise ValueError(f'Different output {name}')
        else:path.write_bytes(s.encode('utf-8'))
    print(json.dumps(findings))

if __name__=='__main__':
    main()
