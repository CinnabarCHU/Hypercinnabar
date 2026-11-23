"""Validate source hashes, table coverage, row/cell references, adjudications and selected print invariants."""
from collections import Counter,defaultdict
from pathlib import Path
import argparse,hashlib,json
import fitz
from build import DATA,ROOT,load

def verify(ir):
    catalog=load(DATA/'datasets.csv');regions=load(DATA/'regions.csv')
    rows=load(DATA/'print_rows.csv.gz');cells=load(DATA/'print_cells.csv.gz')
    baseline=load(ROOT.parent/'table_coverage.csv')
    wanted={d['item_id'] for d in baseline if d['native_online']=='0' and d['has_named_fields_in_ir_package']=='0'}
    assert wanted=={d['item_id'] for d in catalog} and len(wanted)==63
    slots={(r['item_id'],r['pdf_page']):r for r in regions}
    assert len(regions)==len(slots)==64
    counts=Counter(r['item_id'] for r in rows);cell_counts=Counter(r['item_id'] for r in cells)
    assert all(int(d['row_count'])==counts[d['item_id']] and int(d['cell_count'])==cell_counts[d['item_id']] for d in catalog)
    files={}
    for region in regions:
        path=ir/region['pdf_path']
        if path not in files:files[path]=hashlib.sha256(path.read_bytes()).hexdigest(),fitz.open(path)
        sha,doc=files[path];page=doc[int(region['pdf_page'])-1]
        assert sha==region['sha256'] and page.rect.contains(fitz.Rect(*map(float,region['body_bbox'].split(','))))
        assert region['caption_text_layer'] and region['header_text']
    rowmap={(r['item_id'],r['print_row']):r for r in rows};seen=set()
    registered={(r['item_id'],r['pdf_page'],r['field'],r['reading'],round(float(r['row_y_pt']),2))
                       for r in load(DATA/'manual_readings.csv')}
    used=set(); statuses=Counter(); byitem=defaultdict(Counter)
    for c in cells:
        item=c['item_id'];key=(item,c['print_row'],c['field']);assert key not in seen;seen.add(key)
        row=rowmap[(item,c['print_row'])]; assert row['pdf_page']==c['pdf_page'] and row['printed_page']==c['printed_page']
        vals=json.loads(row['cell_readings_json']);assert vals.get(c['field'],'')==c['reading']
        cell=fitz.Rect(*map(float,c['cell_bbox_pt'].split(',')));area=fitz.Rect(*map(float,slots[(item,c['pdf_page'])]['body_bbox'].split(',')))
        assert area.contains(cell) and cell.width>0 and cell.height>0,key
        status=c['review_status'];statuses[status]+=1;byitem[item][status]+=1
        if status=='visually_collated':
            matches=[v for v in registered if v[:4]==(item,c['pdf_page'],c['field'],c['reading']) and abs(v[4]-float(c['row_y_pt']))<1.6]
            assert len(matches)==1,key;used.add(matches[0])
    assert set(byitem)==wanted and all(x['visually_collated']>0 for x in byitem.values()) and registered==used
    # These complete publication bodies were manually collated. Some have blank or spanning slots.
    complete={'IR02.T02','IR07.T01','IR07.T02','IR09.T23','IR10.T25','IR10.T22','IR12.T22','IR13.T19','IR13.T25','IR14.T22','IR15.T25','IR16.T23','IR17.T03','IR17.T22','IR18.T18','IR19.T15'}
    for i in complete:
        assert set(byitem[i])<={'visually_collated','vertical_label_in_separate_table'},(i,byitem[i])
    pole=load(DATA/'pole_notes.csv');assert sum(counts[d['item_id']] for d in pole)==131
    for d in pole:
        reg=slots[(d['item_id'],d['pdf_page'])];assert reg['printed_page']==d['printed_page']
    assert len([r for r in rows if r['item_id']=='IR02.T02'])==44
    assert '851' in next(z['caption_text_layer'] for z in catalog if z['item_id']=='IR19.T15')
    pending={'readers_disagree','column_assignment_review','pdf_layer_only','ink_without_string','optical_only'}
    v=dict(table_ids=len(wanted),caption_regions=len(slots),physical_rows=len(rows),cell_slots=len(cells),status_counts=dict(statuses),
           manual_cells=len(used),pending_cells=sum(statuses[k] for k in pending),fully_manually_collated_print_bodies=sorted(complete),
           paleogeographic_print_rows=131,sources_sha256_verified=len(files))
    (ROOT/'verification.json').write_text(json.dumps(v,indent=2)+'\n')
    print(json.dumps(v,ensure_ascii=False))
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('ir_primary',type=Path);verify(ap.parse_args().ir_primary)
