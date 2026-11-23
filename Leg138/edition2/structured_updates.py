"""Attach native-field editions, print-cell audit trails, and the adjudicated SR object registry."""
from collections import defaultdict
import csv,gzip,json
from companions import read

STATUS={'visually_collated':'V','pdf_and_optical_agree':'A','blank_at_scan_threshold':'B',
        'vertical_label_in_separate_table':'S','readers_disagree':'?D','column_assignment_review':'?C',
        'pdf_layer_only':'?P','optical_only':'?O','ink_without_string':'?I'}
LEGEND='Cell marks: V visual collation; A PDF and optical readings agree; B blank at scan threshold; S separately recorded spanning label. Provisional OCR: ?D readers disagree; ?C column assignment under review; ?P PDF layer only; ?O optical reading only; ?I ink without a readable string. Open the companion cell-evidence CSV for both readings and coordinates.'
def value(row,key):
    status=row.get(key+'__status')
    return (row.get(key,'')+' ['+STATUS[status]+']').strip() if status else row.get(key,'')
def gzread(file):
    with gzip.open(file,'rt',encoding='utf-8-sig',newline='') as stream:return list(csv.DictReader(stream))
def attach(root,items,add):
    ir=root/'ir/core';sr=root/'sr/core/edition2';nd=ir/'edition2_native';pr=ir/'edition2_print/data'
    coverage={r['item_id']:r for r in read(nd/'coverage.csv')}
    for dataset in read(nd/'datasets.csv'):
        item=dataset['source_items'];anchor=items[item];record=coverage[item]
        file=ir/dataset['data_path'];rows=read(file)
        cols=['source_line']+json.loads(record['fields'])
        if any(row.get('verification_flags') for row in rows):cols.append('verification_flags')
        if any(row.get('unresolved_source_fragment') for row in rows) and 'unresolved_source_fragment' not in cols:cols.append('unresolved_source_fragment')
        add('IR.C'+anchor['chapter'].zfill(2),int(anchor['pdf_page'] or 0),item,'native named fields · '+record['family'],file,'table',columns=cols,
            representation='named_native',note='Published electronic rows, with native file line and named fields. '+record['flagged_lines']+' rows carry source or alignment flags.')
    by_item=defaultdict(list);by_cell=defaultdict(list)
    for row in gzread(pr/'print_rows.csv.gz'):by_item[row['item_id']].append(row)
    for cell in gzread(pr/'print_cells.csv.gz'):by_cell[cell['item_id']].append(cell)
    for ds in read(pr/'datasets.csv'):
        item=ds['item_id'];doc='IR.C'+ds['chapter'].zfill(2);pg=int(ds['pdf_pages'].split(',')[0])
        cross={(cell['pdf_page'],cell['print_row'],cell['field']):cell for cell in by_cell[item]}
        field_names=list(dict.fromkeys(c['field'] for c in by_cell[item]));rows=[]
        for row in by_item[item]:
            record={k:row[k] for k in ('item_id','pdf_page','printed_page','print_row','source_row_bbox_pt','row_kind','reading_status')}
            values=json.loads(row['cell_readings_json'])
            for k in field_names:
                cell=cross.get((row['pdf_page'],row['print_row'],k))
                record[k]=values.get(k,'')
                record[k+'__status']=cell['review_status'] if cell else ''
                if cell is not None:assert record[k]==cell['reading'],(item,k,record[k],cell['reading'])
            rows.append(record)
        note=ds['title_as_indexed']+' | '+str(ds['visually_collated_cells'])+' visually collated slots, '+ds['review_cells']+' provisional or ambiguous slots. '+LEGEND
        add(doc,pg,item,'printed named cells with review marks',pr/'print_rows.csv.gz','table',rows,
            ['pdf_page','print_row']+field_names,representation='print_cells',note=note)
        add(doc,pg,item,'cell evidence including coordinates and both readings',pr/'print_cells.csv.gz','csv',by_cell[item],
            representation='print_cell_evidence',note='Each row is a cell slot with its review status, both OCR witnesses, and the printed position.')
    for r in read(pr/'spanning_print_labels.csv'):
        item=r['item_id'];anchor=items[item];d='IR.C'+anchor['chapter'].zfill(2)
        if r==read(pr/'spanning_print_labels.csv')[0]:add(d,int(r['pdf_page']),item,'separate spanning labels',pr/'spanning_print_labels.csv','csv',representation='print_spanning_labels')
    for r in read(sr/'data/print_datasets.csv'):
        doc='SR.C'+r['chapter'].zfill(2);path=sr/r['file'];rows=read(path)
        cols=[k for k in rows[0] if k not in ('source_pdf_page','source_print_page','table_row','printed_row')]
        add(doc,int(r['pdf_page']),r['item_id'],'print transcription · '+r['role'],path,'table',columns=cols,
            representation='sr_reviewer_print',note=r['editorial_note'])
    chapters=defaultdict(list)
    for r in read(sr/'data/objects.csv'):chapters['SR.C'+r['chapter'].zfill(2)].append(r)
    for d,rr in chapters.items():
        accepted=sum(r['status']=='accepted' for r in rr)
        add(d,1,d,'object identity and opening-page decisions',sr/'data/objects.csv','csv',rr,
            representation='sr_object_register',locator='chapter_object_register',
            note=f'{accepted} accepted identities; {len(rr)-accepted} rejected IDs. Caption text and plot pixels have separate verification scopes.')
