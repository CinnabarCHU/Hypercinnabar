"""Bind the exact rate-panel render inputs and source code to each PR item page."""
from pathlib import Path
import argparse,json,shutil
from companions import read,write,digest
def publish(root,out):
    if not (out/'html/PR.html').is_file():return
    mod=root/'figures/core';target=out/'resources/rate_replay'
    for name in ('data','tools'):
        (target/name).mkdir(exist_ok=True,parents=True)
        for src in (mod/name).glob('*.csv' if name=='data' else '*.py'):
            shutil.copyfile(src,target/name/src.name)
    datahash=digest(target/'data/ir_mean_intervals.csv');codehash=digest(target/'tools/draw_atlas.py')
    station={r['site']:r for r in read(mod/'data/figure_index.csv')};assets=read(out/'resources.csv')
    html=out/'html/PR.html';display=html.read_text();lineage=[]
    for s,r in station.items():
        item='PR.F'+r['pr_figure'];pg=r['pr_pdf_page'];fig=next(a for a in assets if a['item_id']==item and a['kind']=='figure');svg=next(a for a in assets if a['item_id']==item and a['kind']=='svg')
        lineage.append(dict(site=s,item_id=item,source_pr_pdf_page=pg,ir_table=r['ir_mean_table'],figure_pdf=fig['file'],figure_pdf_sha256=fig['sha256'],figure_svg=svg['file'],figure_svg_sha256=svg['sha256'],matrix='resources/rate_replay/data/ir_mean_intervals.csv',matrix_sha256=datahash,renderer='resources/rate_replay/tools/draw_atlas.py',renderer_sha256=codehash,original_module='figures/core',editorial_note=r['editorial_note']))
        marker=f'<section id="p{pg}">';extra='<p class="meta"><a href="../resources/rate_replay/data/ir_mean_intervals.csv">Rate-panel source values and native line numbers</a> · <a href="../resources/rate_replay/tools/draw_atlas.py">Renderer</a> · <a href="../rate_plot_lineage.csv">Panel lineage</a></p>'
        if extra not in display.split(marker,1)[1].split('</section>',1)[0]:display=display.replace(marker,marker+extra,1)
    write(out/'rate_plot_lineage.csv',lineage);html.write_text(display)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('output',type=Path);a=p.parse_args();publish(a.root,a.output)
