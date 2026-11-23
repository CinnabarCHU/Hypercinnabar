"""Check figure package references, published source bytes, row counts and all eleven vector pages."""
from pathlib import Path
import argparse
import hashlib
import xml.etree.ElementTree as ET
import fitz
from check_rates import PR_SHA, read
from read_tables import ROOT

def verify(ir, pr):
    assert hashlib.sha256(pr.read_bytes()).hexdigest()==PR_SHA
    manifest=read('ir_interval_witnesses.csv')
    assert len(manifest)==22
    for row in manifest:
        content=(ir/row['distribution_path']).read_bytes()
        assert len(content)==int(row['bytes'])
        assert hashlib.sha256(content).hexdigest()==row['sha256'],row['source_url']
    intervals=read('ir_mean_intervals.csv')
    checks=read('pr_rate_check.csv')
    assert len(intervals)==len(checks)==230
    terminal=next(r for r in intervals if r['site']=='853' and r['values_source_line']=='59')
    assert (terminal['young_Ma'],terminal['old_Ma'],terminal['noncarbonate_mar'],terminal['organic_carbon_mar'])==('7.28','7.50','','0.14')
    assert len(read('pr_panel_axes.csv'))==54
    assert len(read('pr_printed_marks.csv'))==44
    assert len(read('pr_mar_spotcheck.csv'))==1
    summaries=read('pr_rate_summary.csv')
    assert [sum(int(r[k]) for r in summaries) for k in ('evaluated','within_tolerance','different_at_print_scale','unresolved')]==[127,123,4,103]
    index=read('figure_index.csv')
    assert [int(a['site']) for a in index]==list(range(844,855))
    with fitz.open(ROOT/'Leg138_PR_Rate_Atlas.pdf') as atlas:
        assert len(atlas)==len(index)
        for row,page in zip(index,atlas):
            svg=ROOT/row['svg']
            assert ET.parse(svg).getroot().tag.endswith('svg')
            assert 'Site '+row['site'] in page.get_text()
            with fitz.open(svg.with_suffix('.pdf')) as graphic:
                assert len(graphic)==1
    print('Verified 11 site pairs, 54 original axes, 22 primary tables, 230 intervals, 44 graphic marks and 1 MAR spot check.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('ir_primary',type=Path)
    p.add_argument('pr_pdf',type=Path)
    args=p.parse_args()
    verify(args.ir_primary,args.pr_pdf)
