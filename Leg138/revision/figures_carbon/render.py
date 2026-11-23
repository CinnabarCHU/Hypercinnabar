"""Rebuild published downhole carbon records from the Leg 138 field tables."""
import argparse
import collections
import csv
import gzip
import hashlib
import io
import json
import re
from pathlib import Path

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TABLES = ROOT / 'ir/core/tables/carbons.csv'
ORGANIC = ROOT / 'data/carbon_reported.csv'
LAYOUTS = HERE / 'plot_layout.json'


def read(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write(path, records):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, records[0].keys(), lineterminator='\n')
    writer.writeheader()
    writer.writerows(records)
    data = stream.getvalue().encode()
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix=='.gz' else data)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def style(site, hole, organic):
    if site==844:
        return dict(A='triangle_right',B='cross',C='open_circle',D='square')[hole[-1]]
    if site==847 and hole.endswith('A') or site==848 and hole.endswith('D'):
        return 'open_circle'
    if site==850:
        return 'cross' if hole.endswith('A') else 'line'
    if site==854 or site==852 and organic:
        return 'dot'
    return 'cross' if organic else 'line'


def values_for(fig, records, organic, subset851):
    points=[]
    for panel in fig['panels']:
        field=panel['field']
        for row in records:
            site=int(row['site'])
            if site!=fig['site']:
                continue
            key=(row['item_id'],row['source_line'])
            is_org=field=='organic_c_pct'
            record=organic.get(key,{}) if is_org else {}
            value=record.get('organic_c_pct','') if is_org else row[field]
            role=record.get('footnote_role','')
            associated_role=organic.get(key,{}).get('footnote_role','')
            state='plotted'
            if not value:
                state='missing'
            elif site==852 and role=='late_addition_excluded_from_other_tables_figures_statistics':
                state='excluded_explicit_table_note'
            elif not is_org and site==852 and associated_role=='late_addition_excluded_from_other_tables_figures_statistics':
                state='excluded_graphic_subset_inference'
                role='carbonate_from_sample_with_late_organic_addition'
            elif is_org and site==851 and row['source_line'] not in subset851:
                state='excluded_graphic_subset_inference'
            elif float(value)<0 or float(value)>panel['x_max']:
                state='outside_printed_axis'
            points.append(dict(item_id=fig['item_id'],field=field,ir_table=row['item_id'],
                               table_path=row['source_path'],source_line=row['source_line'],hole=row['reported_hole'],
                               sample=row['sample_label'],depth_mbsf=row['depth_mbsf'],depth_mcd=row['depth_mcd'],
                               published_token=record.get('published_organic_c',row[field]),value=value,
                               footnote_role=role,selection=state,symbol=style(site,row['reported_hole'],is_org)))
    return points


def project(fig,panel,row):
    l,t,r,b=panel['frame']
    return l+(r-l)*float(row['value'])/panel['x_max'], t+(b-t)*float(row['depth_mbsf'])/fig['depth_max']


def text_parts(text,font,size):
    for part in re.split('(₃|Corg)',text):
        if part=='₃':
            yield '3',size*.72,-.24*size
        elif part=='Corg':
            yield 'C',size,0
            yield 'org',size*.7,-.20*size
        elif part:
            yield part,size,0


def lettering(c, text, font, size, x, y, centered=False, width=None):
    parts=list(text_parts(text,font,size))
    natural=sum(stringWidth(s,font,z) for s,z,k in parts)
    left=x-natural/2 if centered else x
    ob=c.beginText(left,y)
    if width:
        ob.setHorizScale(100*width/natural)
    for s,z,shift in parts:
        ob.setRise(shift)
        ob.setFont(font,z)
        ob.textOut(s)
    c.drawText(ob)


def plot(out, fig, points):
    panels=fig['panels']
    left=min(panels[0]['frame'][0]-51,*(a['x']-3 for a in fig['caption']))
    top=min(p['frame'][1] for p in panels)-42
    right=max(panels[-1]['frame'][2]+9,*(a['x']+a['width']+3 for a in fig['caption']))
    bottom=fig['caption'][-1]['baseline_y']+7
    X=lambda a:a-left
    Y=lambda a:bottom-a
    scale=.63
    c=Canvas(str(out),pagesize=((right-left)*scale,(bottom-top)*scale),invariant=1,pageCompression=1)
    c.setTitle(fig['item_id']+' — Downhole carbon records')
    c.setCreator('Leg 138 digital edition')
    c.scale(scale,scale)
    for panel in panels:
        l,t,r,b=panel['frame']
        c.setStrokeColorRGB(.1,.1,.1)
        c.setFillColorRGB(.08,.08,.08)
        c.setLineWidth(1.1)
        c.rect(X(l),Y(b),r-l,b-t)
        n=int(round(fig['depth_max']/fig['depth_tick']))
        for i in range(5*n+1):
            v=i/5*fig['depth_tick']
            y=Y(t+(b-t)*v/fig['depth_max'])
            if 0<i<5*n:
                tick=9 if i%5==0 else 5
                c.setLineWidth(.85)
                c.line(X(l),y,X(l)+tick,y)
                c.line(X(r),y,X(r)-tick,y)
            if i%5==0 and panel==panels[0]:
                c.setFont('Helvetica',12)
                c.drawRightString(X(l)-5,y-4,f'{v:g}')
        n=int(panel['x_max']/panel['tick']+1e-6)
        for i in range(n+1):
            v=i*panel['tick']
            x=X(l+(r-l)*v/panel['x_max'])
            if i>0 and v<panel['x_max']-1e-6:
                c.line(x,Y(t),x,Y(t)-8)
                c.line(x,Y(b),x,Y(b)+8)
            # At Site 848 the far-end 100% and 0.5% ticks have no labels.
            if fig['site']==848 and abs(v-panel['x_max'])<1e-7:
                continue
            c.setFont('Helvetica',12)
            if v==0:
                c.drawString(x-1,Y(t)+5,'0')
            elif abs(v-panel['x_max'])<1e-7:
                c.drawRightString(x+1,Y(t)+5,f'{v:g}')
            else:
                c.drawCentredString(x,Y(t)+5,f'{v:g}')
        lettering(c,panel['heading'],'Helvetica',13,X((r+l)/2),Y(t)+23,centered=True)
        if panel==panels[0]:
            c.saveState()
            c.translate(X(l)-41,Y((t+b)/2))
            c.rotate(90)
            c.setFont('Helvetica',13)
            c.drawCentredString(0,0,'Depth (mbsf)')
            c.restoreState()
        # Curves are clipped to the original frame, including negative values and >x-max samples.
        c.saveState()
        clipping=c.beginPath()
        clipping.rect(X(l),Y(b),r-l,b-t)
        c.clipPath(clipping,stroke=0,fill=0)
        grouped=collections.defaultdict(list)
        for pt in points:
            if pt['field']==panel['field']:
                grouped[pt['hole']].append(pt)
        for hole, group in sorted(grouped.items()):
            group.sort(key=lambda s:(float(s['depth_mbsf']),int(s['source_line'])))
            valid=[p for p in group if p['selection'] in ('plotted','outside_printed_axis')]
            if not valid:
                continue
            coords=[project(fig,panel,p) for p in valid]
            symbol=valid[0]['symbol']
            c.setLineWidth(1)
            if symbol!='open_circle':
                line=c.beginPath()
                previous=False
                for point in group:
                    if point['selection'] not in ('plotted','outside_printed_axis'):
                        if fig['site']==844 and panel['field']=='organic_c_pct':
                            previous=False
                        continue
                    px,py=project(fig,panel,point)
                    if previous:
                        line.lineTo(X(px),Y(py))
                    else:
                        line.moveTo(X(px),Y(py))
                    previous=True
                c.drawPath(line)
            for px,py in coords:
                x,y=X(px),Y(py)
                c.setFillColorRGB(.1,.1,.1)
                if symbol=='cross':
                    c.line(x-3.5,y,x+3.5,y)
                    c.line(x,y-3.5,x,y+3.5)
                elif symbol=='dot':
                    c.circle(x,y,2.8,fill=1)
                elif symbol=='square':
                    c.rect(x-3,y-3,6,6,fill=1)
                elif symbol=='triangle_right':
                    q=c.beginPath()
                    q.moveTo(x-4,y-4)
                    q.lineTo(x+4,y)
                    q.lineTo(x-4,y+4)
                    q.close()
                    c.drawPath(q,fill=1)
                elif symbol=='open_circle':
                    c.setFillColorRGB(1,1,1)
                    c.circle(x,y,3.4,fill=1)
        c.restoreState()
    for line in fig['caption']:
        lettering(c,line['text'],'Times-Roman',12,X(line['x']),Y(line['baseline_y']),width=line['width'])
    c.showPage()
    c.save()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=HERE)
    args=parser.parse_args()
    out=args.out
    (out/'plots').mkdir(parents=True,exist_ok=True)
    tables=read(TABLES)
    org={(r['source_item'],r['source_line']):r for r in read(ORGANIC)}
    native={r['item_id']:r for r in read(ROOT/'ir/core/native_tables.csv')}
    subset851={r['source_line'] for r in read(HERE/'figure33_organic_subset851.csv')}
    layouts=json.loads(LAYOUTS.read_text())
    all_points=[]
    manifests=[]
    for f in layouts:
        site=f['site']; item=f['item_id']
        points=values_for(f,tables,org,subset851)
        outpdf=out/'plots'/f'{item}.pdf'
        plot(outpdf,f,points)
        all_points.extend(points)
        tablekey=points[0]['ir_table']
        source=native[tablekey]
        extent='all published panels'
        comments={844:'Symbols distinguish four holes. Interpolating strokes are within-hole, sorted by ODP depth.',
            846:'The Corg axis clips values above 2%; the published zero values remain at the frame.',
            847:'The negative reported organic-carbon datum is retained and clipped to the original axis.',
            848:'Hole D carbonate has open circles. The organic track includes the residues marked a.',
            850:'Crosses identify Hole A. Hole B is drawn with a line.',
            851:'Organic-carbon subset inferred from print symbols and core-section positions. Table 12 lacks an explicit per-row selection.',
            852:'33 late Corg additions excluded per T13 note a; the corresponding 33 carbonate points are also omitted based on a two-way print/curve comparison. Eleven Corg values remain.',
            853:'At 6.83 mbsf the tabulated 0.009% disagrees with the print point near 0.09%; original numeric value retained.',
            854:'Only carbonate published in Figure 25. No organic-carbon panel is added.'}
        if site==852:
            extent='both panels; carbonate subset inferred from print comparison'
        if site==851:
            extent='carbonate panel; organic-carbon panel with inferred source-row selection'
        inp=['ir/primary/'+source['source_path'],'ir/core/tables/carbons.csv','data/carbon_reported.csv']
        if site==851:
            inp.append('revision/figures_carbon/figure33_organic_subset851.csv')
        counts=collections.Counter(r['selection'] for r in points)
        manifests.append(dict(item_id=item,source_page=f['source_page'],source_kind='IR published numerical table',
            inputs='|'.join(inp),table_ids=tablekey,renderer='revision/figures_carbon/render.py',
            output=f'revision/figures_carbon/plots/{item}.pdf',redraw_extent=extent,qualification=comments.get(site,'Downhole native table rows on the original depth and percentage scales.'),
            site=site,ir_table_sha256=source['sha256'],source_pdf_sha256=f['source_sha256'],pdf_sha256=digest(outpdf),
            plotted_within_frame=counts['plotted'],clipped_by_frame=counts['outside_printed_axis'],
            excluded_explicit=counts['excluded_explicit_table_note'],excluded_inferred=counts['excluded_graphic_subset_inference'],
            missing_fields=counts['missing']))
    write(out/'points.csv.gz',all_points)
    write(out/'manifest.csv',manifests)


if __name__=='__main__':
    main()
