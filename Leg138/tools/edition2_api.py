"""Read-only critical-edition endpoints. Value views and source witnesses stay distinct."""
import json
from catalog_edition2 import site_tags

NAMES={'ir-tables','item-rows','print-cells','sr-objects','sr-apparatus','roi','rotation-stages','geography','sr-tables','sr-table-segments','sr-table-cells','sr-table-rows'}
def matches_site(row,site):
    return not site or '|'+site+'|' in site_tags(row)
def find_named(db,item,site,limit,offset):
    if not item:raise ValueError('item is required')
    review=db.execute('SELECT * FROM ir_table_review WHERE item_id=?',(item,)).fetchone()
    if review is None:raise KeyError('Unknown IR table')
    sql="""SELECT row_no,reading_status,record_json FROM ir_named WHERE item_id=?
           AND (?='' OR instr(sites,?)>0) ORDER BY row_no LIMIT ? OFFSET ?"""
    result=[]
    source_info=db.execute('SELECT d.source_path,p.local_source,p.url FROM datasets d JOIN items i ON i.item_id=? JOIN documents p USING(doc_id) WHERE d.dataset_id=?',(item,review['default_dataset'])).fetchone()
    asset_cache={}
    for r in db.execute(sql,(item,site,'|'+site+'|',limit,offset)):
        row=json.loads(r['record_json'])
        raw_path=row.get('source_path') or source_info['source_path'] or source_info['local_source']
        candidate=raw_path if raw_path.startswith('ir/') else 'ir/primary/'+raw_path
        if candidate not in asset_cache:
            a=db.execute('SELECT local_path,url,sha256 FROM assets WHERE local_path=?',(candidate,)).fetchone()
            asset_cache[candidate]=dict(a) if a else None
        result.append({**row,'item_id':item,'dataset_id':review['default_dataset'],'row_no':r['row_no'],'reading_status':r['reading_status'],'source_representation':review['representation'],
                       'source_witness':asset_cache[candidate],'report_source':source_info['local_source'],'report_url':source_info['url']})
    return result
def retrieve(db,name,q,limit,offset):
    site=q.get('site','');item=q.get('item','');chapter=q.get('chapter','')
    if name=='geography':return geographic(db,q,limit,offset)
    if name in ('sr-tables','sr-table-segments','sr-table-cells','sr-table-rows'):return sr_print(db,name,q,limit,offset)
    if name=='item-rows':return find_named(db,item,site,limit,offset)
    if name=='ir-tables':
        sql="""SELECT t.*,i.title,i.pdf_page,i.doc_id FROM ir_table_review t JOIN items i USING(item_id)
               WHERE (?='' OR t.item_id=?) AND (?='' OR t.site=? OR EXISTS(SELECT 1 FROM ir_named n WHERE n.item_id=t.item_id AND instr(n.sites,?)>0))
               AND (?='' OR i.doc_id=?) ORDER BY t.item_id LIMIT ? OFFSET ?"""
        doc=f'IR.C{int(chapter):02d}' if chapter else ''
        result=[]
        for r in db.execute(sql,(item,item,site,site,'|'+site+'|',chapter,doc,limit,offset)):
            data=dict(r);data['detail']=json.loads(data.pop('detail_json'))
            data['datasets']=[x[0] for x in db.execute('SELECT dataset_id FROM dataset_items WHERE item_id=? ORDER BY dataset_id',(r['item_id'],))]
            result.append(data)
        return result
    if name=='print-cells':
        if not item:raise ValueError('item is required')
        row=q.get('row','');field=q.get('field','');status=q.get('status','')
        sql="""SELECT c.record_json FROM ir_print_cells c JOIN ir_table_review t USING(item_id)
               WHERE c.item_id=? AND (?='' OR t.site=? OR EXISTS(SELECT 1 FROM ir_named n WHERE n.item_id=c.item_id AND n.row_no=c.row_no AND instr(n.sites,?)>0))
               AND (?='' OR c.row_no=?) AND (?='' OR c.field=?) AND (?='' OR c.status=?)
               ORDER BY c.row_no,c.field LIMIT ? OFFSET ?"""
        return [json.loads(r[0]) for r in db.execute(sql,(item,site,site,'|'+site+'|',row,row,field,field,status,status,limit,offset))]
    if name=='sr-objects':
        status=q.get('status','accepted');kind=q.get('kind','')
        if status not in ('accepted','rejected','all'):raise ValueError('status must be accepted, rejected or all')
        doc=f'SR.C{int(chapter):02d}' if chapter else ''
        sql="""SELECT r.detail_json,r.source_path,a.url,a.sha256 FROM item_reviews r JOIN items i USING(item_id) LEFT JOIN assets a ON a.local_path=r.source_path
               WHERE (?='all' OR r.state=?) AND (?='' OR r.item_id=?) AND (?='' OR i.doc_id=?) AND (?='' OR i.kind=?)
               AND (?='' OR EXISTS(SELECT 1 FROM evidence e WHERE e.item_id=r.item_id AND e.site=?)) ORDER BY r.item_id LIMIT ? OFFSET ?"""
        result=[]
        for row in db.execute(sql,(status,status,item,item,chapter,doc,kind,kind,site,site,limit,offset)):
            obj=json.loads(row[0])
            obj.update(source_path=row['source_path'],source_url=row['url'],source_sha256=row['sha256'],proof_path='sr/core/edition2/'+obj['proof'])
            result.append(obj)
        return result
    if name=='sr-apparatus':
        ds=q.get('dataset','');line=q.get('line','');ordinal=q.get('row','')
        sql="""SELECT a.record_json FROM sr_apparatus a JOIN sr_rows r ON (a.dataset_id=r.dataset_id AND a.record_no=r.record_no)
               WHERE (?='' OR a.dataset_id=?) AND (?='' OR a.line_first=?) AND (?='' OR a.record_no=?)
               AND (?='' OR instr(r.sites,?)>0) ORDER BY a.dataset_id,a.line_first LIMIT ? OFFSET ?"""
        return [json.loads(r[0]) for r in db.execute(sql,(ds,ds,line,line,ordinal,ordinal,site,'|'+site+'|',limit,offset))]
    if name=='roi':
        core=q.get('core','');roi=q.get('roi','');role=q.get('role','')
        sql="""SELECT record_json FROM optical_roi WHERE (?='' OR site=?) AND (?='' OR core_id=?)
               AND (?='' OR roi_id=?) AND (?='' OR role=?) ORDER BY site,core_id,roi_id LIMIT ? OFFSET ?"""
        return [json.loads(r[0]) for r in db.execute(sql,(site,site,core,core,roi,roi,role,role,limit,offset))]
    raise KeyError(name)

def geographic(db,q,limit,offset):
    import math
    site=q.get('site','');kind=q.get('kind','');status=q.get('status','');geometry=q.get('geometry','')
    if geometry not in ('','null','point'):raise ValueError('geometry must be null or point')
    text=q.get('age',q.get('age_Ma',''));age=float(text) if text!='' else None
    if age is not None and (not math.isfinite(age) or age<0):raise ValueError('age must be finite and nonnegative, in Ma')
    sql="""SELECT feature_json FROM geographic_features WHERE (?='' OR site=? OR (site IS NULL AND (chapter_site=? OR caption_site=?)))
           AND (? IS NULL OR age_ma=?) AND (?='' OR kind=?) AND (?='' OR position_status=?) AND (?='' OR has_geometry=?)
           ORDER BY kind,COALESCE(site,chapter_site),age_ma,feature_id LIMIT ? OFFSET ?"""
    return [json.loads(r[0]) for r in db.execute(sql,(site,site,site,site,age,age,kind,kind,status,status,geometry,int(geometry=='point'),limit,offset))]
def sr_print(db,name,q,limit,offset):
    key=q.get('item','');part=q.get('segment','');role=q.get('role','body');row=q.get('row','')
    if role not in ('header','body','all'):raise ValueError('role must be header, body or all')
    site=q.get('site','');requested_chapter=q.get('chapter','')
    if requested_chapter:
        chapter_doc=f'SR.C{int(requested_chapter):02d}'
    else:chapter_doc=''
    if name=='sr-tables':
        status=q.get('status','');review=q.get('review','')
        sql="""SELECT t.details FROM sr_print_review t JOIN items i USING(item_id) WHERE (?='' OR t.item_id=?) AND (?='' OR t.status=?)
            AND (?='' OR t.review=?) AND (?='' OR i.doc_id=?) AND (?='' OR EXISTS(SELECT 1 FROM evidence e WHERE e.item_id=t.item_id AND e.site=?))
            ORDER BY i.doc_id,i.pdf_page,t.item_id LIMIT ? OFFSET ?"""
        result=[]
        for selection in db.execute(sql,(key,key,status,status,review,review,chapter_doc,chapter_doc,site,site,limit,offset)):
            record=json.loads(selection[0])
            record['datasets']=[r[0] for r in db.execute('SELECT dataset_id FROM dataset_items WHERE item_id=? ORDER BY dataset_id',(record['item_id'],))]
            result.append(record)
        return result
    if not key:raise ValueError('item is required for SR print segments, rows or cells')
    if site and not db.execute('SELECT 1 FROM evidence WHERE site=? AND item_id=? LIMIT 1',(site,key)).fetchone():return []
    if name=='sr-table-segments':
        return [json.loads(r[0]) for r in db.execute('SELECT details FROM sr_segments WHERE item_id=? AND (?=\'\' OR segment=?) ORDER BY page,segment LIMIT ? OFFSET ?',(key,part,part,limit,offset))]
    cols="""SELECT c.record_json, h.field_header, h.status AS header_status, s.review, s.status AS segment_status,
                   a.local_path AS source_path, a.url AS source_url, a.sha256 AS source_sha256
            FROM sr_print_slots c JOIN sr_segments s ON c.segment=s.segment
            LEFT JOIN sr_slot_fields h ON h.segment=c.segment AND h.col=c.col
            LEFT JOIN assets a ON a.local_path='sr/primary/'||json_extract(s.details,'$.source')"""
    def decorate(rec):
        c=json.loads(rec[0]);c.update(header_candidate=rec['field_header'],header_status=rec['header_status'],segment_review=rec['review'],segment_status=rec['segment_status'],source_path=rec['source_path'],source_url=rec['source_url'],source_sha256=rec['source_sha256'])
        if site:c['site_filter_scope']='item_publication_evidence'
        return c
    if name=='sr-table-cells':
        col=q.get('col','')
        sql=cols+""" WHERE s.item_id=? AND (?='' OR s.segment=?) AND (?='all' OR c.role=?) AND (?='' OR c.row_no=?) AND (?='' OR c.col=?)
            ORDER BY s.page,s.segment,c.role,c.row_no,c.col LIMIT ? OFFSET ?"""
        return [decorate(r) for r in db.execute(sql,(key,part,part,role,role,row,row,col,col,limit,offset))]
    sql="""SELECT r.segment,r.role,r.row_no,s.page,s.review,s.status FROM sr_slot_rows r JOIN sr_segments s USING(segment) WHERE r.item_id=?
           AND (?='' OR r.segment=?) AND (?='all' OR r.role=?) AND (?='' OR r.row_no=?) ORDER BY s.page,r.segment,r.role,r.row_no LIMIT ? OFFSET ?"""
    result=[]
    for r in db.execute(sql,(key,part,part,role,role,row,row,limit,offset)):
        cells=[decorate(c) for c in db.execute(cols+' WHERE c.segment=? AND c.role=? AND c.row_no=? ORDER BY c.col',(r['segment'],r['role'],r['row_no']))]
        result.append(dict(item_id=key,segment=r['segment'],role=r['role'],row=r['row_no'],pdf_page=r['page'],segment_status=r['status'],segment_review=r['review'],cells=cells))
    return result
