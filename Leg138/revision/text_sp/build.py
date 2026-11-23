"""Compile the visually read line corrections and reading order against the fixed print witnesses."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

import fitz

import operations

HERE = Path(__file__).resolve().parent
DIGEST = {'SP': '7934144bec5ec839c5a95c113cec9a266ac2ad5ef4b97b50cd44ffad3d534e37',
          'PR': '48f7d7e22f672f499c38d610d995ad713874cfd01bc29516cf6b2f4cbe6d18c5'}
SOURCE = {'SP': 'https://www-odp.tamu.edu/publications/prosp/digital/138prosp.pdf',
          'PR': 'https://www-odp.tamu.edu/publications/prelim/138PREL.PDF'}
ROLE = {'r':'running_head','h':'heading','p':'body','a':'author_affiliation', 'b':'bibliography',
        'l':'list_item','i':'imprint', 's':'printed_signatory', 't':'title','d':'dateline'}

# Each group is a paragraph or stand-alone label; ordinals address the unaltered PDF text layer.
GROUPS = {
 'SP': {
  1:'t2 t3 t4 a5,7,9,11,13,15 a6,8,10,12,14 a16-20 s21-23 s25-28 s29-31 d32',
  2:'p1-5 i6-7 h8 p9-12 h13 p14-17 l18 l19 l20 l21 l22 l23 l24-26 p27-30 p31-38',
  3:'r1-3 h4 p5-11 h12 p13-17 p18-24 h25 p26-29 p30-40',
  4:'r1-3 p4-8 p9-18 p19-25 h26 p27-28 l29-30 l31 l32-33 l34-36 l37-38 l39-40 p41-43',
  5:'r1-3 p4-12 p13-18 h19 p20-25 p26-32 h33 p34-41',
  6:'r1-3 h4 p5-18 p19-25 p26-35 p36-38',
  7:'r1-3 h4 b5-6 b7-8 b9-10',
 },
 'PR': {
  6:'h1 p2-8 p9-16 p17-19 h20 p21-25 p26-29 h30 p31 l32-33 l34 l35-36 l37-39',
  7:'r1-3 l4-5 l6 p7-8 p9-18 h19 p20-28 h29 h30 h31 p32-36 p37-41',
  8:'r1-3 p4-5 p6-13 p14-20 p21-36 p37-43 p44-47',
  9:'r1-3 p4-7 p8-16 h17 p18-21 p22-33 p34-44 p45-47',
  10:'r1-3 p4-9 p10-20 p21-33 p34-47 p48',
  11:'r1-3 p4-8 p9-14 p15-25 p26-32 p33-40 h41 p42-47',
  12:'r1-3 p4-9 p10-22 p23-31 p32-42 p43-48',
  13:'r1-3 p4-10 p11-16 p17-29 p30-39 h40 p41-48',
  14:'r1-3 p4-25 p26-33 p34-38 p39-47',
  15:'r1-3 p4-12 p13-24 p25-29 p30-47 p48',
  16:'r1-3 p4-12 h13 h14 p15-19 p20-25 p26-38 p39-41 p42-46',
  17:'r1-3 p4-16 p17-27 h28 p29-31 p32-38 p39-48',
  18:'r1-3 p4 p5-14 p15-23 p24-29 p30-40 h41 p42-47',
  19:'r1-3 p4-7 p8-15 p16-23 p24-37 p38-46 p47',
  20:'r1-3 p4-13 p14-36 p37-43 p44-48',
  21:'r1-3 h4 p5-8 p9-17 p18-25 p26-39 p40-48',
  22:'r1-3 p4-9 h10 p11-14 p15-22 p23-32 p33-39 p40-43 p44-45',
  23:'r1-3 p4-11 p12-16 p17-21 p22-25 p26-31 p32-39 h40 p41-45 p46',
  24:'r1-3 p4-8 p9-16 p17-28 p29-33 p34-39 p40-46',
  25:'r1-3 p4-9 p10-13 h14 p15-25 p26-32 p33-38 p39-47',
  26:'r1-3 p4-12 p13-22 p23-29 p30-33 p34-42',
  27:'r1-3 h4 b5-6 b7-8 b9-10 b11-13 b14-16 b17-19 b20-21 b22-23 b24-25 b26-30 b31-32 b33-34 b35-37 b38-39 b40-41 b42-43 b44-45 b46 b47-50 b51-52',
  28:'r1-3 b4-5 b6-9 b10-12 b13-15',
 },
}

# Source-layer readings (left) and visible print (right) at individual line addresses.
READINGS = {
 'SP': {
  (1,21): [('Kabinowitz','Rabinowitz')], (1,25): [('W/','W.')],
  (2,13): [('D I S C L A I M E R','DISCLAIMER')], (2,20): [('Francais','Français'),("1'Exploitation","l'Exploitation")],
  (4,5): [('El Nino','El Niño')], (4,20): [('todayfs',"today's")],
  (5,4): [('radiation—the','radiation--the')], (5,37): [('O2','O₂')],
  (5,38): [('NO3','NO₃'),('NO2','NO₂'),('PO4','PO₄'),('Si(OH)4','Si(OH)₄'),('NH4','NH₄')],
  (7,9): [("0'Brien","O'Brien")],
 },
 'PR': {
  (6,5): [('Oceanographic','oceanographic')],(6,34): [('Oceanographic','oceanographic')],(6,37): [('Oceanographic','oceanographic')],
  (7,6): [('Oceanographic','oceanographic')],(7,8): [('Oceanographic','oceanographic')],
  (7,31): [('EEO-2','EEQ-2')],(7,40): [('Oceanographic','oceanographic')],
  (8,36): [('Oceanographic','oceanographic')],(8,43): [('Oceanographic','oceanographic')],
  (9,17): [('EEO-D','EEQ-1)')], (10,8): [('Oceanographic','oceanographic')],(10,44): [('Oceanographic','oceanographic')],
  (11,11): [('8.5 Ma)','8.5 Ma )')], (11,41): [('EEO-4','EEQ-4')],(11,44): [('Fig.l','Fig.1')],
  (12,4): [('APCs',"APC's")],(12,21): [('Zone~Hey','Zone--Hey')],(12,30): [('m.y.—Fig.','m.y.--Fig.')],
  (13,15): [('Miocene~a','Miocene--a')],(13,24): [('H2S','H₂S')],(13,40): [('EEO-3','EEQ-3')],
  (13,42): [('Oceanographic','oceanographic')],(13,48): [('circulation-changes','circulation--changes')],
  (14,4): [('Oceanographic','oceanographic')],(14,12): [('Oceanographic','oceanographic')],
  (14,25): [('chert~the','chert--the')],(14,43): [('m.y.—Fig.','m.y.--Fig.')],
  (15,48): [('Ma.','Ma .')],(16,14): [('WEO-5','WEQ-5')], (16,19): [('APCs',"APC's")],
  (17,24): [('Oceanographic','oceanographic')],(17,28): [('WEO-fr','WEQ-6')],
  (18,39): [('Oceanographic','oceanographic')],(18,47): [('Oceanographic','oceanographic')],
  (21,4): [('WEO-fi','WEQ-4)')],(22,5): [('transect Sedimentation','transect. Sedimentation')],
  (22,10): [('WEO-3^','WEQ-3)')],(23,19): [('Oceanographic','oceanographic')],(23,40): [('WEO-7','WEQ-7')],
  (25,14): [('Site 854 (proposed','Site 854 (proposed Site WEQ-2)')],
  (27,5): [('DSDP.','DSDP,')],(27,7): [('ODP.','ODP,'),('Results.','Results,')],(27,10): [('Geology.','Geology,')],
  (27,13): [('ODP.','ODP,'),('Repts..','Repts.,')],
  (27,15): [('Theyer, R, et al,','Theyer, F., et al.,'),('Repts. DSDP.','Repts. DSDP,')],
  (27,21): [('Science^','Science,')],(27,22): [('Bull..','Bull.,')],(27,25): [('Bull..','Bull.,')],
  (27,26): [('Mclntyre','McIntyre'),('Mix, A. C,','Mix, A. C.,')],
  (27,32): [('Res..','Res.,')],(27,34): [('Res..','Res.,')],(27,35): [('Moore, T. C,','Moore, T. C.,')],
  (27,37): [('Ouat. Res..','Quat. Res.,')],(27,41): [('Oceanographic','oceanographic'),('Science.','Science,')],
  (27,42): [('DSDP.','DSDP,')],(27,48): [('In_','In')],(27,49): [('CO2:','CO₂:')],
  (28,4): [('America. N.','America, N,')],(28,10): [('Moore, T. C,','Moore, T. C.,'),('Tectonics.','Tectonics,')],
  (28,15): [('DSDP.','DSDP,')],
 },
}
# Explicit typography where linear Unicode is inadequate (Corg has no complete Unicode subscript spelling).
MARKS = {'SP':{(2,13):[('DISCLAIMER','underline')],(6,21):[('Thomas Washington','italic')],
               (7,6):[('Journal of Marine Research','italic'),('43','bold')],
               (7,8):[('Deep Sea Research','italic'),('34','bold')],(7,10):[('Science','italic'),('214','bold')]},
         'PR':{(7,30): [('EASTERN TRANSECT','underline')],(7,31): [('Site 844 (proposed Site EEQ-2)','underline')],
               (11,41):[('Site 846 (proposed Site EEQ-4)','underline')],(13,40):[('Site 847 (proposed Site EEQ-3)','underline')],
               (13,22):[('org','subscript')],(13,28):[('org','subscript')]}}


# Underlined headings and references are directly visible on the print pages.
UNDERLINED = {
 (9,17):['Site 845 (proposed Site EEQ-1)'],(16,13):['WESTERN TRANSECT'],(16,14):['Site 848 (proposed Site WEQ-5)'],
 (17,28):['Site 849 (proposed Site WEQ-6)'],(18,26):['Thalassiothrix longissima'],(18,41):['Site 850 (new site)'],
 (21,4):['Site 851 (proposed Site WEQ-4)'],(22,10):['Site 852 (proposed Site WEQ-3)'],
 (23,40):['Site 853 (proposed Site WEQ-7)'],(25,14):['Site 854 (proposed Site WEQ-2)'],
 (27,5):['Init. Repts. DSDP'],(27,7):['Proc. ODP, Sci. Results'],(27,10):['Geology'],(27,12):['In Kroenke'],
 (27,13):['Proc. ODP, Init. Repts.'],(27,15):['In Mayer','Init. Repts. DSDP'],(27,17):['In'],(27,18):['The Ocean Basins and Margins'],
 (27,21):['Science'],(27,22):['Geol. Soc. of Am. Bull.'],(27,24):['Geol.'],(27,25):['Soc. of Am. Bull.'],
 (27,28):['In Berger'],(27,29):['Milankovitch and Climate (Pt. 1)'],(27,32):['Jour. Geophys. Res.'],(27,34):['Jour. Geophys. Res.'],
 (27,37):['Quat. Res.'],(27,39):['Nature'],(27,41):['Science'],(27,42):['Init. Repts. DSDP'],(27,44):['In Bally'],
 (27,45):['Seismic Expressions of Structural Styles'],(27,48):['In Sunquist'],(27,49):['The Carbon Cycle and Atmospheric CO₂: Natural Variations'],
 (27,50):['Archean to Present'],(27,52):['In Winterer'],(28,4):['The Geology of North America, N, The Eastern Pacific Ocean and Hawaii'],
 (28,7):['In Watkins'],(28,8):['Studies in Continental Margin Geology'],(28,10):['Cenozoic Tectonics, Sedimentation,'],
 (28,11):['and Paleoceanography of the Central Equatorial Pacific'],(28,14):['In Larson','Init. Repts.'],(28,15):['DSDP'],
}
GROUPS['PR'].update(operations.GROUPS)
READINGS['PR'].update(operations.READINGS)
UNDERLINED.update(operations.UNDERLINED)
for address,words in UNDERLINED.items():
    MARKS['PR'].setdefault(address,[]).extend((word,'underline') for word in words)
MARKS['PR'][(27,28)].append(('18','superscript'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ordinals(group):
    result = []
    for bounds in group[1:].split(','):
        endpoints = [int(value) for value in bounds.split('-')]
        result.extend(range(endpoints[0], endpoints[-1] + 1))
    return result


def compile_page(doc_id, source_page, pdf):
    page = pdf[source_page - 1]
    physical = [line for block in page.get_text('dict', flags=fitz.TEXTFLAGS_TEXT)['blocks']
                for line in block['lines']]
    objects = page.get_images()
    assert len(objects) == 1, (doc_id, source_page, objects)
    image = pdf.extract_image(objects[0][0])
    blocks, variants, used = [], [], set()
    groups = GROUPS[doc_id][source_page]
    corrections = READINGS[doc_id]
    for number, group in enumerate(groups.split(), 1):
        ids = ordinals(group)
        block_id = f'{doc_id}.p{source_page:03}.b{number:02}'
        lines, locations, marks = [], [], []
        for line_id in ids:
            assert line_id not in used
            used.add(line_id)
            line = physical[line_id-1]
            value = ''.join(s['text'] for s in line['spans']).strip()
            for old, new in corrections.get((source_page,line_id),[]):
                assert value.count(old) == 1, (doc_id, source_page,line_id,old,value)
                value = value.replace(old,new,1)
                variants.append([doc_id,source_page,line_id,block_id,old,new,'printed_reading'])
            lines.append(value)
            locations.append([round(k,2) for k in line['bbox']])
            for token, style in MARKS[doc_id].get((source_page,line_id),[]):
                # 'org' binds to the analyte Corg, rather than 'organic' elsewhere on the line.
                start = value.index('Corg') + 1 if token == 'org' else value.index(token)
                # Specific 'In' before editor names is underlined, not the name itself.
                end = start + (2 if token.startswith('In ') else len(token))
                marks.append(dict(line=line_id,begin=start,end=end,style=style,text=value[start:end]))
        # Keep lexical hyphens at line breaks (including large-scale, north-south).
        text = lines[0]
        starts = {ids[0]:0}
        for index, (left,right) in enumerate(zip(lines,lines[1:]),1):
            # On PR p109 the layer splits a single printed line before its degree sign.
            same_print_line = (doc_id, source_page, ids[index]) == ('PR',109,16)
            spacing = '' if left.endswith('-') or same_print_line else ' '
            starts[ids[index]] = len(text) + len(spacing)
            text += spacing + right
        inline_styles = [dict(begin=starts[m['line']]+m['begin'],end=starts[m['line']]+m['end'],style=m['style']) for m in marks]
        for inline,m in zip(inline_styles,marks):
            assert text[inline['begin']:inline['end']] == m['text']
        bbox=[min(loc[0] for loc in locations),min(loc[1] for loc in locations),
              max(loc[2] for loc in locations),max(loc[3] for loc in locations)]
        # Publisher OCR stops partway along the Site 854 heading. Retain its own
        # bbox and add an independent print region spanning the complete heading.
        if (doc_id,source_page,group)==('PR',25,'h14'):
            bbox[2] = 227.0
        blocks.append(dict(id=block_id,role=ROLE[group[0]],text=text,source_lines=lines,
                           line_ordinals=ids,line_bboxes_pt=locations,bbox_pt=bbox,styles=marks,inline_styles=inline_styles))
    excluded = []
    if (doc_id,source_page) == ('SP',1):
        for ordinal,note in [(1,'Speck in upper margin'),(24,'Fragment of manuscript signature')]:
            value=''.join(s['text'] for s in physical[ordinal-1]['spans']).strip()
            variants.append([doc_id,source_page,ordinal,'',value,'',note])
            excluded.append(dict(line=ordinal,publisher_text=value,reason=note))
    assert used == set(range(1,len(physical)+1)) - {a['line'] for a in excluded}, (doc_id,source_page,len(physical), used)
    scope = 'all printed text; three manuscript signatures retained in witness only' if (doc_id,source_page)==('SP',1) else 'all printed text'
    folio = next((int(line.split()[-1]) for b in blocks if b['role']=='running_head'
                  for line in b['source_lines'] if line.lower().startswith('page ')),None)
    row=dict(doc_id=doc_id,source_page=source_page,witness_sha256=DIGEST[doc_id],
             source_url=SOURCE[doc_id]+f'#page={source_page}',review_scope=scope,
             review_method='visual scan collation by an AI editor; no independent human sign-off',
             native_image_sha256=sha(image['image']),native_image_size_px=[image['width'],image['height']],
             printed_folio=folio,excluded=excluded,blocks=blocks)
    return row,variants


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('originals', type=Path, help='directory containing original SP.pdf and PR.pdf')
    parser.add_argument('--out', type=Path, default=HERE)
    parser.add_argument('--check', action='store_true', help='compare against the committed collation without rewriting it')
    parser.add_argument('--doc',choices=('SP','PR'),action='append',help='Select a publication; use a separate output for a subset')
    args=parser.parse_args(); pages=[];variants=[]
    selected=set(args.doc or GROUPS)
    if len(selected)<2 and args.out.resolve()==HERE:
        parser.error('Specify --out for a single-publication build')
    for key in GROUPS:
        if key not in selected:continue
        witness=(args.originals/f'{key}.pdf').read_bytes()
        if sha(witness)!=DIGEST[key]: raise ValueError(f'Unexpected {key} digital edition')
        with fitz.open(stream=witness,filetype='pdf') as pdf:
            for page_id in sorted(GROUPS[key]):
                page,edits=compile_page(key,page_id,pdf);pages.append(page);variants.extend(edits)
    data=''.join(json.dumps(p,ensure_ascii=False,separators=(',',':'))+'\n' for p in pages)
    buf=io.StringIO();cs=csv.writer(buf,lineterminator='\n');cs.writerow(['doc_id','source_page','pdf_line','reader_block','publisher_reading','print_reading','decision']);cs.writerows(variants)
    docs={}
    for key in GROUPS:
        if key not in selected:continue
        read=[p for p in pages if p['doc_id']==key]; blocks=[b for p in read for b in p['blocks']];
        docs[key]={'pages':len(read),'source_pages':[p['source_page'] for p in read], 'blocks':len(blocks),
              'printed_lines':sum(len(b['source_lines']) for b in blocks), 'variant_entries':sum(v[0]==key for v in variants),
              'witness_sha256':DIGEST[key]}
    outputs={'pages.jsonl':data,'variants.csv':buf.getvalue(),'verification.json':json.dumps(docs,indent=2)+'\n'}
    for name,value in outputs.items():
        output=args.out/name
        if args.check:
            if output.read_text(encoding='utf-8')!=value: raise ValueError(f'Collation differs in {name}')
        else:
            args.out.mkdir(exist_ok=True,parents=True); output.write_text(value,encoding='utf-8')
    print(json.dumps(docs))


if __name__ == '__main__':
    main()
