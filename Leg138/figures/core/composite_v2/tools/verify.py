"""Validate reference hashes, vector resources and graphic-stage declarations."""
from pathlib import Path
from collections import Counter
import argparse,csv,hashlib,json
import fitz
from collect_tracks import ROOT,DATA

def read(name):
    with (DATA/name).open(newline='') as f:return list(csv.DictReader(f))

def run(disc,pr):
    src=read('source_tracks.csv');regs=read('panel_regions.csv');lays=read('figure_layers.csv');index=read('figure_index.csv')
    seen={}
    for s in src:
        if s['source_path'] not in seen:seen[s['source_path']]=hashlib.sha256((disc/s['source_path']).read_bytes()).hexdigest()
        assert seen[s['source_path']]==s['source_sha256'],s['source_path']
    sha=hashlib.sha256(pr.read_bytes()).hexdigest();assert all(r['source_pdf_sha256']==sha for r in regs)
    keys={(r['site'],r['source_page'],r['panel']) for r in regs}
    assert len(keys)==len(regs)==66 and len(index)==22
    assert keys=={(r['site'],r['pdf_page'],r['panel']) for r in lays}
    assert {int(r['site']) for r in index}==set(range(844,855))
    assert all(r['historical_20_point_filter_reproduced']=='no' for r in lays)
    assert sum(int(r['curves']) for r in lays)==110
    assert len(read('scan_trace_checks.csv'))==len(read('alternative_scale_checks.csv'))==44
    assert len(read('retained_layers.csv'))==55
    with fitz.open(ROOT/'Leg138_PR_Composite_Atlas.pdf') as atlas:
        assert len(atlas)==22
        for a,p in zip(index,atlas):
            assert 'Site '+a['site'] in p.get_text() and a['published_source_sha256']==sha
            with fitz.open(ROOT/a['vector_overlay']) as v:assert len(v)==1
    count=Counter()
    for row in read('site_series.csv'):count[row['quantity']]+=int(row['rows'])
    record=dict(stations=11,published_figures=11,source_figure_pages=22,independent_physical_panels=66,
                vector_traces=110,source_row_counts=dict(count),source_files_hashed=len(seen),retained_interpretive_and_axis_layers=55,
                proven_PR_twenty_point_filter_reproductions=0,printed_single_track_comparisons=44,
                panel_geometry='printed tick calibration and original page coordinates',
                reference_source_sha256=sha,atlas_sha256=hashlib.sha256((ROOT/'Leg138_PR_Composite_Atlas.pdf').read_bytes()).hexdigest())
    (ROOT/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('disc_primary',type=Path);ap.add_argument('pr_pdf',type=Path);a=ap.parse_args();run(a.disc_primary,a.pr_pdf)
