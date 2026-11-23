"""Audit out-of-sequence, numeric in-text references without manufacturing new publication objects."""
import gzip,csv,re
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def run():
    with (E/'data/objects.csv').open() as f:ids={q['item_id'] for q in csv.DictReader(f) if q['status']=='accepted'}
    with gzip.open(E/'data/reference_mentions.csv.gz','rt') as f:hits=list(csv.DictReader(f))
    rows=set()
    for r in hits:
        ch=int(r['chapter'])
        for number in [r['first'],r['second']]:
            if not number.isdigit():continue
            suggestion=f"SR.C{ch:02d}.{r['kind'].upper()}{int(number)}"
            if suggestion in ids:continue
            if ch in (1,23,34):kind='cross_publication_reference'
            elif ch in (8,11,20):kind='taxonomic_literature_or_plate_panel'
            elif ch==40:kind='named_panel_within_plate'
            elif ch==17 and number=='51':kind='OCR_panel_5I_in_paired_5I_5J'
            elif ch==47 and number=='1':kind='collective_reference_to_printed_Tables_1a_to_1d'
            else:kind='requires_inspection'
            rows.add((ch,r['kind'],number,int(r['pdf_page']),kind,r['context']))
    with (E/'data/excluded_reference_mentions.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['chapter','kind','referenced_number','pdf_page','reason','line_excerpt']);w.writerows(sorted(rows))
    print(len(rows))
if __name__=='__main__':run()
