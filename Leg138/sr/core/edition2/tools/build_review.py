"""Publish the visually reviewed object identities while keeping previous locators and rejected candidates."""
from pathlib import Path
import csv,json,gzip,collections,re
import fitz
from PIL import Image,ImageDraw,ImageFont
E=Path(__file__).resolve().parents[1];C=E.parent;P=C.parent/'primary'
def read(name):return list(csv.DictReader((C/name).open()))
def emit(name,rows):
    with (E/'data'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
OLD={x['item_id']:x for x in read('items.csv')}
CH={int(x['chapter']):x for x in read('chapters.csv')}
RETRACT={
 'SR.C13.FIGURE12A':('SR.C13.FIGURE12','In running prose an author refers to panel A of Figure 12; the full caption is on leaf 14.'),
 'SR.C17.FIGURE15A':('SR.C17.FIGURE15','A sentence continues after a reference to panel A. The numbered caption introducing the panels is on leaf 17.'),
 'SR.C47.TABLE1':('SR.C47.TABLE1A|SR.C47.TABLE1B|SR.C47.TABLE1C|SR.C47.TABLE1D','The prose refers to the four printed lettered tables collectively. There is no separate unlettered table heading.')}
SPECIAL={
 'SR.C03.APPENDIX1':(3,7,(285,563,533,585),0,'CD-ROM as Appendix (back pocket, this volume).','publisher_disc_pointer'),
 'SR.C21.FIGURE17':(21,1,(20,9,379,30),0,'ODP Proceedings, Scientific Results, Volume 138: Chapter 21: Figure 17.','foldout_title'),
 'SR.C31.TABLE1':(31,5,(341,263,354.8,466),90,'Table 1. Classification of the laminae.','rotated_print_heading'),
 'SR.C37.TABLE1':(37,2,(78,280,104,486),90,'Table 1. Chemical composition of sedimentary formations.','rotated_print_heading'),
 'SR.C41.TABLE1':(41,2,(85,229,98.5,471),90,'Table 1. Summary of Leg 138 sites and Sr-isotope reversals.','rotated_print_heading'),
 'SR.C41.TABLE2':(41,6,(184,39,456,70),0,'Table 2. ⁸⁷Sr/⁸⁶Sr ratios and Sr concentrations of Leg 138 pore waters.','opening_caption_fragmented_text_layer'),
 'SR.C47.FIGURE3':(47,13,(289,667,537,704),0,'Fig. 3. The distribution of synchronous and diachronous faunal events as a function of age (data from Table 1).','true_caption_beside_running_reference'),
 'SR.C47.TABLE1C':(47,6,(240,84,576,107),0,'TABLE 1c. Radiolarian Biostratigraphic Events, ODP Leg 138, Sites 848 and 849','opening_caption_fragmented_text_layer'),
 'SR.C17.APPENDIXF':(17,42,(274,43,435,72),0,'APPENDIX F','additional_appendix_heading')}
def supplement():
    panel=Image.new('L',(772,9*67+25),'white');draw=ImageDraw.Draw(panel)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',10)
    draw.text((3,4),'Original-page overlays | alternative / rotated headings and additional appendix',font=font,fill='black')
    for j,(key,(ch,n,box,rot,text,role)) in enumerate(SPECIAL.items()):
        source='official/VOLUME/CHAPTERS/sr138_f21.pdf' if key=='SR.C21.FIGURE17' else CH[ch]['source']
        with fitz.open(P/source) as doc:
            p=doc[n-1].get_pixmap(matrix=fitz.Matrix(2,2).prerotate(rot),clip=fitz.Rect(box),colorspace=fitz.csGRAY)
        im=Image.frombytes('L',(p.width,p.height),p.samples);im.thumbnail((610,61))
        panel.paste(im,(146,24+j*67+(61-im.height)//2))
        draw.text((3,29+j*67),key+' p'+str(n),font=font,fill='black');draw.line((0,87+j*67,770,87+j*67),fill=215)
    panel.save(E/'atlas/supplement.png',optimize=True)
def review():
    originals=list(map(json.loads,gzip.open(E/'data/selected_lines.jsonl.gz','rt')))
    originals.append(dict(item_id='SR.C17.APPENDIXF',chapter=17,source=CH[17]['source'],pdf_page=42,previous_status='new',sheet='',cell=''))
    records=[];changes=[]
    for q in originals:
        key=q['item_id'];old=OLD.get(key);ch=int(q['chapter']);n=q['pdf_page'];source=q['source'];folio=q.get('print_page','')
        box=q.get('bbox');text=q.get('text','');basis=q.get('basis','');evidence=f"atlas/sheet{int(q['sheet']):02d}.png" if q.get('sheet') else '';cell=q['cell'];rot=0
        if key in SPECIAL:
            ch,n,box,rot,text,basis=SPECIAL[key];source='official/VOLUME/CHAPTERS/sr138_f21.pdf' if key=='SR.C21.FIGURE17' else CH[ch]['source']
            folio='' if key=='SR.C21.FIGURE17' else int(CH[ch]['print_page_first'])+n-1
            evidence='atlas/supplement.png';cell=list(SPECIAL).index(key)+1
        m=re.fullmatch(r'SR.C\d{2}\.(FIGURE|TABLE|PLATE|APPENDIX)([\dA-Z]*)',key)
        assert m
        old_page=int(old['pdf_page']) if old else ''
        changed='added' if not old else 'rejected_running_reference' if key in RETRACT else 'opening_page_corrected' if old_page!=n else 'retained'
        record=dict(item_id=key,chapter=ch,kind=m[1].lower(),number=m[2],status='rejected' if key in RETRACT else 'accepted',change=changed,source=source,pdf_page=n,print_page=folio,
            previous_pdf_page=old_page,previous_status=old['status'] if old else '',layout_basis=basis,reading_orientation_deg=rot,
            source_bbox_pt=json.dumps(box,separators=(',',':')),caption_or_heading_first_line=text,proof=evidence,proof_cell=cell,
            corrected_parent=RETRACT.get(key,('',''))[0],editorial_note=RETRACT.get(key,('',''))[1])
        records.append(record)
        if changed!='retained' or key in ('SR.C47.FIGURE3','SR.C41.TABLE2','SR.C47.TABLE1C'):
            changes.append(record)
    emit('objects.csv',records);emit('changes.csv',changes)
    scope=[{'chapter':ch,'original_items':sum(int(k['chapter'])==ch for k in OLD.values()),'new_or_revised_total':len([q for q in records if q['chapter']==ch and q['status']=='accepted']),'accepted_previous_candidate':sum(q['chapter']==ch and q['status']=='accepted' and q['previous_status']=='pdf_caption_candidate' for q in records),'rejected_previous_candidate':sum(q['chapter']==ch and q['status']=='rejected' for q in records),'added_appendices':sum(q['chapter']==ch and q['change']=='added' for q in records),'locator_page_changes':sum(q['chapter']==ch and q['change']=='opening_page_corrected' for q in records)} for ch in CH]
    emit('chapter_coverage.csv',scope)
    supplement()
    return records
if __name__=='__main__':
    rows=review();print(collections.Counter(r['change'] for r in rows),collections.Counter(r['status'] for r in rows))
