"""Test the projected numerical positions against independently rendered IR page images."""
import argparse
import json
from pathlib import Path
from collections import Counter
import fitz
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
from render import HERE, LAYOUT, digest, project, rows, write_rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', type=Path, required=True, help='Root containing ir/primary/ and disc/primary/')
    p.add_argument('--out', type=Path, default=HERE)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    layouts=json.loads(LAYOUT.read_text())
    manifest={r['item_id']:r for r in rows(HERE/'manifest.csv')}
    all_points=rows(HERE/'points.csv.gz')
    summaries=[];checks=[]
    for spec in layouts:
        item=spec['item_id'];chapter=item[2:4];m=manifest[item]
        for path,sha in zip(m['inputs'].split('|')[:2],(m['chem_sha256'],m['ir_table_sha256'])):
            if digest(args.sources/path) != sha:
                raise ValueError('Changed numerical witness '+path)
        witness=args.sources/f'ir/primary/VOLUME/CHAPTERS/ir138_{chapter}.pdf'
        if digest(witness)!=spec['source_sha256']:
            raise ValueError('Changed print witness '+str(witness))
        with fitz.open(witness) as pdf:
            pix=pdf[spec['source_page']-1].get_pixmap(matrix=fitz.Matrix(1.55,1.55),colorspace=fitz.csGRAY)
        scan=np.asarray(Image.frombytes('L',(pix.width,pix.height),pix.samples).resize((950,1240)))
        # A white-centered marker can legitimately be several pixels from the nearest ink.
        # Axis ink can make this quantity artificially small. Label its edge cases explicitly.
        dist=distance_transform_edt(scan>=155)
        panels={a['letter']:a for a in spec['panels']}
        counts=Counter()
        for row in all_points:
            if row['item_id']!=item or row['status']!='plotted_numeric':
                continue
            panel=panels[row['panel']]
            x,y=project(panel,spec,row); l,t,r,b=panel['source_frame_950x1240']
            nearest=float(dist[round(y),round(x)])
            edge=min(x-l,r-x,y-t,b-y)<=8
            flag='edge_indeterminate' if edge else ('near_print_ink' if nearest<=5.0 else 'inspect_difference')
            counts[flag]+=1
            checks.append(dict(item_id=item,panel=row['panel'],field=row['field'],chem_line=row['chem_line'],
                               plot_x_950px=f'{x:.2f}',plot_y_1240px=f'{y:.2f}',
                               nearest_print_ink_px=f'{nearest:.2f}',geometry_check=flag))
        summaries.append(dict(item_id=item,source_page=spec['source_page'],panels=len(panels),
                              numeric_markers=int(m['numeric_marks']),edge_indeterminate=counts['edge_indeterminate'],
                              near_print_ink=counts['near_print_ink'],inspect_difference=counts['inspect_difference']))
    write_rows(args.out/'geometry_checks.csv.gz',checks)
    write_rows(args.out/'geometry_summary.csv',summaries)


if __name__=='__main__':
    main()
