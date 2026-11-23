"""Merge a visual second pass of all one-sided VCD header readings into the original per-page index."""
import argparse
import csv
import statistics
from pathlib import Path
import fitz
from export_regions import BASE,rows


def bounds(page,side):
    words=[w for w in page.get_text('words') if w[1]<115]
    anchors=[w for w in words if w[4].strip('!.,:[]').upper() in ('SITE','HOLE','CORED','CORE')]
    y=min(w[1] for w in anchors or words)
    if side=='form':
        hole=next((w for w in anchors if w[4].strip('!.,:[]').upper()=='HOLE'),None)
        left,right=(max(0,hole[0]-58),min(page.rect.width,hole[0]+85)) if hole else (152,338)
    else:left,right=432,568
    return [round(v,2) for v in (left,max(0,y-7),right,min(page.rect.height,y+20))]


def build(primary,data,out):
    first=rows(data/'vcd_pages.csv')
    review={(r['site'],r['pdf_page']):r for r in rows(out/'vcd_visual_readings.csv')}
    photos={r['core_id']:r['source_path'] for r in rows(data/'native_photo_catalog.csv')}
    result=[]
    for old in first:
        form=old['printed_form_core'];photo=old['printed_photo_core']
        key=(old['site'],old['pdf_page'])
        item=dict(site=key[0],pdf_page=key[1],source_path=old['source_path'],
                  edition_one_evidence=old['identity_evidence'],
                  edition_one_form_token=form,edition_one_photo_token=photo)
        reading=review.get(key)
        coords=['']*4
        if reading:
            side=reading['visually_checked_side']
            if side=='form':form=reading['transcription']
            else:photo=reading['transcription']
            with fitz.open(primary/old['source_path']) as doc:
                coords=bounds(doc[int(key[1])-1],side)
            evidence=reading['decision']
        else:evidence=old['identity_evidence']
        item.update(edition_two_evidence=evidence,form_id=form,photo_id=photo,
                    photo_file_by_photo_id=photos.get(photo,''),
                    separate_photo_candidate_by_form=photos.get(form,'') if form!=photo else '',
                    checked_side=reading['visually_checked_side'] if reading else '',
                    checked_left_pt=coords[0],checked_top_pt=coords[1],checked_right_pt=coords[2],checked_bottom_pt=coords[3],
                    note=reading['note'] if reading else '')
        result.append(item)
    with (out/'vcd_page_identities.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,list(result[0]));w.writeheader();w.writerows(result)
    print(len(review),'visually checked missing labels in',len(result),'pages')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path)
    p.add_argument('--catalog',type=Path,default=BASE.parent/'data');p.add_argument('--out',type=Path,default=BASE/'data')
    a=p.parse_args();build(a.primary,a.catalog,a.out)
