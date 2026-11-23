"""Cross-check the public data tables and build per-site coverage for the second plate edition."""
import argparse
import csv
import gzip
import json
from collections import Counter
from pathlib import Path
from export_regions import BASE,rows


def run(data):
    photos=rows(data/'photos.csv');lanes=rows(data/'lanes.csv');rgn=rows(data/'regions.csv');qa=rows(data/'qa.csv')
    hdr=rows(data/'vcd_page_identities.csv');slide_rows=rows(data/'smear_rows.csv');pg=rows(data/'smear_grid_pages.csv')
    with gzip.open(data/'smear_cells.csv.gz','rt') as f:cells=list(csv.DictReader(f))
    versions=json.loads((data/'smear_verification.json').read_text());fingerprints=json.loads((data/'photo_verification.json').read_text())
    assert len(qa)==len({r['core_id'] for r in qa})==43
    assert all(r['form_id'] and r['photo_id'] for r in hdr)
    assert [r['site'] for r in hdr if r['form_id']!=r['photo_id']]==['845','846']
    assert len(slide_rows)==1156 and len(cells)==25194
    assert all(r['printed_page'] and r['sample_edition_literal'] and r['depth_edition_literal'] for r in slide_rows)
    assert all(r['lithology_edition_literal'] in {'D','M'} for r in slide_rows)
    pending=[r for r in cells if r['reading_evidence']=='source text layer and located cell' and (r['status'].startswith('check_') or r['status']=='ink_without_text')]
    stats=[]
    for site in sorted({p['site'] for p in photos}):
        local=[r for r in rgn if r['site']==site]
        stats.append(dict(site=site,photos=sum(r['site']==site for r in photos),
            visually_reviewed_overviews=sum(r['core_id'][:3]==site for r in qa),photographed_liners=sum(r['role']=='photographed_liner' for r in local),
            sediment_candidates=sum(r['role']=='sediment_candidate' for r in local),visually_excluded_bands=sum(r['role']=='reviewed_non_sediment_band' for r in local),
            vcd_pages=sum(r['site']==site for r in hdr),vcd_conflicting_labels=sum(r['site']==site and r['form_id']!=r['photo_id'] for r in hdr),
            smear_pages=sum(r['site']==site for r in pg),smear_rows=sum(r['site']==site for r in slide_rows),smear_cells=sum(r['site']==site for r in cells),
            visually_resolved_smear_cells=sum(r['site']==site and r['reading_evidence']!='source text layer and located cell' for r in cells),
            unresolved_smear_ocr_flags=sum(r['site']==site for r in pending)))
    with (data/'site_coverage.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,list(stats[0]));w.writeheader();w.writerows(stats)
    combined=dict(photo_checks=fingerprints,visual_photo_overviews=len(qa),smear=versions,
        smear_manually_checked_total=sum(r['reading_evidence']!='source text layer and located cell' for r in cells),
        smear_unreviewed_flag_queue=dict(Counter(r['status'] for r in pending)),smear_unreviewed_flagged_cells=len(pending),
        vcd_identity_evidence=dict(Counter(r['edition_two_evidence'] for r in hdr)))
    (data/'edition_verification.json').write_text(json.dumps(combined,indent=2)+'\n');print(len(stats),'sites',len(pending),'unreviewed OCR flags')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,default=BASE/'data')
    a=p.parse_args();run(a.data)
