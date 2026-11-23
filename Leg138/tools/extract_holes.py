"""Keep each published hole-header value and its PDF line coordinates, then check preliminary values."""
import argparse,csv,re
from pathlib import Path
from decimal import Decimal,InvalidOperation
from collections import Counter
import fitz
PREFIX={'Date occupied':'date_occupied','Date departed':'date_departed','Time on hole':'time_on_hole','Position':'position','Bottom felt':'bottom_felt_mbrf','Distance between rig floor and sea level':'rig_floor_above_sea_m','Water depth':'water_depth_sea_level_m','Total depth':'total_depth_mbrf','Penetration':'penetration_m','Number of core':'cores','Total length of cored section':'cored_m','Total core recov':'core_recovered_m','Core recovery':'core_recovery_pct'}
PAIRS={'bottom_felt_mbrf':'water_depth_m','penetration_m':'interval_drilled_m','cores':'cores','cored_m':'interval_cored_m','core_recovered_m':'core_recovered_m','core_recovery_pct':'core_recovery_pct'}
URL='https://www-odp.tamu.edu/publications/138_IR/VOLUME/CHAPTERS/'
def write(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def extract(root,out):
    records=[];holes_seen=set()
    for site in range(844,855):
        chapter=site-835;name=f'ir138_{chapter:02d}.pdf';path=root/'ir/primary/VOLUME/CHAPTERS'/name
        with fitz.open(path) as d:
            last=None;done=set()
            for n in [0,1]:
                page=d[n]
                lines=[]
                for b in page.get_text('dict')['blocks']:
                    for line in b.get('lines',[]):
                        x,y,r,s=line['bbox'];txt=''.join(sp['text'] for sp in line['spans']).strip()
                        lines.append((int((x+r)/2>=page.rect.width/2),y,x,r,s,txt))
                for _,y,x,r,s,t in sorted(lines,key=lambda l:(l[0],l[1],l[2])):
                    heading=re.fullmatch(rf'HOLE\s*({site}[A-E])',t,re.I)
                    if heading:last=heading[1].upper();holes_seen.add(last);continue
                    if not last or ':' not in t:continue
                    label,value=t.split(':',1)
                    field=next((v for k,v in PREFIX.items() if label.startswith(k)),None)
                    if not field or (last,field) in done:continue
                    done.add((last,field))
                    records.append(dict(site=str(site),hole=last,ir_chapter=chapter,field=field,printed_label=label,value_as_extracted=value.strip(),pdf_page=n+1,bbox_pt=' '.join(f'{i:.2f}' for i in (x,y,r,s)),url=URL+name+f'#page={n+1}',status='transcribed_from_official_text_layer'))
    assert len(holes_seen)==42,holes_seen
    write(out/'ir_hole_headers.csv',records)
    with (out/'pr_coring.csv').open() as f:
        pr={r['hole']:r for r in csv.DictReader(f) if r['row_kind']=='hole'}
    checks=[]
    for r in records:
        key=r['field']
        if key not in PAIRS:continue
        old=pr[r['hole']];a=old[PAIRS[key]];b=r['value_as_extracted']
        try: delta=Decimal(b)-Decimal(a)
        except InvalidOperation:delta=None
        checks.append(dict(site=r['site'],hole=r['hole'],ir_field=key,pr_field=PAIRS[key],pr_value=a,ir_value=b,ir_minus_pr='' if delta is None else str(delta),status='check_print' if delta is None else ('same_numeric_value' if delta==0 else 'different_printed_or_extracted_value'),pr_pdf_page=old['pdf_page'],ir_pdf_page=r['pdf_page'],ir_bbox_pt=r['bbox_pt']))
    write(out/'pr_ir_field_comparison.csv',checks)
    print(len(records),len(checks),Counter(r['ir_field'] for r in checks),Counter(r['status'] for r in checks))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('out',type=Path);a=p.parse_args();extract(a.root,a.out)
