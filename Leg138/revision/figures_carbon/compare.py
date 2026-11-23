"""Compare numerical vertices on original carbon figure frames to the scan."""
import argparse
import json
from collections import Counter
from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
from render import HERE, LAYOUTS, digest, project, read, write



def compare_carbonate_subsets(fig, panel, points, scan):
    # A bidirectional comparison distinguishes shorter curves from genuine improvements.
    ambiguous={p['source_line'] for p in points if p['item_id']==fig['item_id']
               and p['field']=='organic_c_pct' and p['selection'].startswith('excluded_')}
    all_numeric=[p for p in points if p['item_id']==fig['item_id'] and p['field']=='carbonate_pct' and p['value']]
    l,t,r,b=map(round,panel['frame'])
    interior=np.zeros(scan.shape,dtype=bool)
    interior[t+8:b-8,l+8:r-8]=True
    ink=scan<155
    evidence=[]
    for mode in ('all_numeric_rows','omit_carbonate_where_Corg_is_a_late_or_inferred_addition'):
        rows=sorted([p for p in all_numeric if mode=='all_numeric_rows' or p['source_line'] not in ambiguous],
                    key=lambda a:float(a['depth_mbsf']))
        frame=Image.new('L',(950,1240),0)
        ImageDraw.Draw(frame).line([tuple(map(round,project(fig,panel,p))) for p in rows],fill=255)
        drawn=np.asarray(frame)>0
        fwd=distance_transform_edt(~ink)[interior & drawn]
        rev=distance_transform_edt(~drawn)[interior & ink]
        evidence.append(dict(item_id=fig['item_id'],selection=mode,rows=len(rows),
                             mean_curve_to_scan_px=f'{fwd.mean():.4f}',mean_scan_to_curve_px=f'{rev.mean():.4f}',
                             max_curve_to_scan_px=f'{fwd.max():.4f}',scan_interior_ink_pixels=len(rev)))
    return evidence


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',required=True,type=Path)
    parser.add_argument('--out',type=Path,default=HERE)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    points=read(HERE/'points.csv.gz')
    manifest={r['item_id']:r for r in read(HERE/'manifest.csv')}
    comparisons=[]
    metrics=[]
    details=[]
    for fig in json.loads(LAYOUTS.read_text()):
        item=fig['item_id']
        m=manifest[item]
        table=args.sources / m['inputs'].split('|')[0]
        pdf=args.sources / f'ir/primary/VOLUME/CHAPTERS/ir138_{item[2:4]}.pdf'
        if digest(table)!=m['ir_table_sha256'] or digest(pdf)!=m['source_pdf_sha256']:
            raise ValueError('Source hash mismatch for '+item)
        with fitz.open(pdf) as d:
            px=d[fig['source_page']-1].get_pixmap(matrix=fitz.Matrix(1.55,1.55),colorspace=fitz.csGRAY)
        arr=np.asarray(Image.frombytes('L',(px.width,px.height),px.samples).resize((950,1240)))
        dist=distance_transform_edt(arr>=155)
        if fig['site'] in (851,852):
            comparisons.extend(compare_carbonate_subsets(fig,fig['panels'][0],points,arr))
        for panel in fig['panels']:
            l,t,r,b=panel['frame']
            counts=Counter()
            for row in points:
                if row['item_id']!=item or row['field']!=panel['field'] or not row['value']:
                    continue
                x,y=project(fig,panel,row)
                nearest=''
                if row['selection']!='plotted':
                    code=row['selection']
                else:
                    nearest=float(dist[round(y),round(x)])
                    border=min(x-l,r-x,y-t,b-y)
                    code='edge_indeterminate' if border<=8 else ('near_print_ink' if nearest<=5 else 'inspect_difference')
                counts[code]+=1
                details.append(dict(item_id=item,field=panel['field'],source_line=row['source_line'],depth_mbsf=row['depth_mbsf'],
                                    value=row['value'],page_x_950px=f'{x:.2f}',page_y_1240px=f'{y:.2f}',
                                    nearest_ink_px=f'{nearest:.2f}' if nearest!='' else '',geometry_check=code))
            metrics.append(dict(item_id=item,field=panel['field'],near_print_ink=counts['near_print_ink'],
                        inspect_difference=counts['inspect_difference'],edge_indeterminate=counts['edge_indeterminate'],
                        outside_printed_axis=counts['outside_printed_axis'],explicit_exclusions=counts['excluded_explicit_table_note'],
                        inferred_exclusions=counts['excluded_graphic_subset_inference']))
    write(args.out/'geometry_checks.csv.gz',details)
    write(args.out/'geometry_summary.csv',metrics)
    write(args.out/'carbonate_subset_comparison.csv',comparisons)


if __name__=='__main__':
    main()
