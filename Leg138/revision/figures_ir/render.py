"""Redraw the eleven Leg 138 interstitial-water suites from the published numerical records."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import re
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WATER = ROOT / 'disc/core/edition2'
LAYOUT = HERE / 'plot_layout.json'


def rows(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def write_rows(path, records):
    buf = io.StringIO(newline='')
    writer = csv.DictWriter(buf, fieldnames=list(records[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(records)
    data = buf.getvalue().encode('utf-8')
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def point_records(layout, water, depth844, hole848, hole852, table):
    points = []
    for panel in layout['panels']:
        for row in water:
            if int(row['directory_site']) != layout['site']:
                continue
            line = row['source_line']
            depth = depth844.get(line, row['depth_mbsf']) if layout['site'] == 844 else row['depth_mbsf']
            hole = row['hole']
            if layout['site'] == 848:
                hole = hole848[line][-1]
            elif layout['site'] == 852:
                hole = hole852.get(line, hole)
            key_hole = str(layout['site']) + hole
            if layout['site'] == 846 and hole == 'B':
                key_hole = '846C'
            if layout['item_id'] == 'IR09.F30' and hole == 'B':
                key_hole = '884B'
            # The 845 caption reverses the usual open/filled assignment.
            if layout['site'] == 845:
                marker = 'open_circle' if hole == 'C' else 'filled_circle'
            elif layout['site'] == 852 and hole == 'C':
                marker = 'open_square'
            else:
                marker = 'open_circle' if hole == 'A' else 'filled_circle'
            value = row[panel['field']]
            try:
                plotted = float(value)
            except ValueError:
                plotted = None
            points.append(dict(item_id=layout['item_id'], panel=panel['letter'], field=panel['field'],
                         chem_file=row['source_file'], chem_line=line, core=row['core'], section=row['section'],
                         sample_prefix=row['native_sample_prefix'], table=table, chem_hole=row['hole'], plot_hole=hole, figure_caption_symbol_hole=key_hole,
                         chem_depth_literal=row['depth_mbsf'], plot_depth_literal=depth,
                         chem_value_literal=value, marker=marker, status='plotted_numeric' if plotted is not None else
                         ('censored_not_plotted' if '<' in value else 'source_missing_not_plotted')))
    return points


def project(panel, layout, row):
    left, top, right, bottom = panel['source_frame_950x1240']
    value = float(row['chem_value_literal'])
    depth = float(row['plot_depth_literal'])
    return (left + (right-left)*(value-panel['x_min'])/(panel['x_max']-panel['x_min']),
            top + (bottom-top)*depth/layout['y_max'])


def draw(path, layout, points):
    panels = layout['panels']
    left = min(panels[0]['source_frame_950x1240'][0] - 49, min(line[0] for line in layout['caption_geometry'])) - 4
    top = min(p['letter_origin'][1] for p in panels) - 19
    right = panels[-1]['source_frame_950x1240'][2] + 14
    bottom = max(p['source_frame_950x1240'][3] for p in panels)
    caption = layout['caption']
    # Preserve line breaks from the witness. Lettered panel references are bold in print.
    cap_font_size = 12
    def fragments(line):
        return [(s, 'Times-Bold' if re.fullmatch(r'(?:[A-D]\.|Figure [0-9]+\.)', s) else 'Times-Roman')
                for s in re.split(r'(Figure [0-9]+\.|\b[A-D]\.)', line) if s]
    width = max(right, max(line[0]+line[2]+3 for line in layout['caption_geometry'])) - left
    height = layout['caption_geometry'][-1][1] - top + 7
    scale = 0.63
    c = canvas.Canvas(str(path), pagesize=(width*scale, height*scale), pageCompression=1, invariant=1)
    c.setCreator('Leg 138 digital edition');c.setTitle(layout['item_id']+' — Interstitial-water geochemistry')
    c.setSubject('Numerical reconstruction using reported shipboard chemistry and original plate scales.')
    c.scale(scale, scale)
    def x(v):
        return v-left
    def y(v):
        return height-(v-top)
    for panel in panels:
        l,t,r,b = panel['source_frame_950x1240']
        xlo,xhi,dx = panel['x_min'],panel['x_max'],panel['tick_interval']
        dy = layout['y_step']
        def xat(v):
            return x(l+(r-l)*(v-xlo)/(xhi-xlo))
        def yat(v):
            return y(t+(b-t)*v/layout['y_max'])
        c.setStrokeColorRGB(0.12,0.12,0.12)
        c.setFillColorRGB(0.08,0.08,0.08)
        c.setLineWidth(1.15)
        c.rect(x(l),y(b),r-l,b-t)
        for it in range(round((xhi-xlo)/(dx/2))+1):
            v=xlo+it*dx/2
            if v>xhi+1e-6:
                break
            tx=xat(v)
            major = it % 2 == 0
            if it and v < xhi:
                size=7 if major else 4
                c.setLineWidth(0.85)
                c.line(tx,y(t),tx,y(t)-size);c.line(tx,y(b),tx,y(b)+size)
            if major and (panel['label_endpoints'] or xlo < v < xhi):
                label=f'{v:g}'
                if panel['field']=='alkalinity' and layout['site'] in (853,854):
                    label=f'{v:.1f}'
                if layout['item_id']=='IR16.F31' and panel['field'] in ('strontium','ammonia') and v==0:
                    label='8'
                c.setFont('Helvetica',12)
                if it==0:
                    c.drawString(tx-1,y(t)+5,label)
                elif abs(v-xhi)<1e-6:
                    c.drawRightString(tx+1,y(t)+5,label)
                else:
                    c.drawCentredString(tx,y(t)+5,label)
        minor_divisor=5 if layout['site'] in (845,846,847,848,851) else 2
        for it in range(round(layout['y_max']/dy)*minor_divisor+1):
            v=dy*it/minor_divisor
            major=it%minor_divisor==0
            if 0<v<layout['y_max']:
                size=8 if major else 4
                c.line(x(l),yat(v),x(l)+size,yat(v));c.line(x(r),yat(v),x(r)-size,yat(v))
            if major and panel['letter']=='A':
                c.setFont('Helvetica',12);c.drawRightString(x(l)-5,yat(v)-4,f'{v:g}')
        c.setFont('Helvetica',13);c.drawCentredString(x((l+r)/2),y(panel['heading_baseline']),f"{panel['field'].title()} ({panel['unit']})")
        c.setFont('Helvetica-Bold',14)
        lx, ly = panel['letter_origin']
        c.drawString(x(lx), y(ly), panel['letter'])
        if panel['letter']=='A':
            c.saveState();c.translate(x(l)-40,y((t+b)/2));c.rotate(90)
            c.setFont('Helvetica',13);c.drawCentredString(0,0,'Depth (mbsf)');c.restoreState()
        data=[p for p in points if p['panel']==panel['letter'] and p['status']=='plotted_numeric']
        data.sort(key=lambda d: float(d['plot_depth_literal']))
        radius=layout['symbol_diameter']/2
        coords=[project(panel,layout,p) for p in data]
        c.setLineWidth(1.15)
        if coords:
            line=c.beginPath();line.moveTo(x(coords[0][0]), y(coords[0][1]))
            for px,py in coords[1:]:
                line.lineTo(x(px),y(py))
            c.drawPath(line)
        for (px,py),point in zip(coords,data):
            shade=0.09 if point['marker']=='filled_circle' else 1
            c.setFillColorRGB(shade,shade,shade)
            if point['marker']=='open_square':
                c.rect(x(px)-radius,y(py)-radius,radius*2,radius*2,fill=1)
            else:
                c.circle(x(px),y(py),radius,fill=1)
    c.setFillColorRGB(0.08,0.08,0.08)
    for j,line in enumerate(caption):
        lx, ly, printed_width = layout['caption_geometry'][j]
        text=c.beginText(x(lx), y(ly))
        width = sum(stringWidth(s,font,cap_font_size) for s,font in fragments(line))
        text.setHorizScale(100*printed_width/width)
        for s,font in fragments(line):
            text.setFont(font,cap_font_size);text.textOut(s)
        c.drawText(text)
    c.showPage();c.save()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=HERE)
    args=parser.parse_args()
    out=args.out; (out/'plots').mkdir(parents=True,exist_ok=True)
    layouts=json.loads(LAYOUT.read_text())
    water=rows(WATER/'water.csv.gz')
    depth844={r['chem_line']:r['print_depth'] for r in rows(WATER/'water_print_depths844.csv')}
    hole848={r['chem_line']:r['print_hole_context'] for r in rows(WATER/'water_print_only848.csv')}
    hole852={r['chem_line']:r['printed_hole'] for r in rows(HERE/'hole_variants852.csv')}
    water_sources={r['source_file']:r for r in rows(WATER/'water_sources.csv')}
    table_ids={int(r['site']):r['table'] for r in rows(WATER/'water_distribution_compare.csv')}
    tables={r['item_id']:r for r in rows(ROOT/'ir/core/native_tables.csv')}
    all_points=[];manifest=[]
    for layout in layouts:
        site=layout['site'];item=layout['item_id'];native=f'SITE_{site}/CHEM/INTERSTI.{site}'
        table_id=table_ids[site];table=tables[table_id]
        points=point_records(layout,water,depth844,hole848,hole852,table_id)
        all_points.extend(points)
        output=out/'plots'/f'{item}.pdf'
        draw(output,layout,points)
        qualifier=[]
        extra=[]
        if site==844:
            qualifier.append('12 truncated CHEM depths replaced for display by concordant printed/IR-table depths');extra.append('disc/core/edition2/water_print_depths844.csv')
        if item=='IR09.F30':
            qualifier.append('print caption gives 884B; table gives 844B')
        if site==846:
            qualifier.append('solid markers retain the 846C print caption key; 15 corresponding CHEM and T9 body samples are 846B')
        if item=='IR11.F25':
            qualifier.append('sodium is calculated by charge balance per IR p.297')
        if site==852:
            qualifier.append('five CHEM A samples plotted with B symbols per printed T12 grouping on p.997')
            extra.append('revision/figures_ir/hole_variants852.csv')
        if item=='IR14.F24':
            qualifier.append('chloride B profile is shifted about +3 mM in the print vs. the native numbers; the native series is plotted')
        if item=='IR17.F27':
            qualifier.append('deepest Li and Sr symbols sit shallower on the print than the 119.0 mbsf table coordinate')
        if item=='IR18.F23':
            qualifier.append('first silica point from the table is 451 µM; the open print marker is near 525 µM')
        if site==848:
            qualifier.append('symbols follow print hole grouping; 6 electronic A assignments retained alongside printed B');extra.append('disc/core/edition2/water_print_only848.csv')
        if item=='IR15.F29':
            qualifier.append('printed sodium axis unit µM is retained; source table gives mM; numeric scale is unchanged')
        if item=='IR16.F31':
            qualifier.append('left-end print glyph reads 8 on Sr and ammonia, reproduced at the axis origin; calibrated ticks imply origin 0')
        censored=sum(p['status']=='censored_not_plotted' for p in points)
        missing=sum(p['status']=='source_missing_not_plotted' for p in points)
        if censored:
            qualifier.append(f'{censored} below-limit values have no exact numeric ordinate; omitted from plot, retained in point ledger')
        if missing:
            qualifier.append(f'{missing} unpublished numeric values omitted; line joins successive available samples')
        manifest.append(dict(item_id=item,source_page=layout['source_page'],source_kind='shipboard CHEM and IR tables',
                    inputs='|'.join(['disc/primary/'+native,'ir/primary/'+table['source_path'],'disc/core/edition2/water.csv.gz']+extra),
                    table_ids=table_id,renderer='revision/figures_ir/render.py',output=f'revision/figures_ir/plots/{item}.pdf',
                    redraw_extent='all quantitative panels; censored marks omitted' if censored else 'all quantitative panels',
                    qualification='; '.join(qualifier) or 'Published numerical observations on the printed axes; connecting lines follow depth order.',
                    site=site,fields='|'.join(p['field'] for p in layout['panels']),chem_sha256=water_sources[native]['sha256'],
                    ir_table_sha256=table['sha256'],source_pdf_sha256=layout['source_sha256'],pdf_sha256=digest(output),
                    numeric_marks=len(points)-censored-missing,censored=censored,missing=missing))
    write_rows(out/'points.csv.gz',all_points)
    write_rows(out/'manifest.csv',manifest)


if __name__=='__main__':
    main()
