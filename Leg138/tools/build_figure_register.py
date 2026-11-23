"""Build the Leg 138 figure reproduction register from the published editorial evidence."""
import argparse
import csv
import gzip
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['item_id','series','doc_id','object_scope','site','title_or_caption','source_path','source_pdf_pages',
          'printed_pages','source_url','page_basis','status','redraw_extent','source_kind','table_ids',
          'inputs_or_related_witnesses','renderer','output','evidence_file','qualification']
DATA, TRACE, LEAD, PRINT = ('data_code_redraw','print_derived_partial_redraw','documented_source_lead','published_image_or_caption')
COMPOSITE={844:7,845:7,846:7,847:6,848:6,849:6,850:6,851:6,852:7,853:6,854:7}


def read(root, name):
    path = root/name
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path,'rt',encoding='utf-8',newline='') as stream:
        return list(csv.DictReader(stream))


def joined(values):
    return '|'.join(dict.fromkeys(str(x) for x in values if x!=''))


def add(row, field, *values):
    row[field] = joined([*row[field].split('|'),*values])


def qualify(row, kind, inputs, evidence, scope, note, renderer='', output=''):
    row['status'] = kind
    row['redraw_extent'] = scope
    add(row,'inputs_or_related_witnesses',*inputs)
    add(row,'evidence_file',evidence)
    add(row,'qualification',note)
    row['renderer'] = renderer
    row['output'] = output


def source_row(item, series, doc, scope, site, title, path, pages, printed, url, basis):
    row = dict.fromkeys(FIELDS,'')
    pdf_pages = sorted(set(int(x) for x in pages if x != ''))
    row.update(item_id=item,series=series,doc_id=doc,object_scope=scope,site=site,title_or_caption=title,
               source_path=path,source_pdf_pages=joined(pdf_pages),printed_pages=joined(printed),
               source_url=url+'#page='+str(pdf_pages[0]),page_basis=basis,status=PRINT,redraw_extent='none',
               source_kind='published source page')
    return row


def table_numbers(text):
    match=re.compile(r'\bTables?\s+(\d+(?:(?:\s*(?:–|—|-|to|through|,\s*and|,|and)\s*)\d+)*)',re.I)
    numbers=set()
    for clause in match.findall(text):
        numbers.update(map(int,re.findall(r'\d+',clause)))
        for a,b in re.findall(r'(\d+)\s*(?:–|—|-|to|through)\s*(\d+)',clause,re.I):
            numbers.update(range(int(a),int(b)+1))
    return sorted(numbers)


def index(root):
    docs={r['doc_id']:r for r in read(root,'data/documents.csv')}
    sources={r['local_path']:r for r in read(root,'data/source_inventory.csv.gz')}
    ir=read(root,'ir/core/chapter_items.csv')
    sr=read(root,'sr/core/edition2/data/objects.csv')
    table_ids={r['item_id'] for r in ir if r['kind']=='table'}|{r['item_id'] for r in sr if r['kind']=='table' and r['status']=='accepted'}
    sr_sites=defaultdict(set)
    for r in read(root,'sr/core/site_evidence.csv'):
        if r['item_id'] and r['site']:sr_sites[r['item_id']].add(r['site'])
    ir_pages=defaultdict(list)
    for r in read(root,'ir/core/chapter_item_locations.csv'):
        if r['anchor_kind'] in ('caption_text_layer','continued_caption_text_layer','page_image_checked'):
            ir_pages[r['item_id']].append(r)
    fold={f"IR{int(r['chapter']):02}.F{int(r['figure']):02}":r for r in read(root,'plates/core/data/foldouts.csv')}
    sr_captions=defaultdict(list)
    for r in read(root,'sr/core/caption_anchors.csv'):
        if r['kind']=='figure':sr_captions[r['item_id']].append(r)
    register={}
    for r in ir:
        if r['kind']!='figure':continue
        item=r['item_id'];doc=f"IR.C{int(r['chapter']):02}";loc=ir_pages[item]
        if item in fold:
            f=fold[item];path='plates/primary/'+f['source_path'];pages=[f['pdf_page']];printed=[];basis='individually located inside publisher foldout; independent PDF page'
        else:
            path=docs[doc]['local_source'];pages=[r['pdf_page']]+[q['pdf_page'] for q in loc];printed=[r['printed_page']]+[q['printed_page'] for q in loc];basis=r['status']
        register[item]=source_row(item,'IR',doc,'numbered_figure',r['site'],r['title'],path,pages,printed,sources[path]['url'],basis)
    for r in sr:
        if r['kind']!='figure' or r['status']!='accepted':continue
        item=r['item_id'];doc=f"SR.C{int(r['chapter']):02}";path='sr/primary/'+r['source'];pages=[r['pdf_page']];printed=[r['print_page']]
        for q in sr_captions[item]:
            if q['source']==r['source'] and q['pdf_page'] and int(q['pdf_page'])>int(r['pdf_page']) and re.match(r'^Figure\s+[\w.]+\.?\s*\(?cont',q['caption_text'],re.I):
                pages.append(q['pdf_page']);printed.append(q['print_page'])
        register[item]=source_row(item,'SR',doc,'numbered_figure',joined(sorted(sr_sites[item])),r['caption_or_heading_first_line'],path,pages,printed,sources[path]['url'],r['layout_basis'])
        register[item]['evidence_file']='sr/core/edition2/data/objects.csv#'+item
    for r in read(root,'sppr/core/data/report_items.csv'):
        if r['kind'] not in ('figure','chart','map','seismic image'):continue
        doc=r['doc_id'];path=docs[doc]['local_source'];item=r['item_id'];pages=range(int(r['pdf_first']),int(r['pdf_last'])+1)
        scope='numbered_figure' if r['kind']=='figure' else 'unnumbered_'+r['kind'].replace(' ','_')
        register[item]=source_row(item,doc,doc,scope,'',r['title'],path,pages,[],sources[path]['url'],'published SP/PR object-page index')
        register[item]['evidence_file']='sppr/core/data/report_items.csv#'+item
    # A same-chapter, reviewed caption that explicitly cites a numbered table gives
    # a lead to that table, regardless of whether the table supplies every curve.
    for item,row in register.items():
        if row['series']=='IR':
            texts=[r['source_caption_head'] for r in ir_pages[item]];base=item.split('.')[0]+'.T';evidence='ir/core/chapter_item_locations.csv#'+item
        elif row['series']=='SR' and item!='SR.C06.FIGURE10': # caption refers to external CK92 Table 2
            texts=[r['caption_text'] for r in sr_captions[item] if r['source']==row['source_path'].removeprefix('sr/primary/') and r['pdf_page'] in row['source_pdf_pages'].split('|')]
            base=item.split('.FIGURE')[0]+'.TABLE';evidence='sr/core/caption_anchors.csv#'+item
        else:continue
        keys=set()
        for t in texts:
            for n in table_numbers(t):
                key=base+(str(n).zfill(2) if row['series']=='IR' else str(n))
                if key in table_ids:keys.add(key)
        if keys:
            row['table_ids']=joined(sorted(keys));qualify(row,LEAD,[],evidence,'none','Caption names an indexed table. Its role and coverage can vary by panel.');row['source_kind']='caption-linked numbered table'
    # Site 846 pilot records explicitly distinguish values read from ink, table
    # associations, and boundaries quoted from the chapter text.
    old_ds={r['sql_name']:r for r in read(root,'previous/ir/metadata/dataset.csv')}
    for r in read(root,'previous/ir/metadata/item_dataset.csv'):
        if not r['item_id'].startswith('F'):continue
        item='IR11.'+r['item_id'];row=register[item];ds=r['sql_name'];src='previous/ir/'+old_ds[ds]['csv_path']
        qualify(row,LEAD,[src],'previous/ir/metadata/item_dataset.csv#'+r['item_id'],'none',r['role']);row['source_kind']='explicit Site 846 pilot figure/data association'
        if re.fullmatch(r't\d+',ds):add(row,'table_ids','IR11.T'+ds[1:].zfill(2))
    # Plates are published contextual observations. They are not a ready-made
    # digital lithology/unit/polarity track for the interpretive summary plots.
    plate=read(root,'plates/core/data/plate_sources.csv');files=read(root,'disc/core/file_index.csv.gz')
    tracks=read(root,'figures/core/composite_v2/data/source_tracks.csv');interp='figures/core/composite_v2/data/retained_layers.csv'
    composites=read(root,'figures/core/composite_v2/data/figure_index.csv');controls={r['site']:r for r in read(root,'figures/core/data/ir_interval_witnesses.csv') if r['role']=='age_control'}
    bysite=[]
    for site,n in COMPOSITE.items():
        st=str(site);ch=site-835;lith=f'IR{ch:02}.F{(6 if site==854 else 5):02}';comp=f'IR{ch:02}.F{n:02}'
        pr_pages=[r for r in composites if r['site']==st];pr=pr_pages[0]['pr_figure'];p=register[pr];p['site']=st
        assert any(r['site']==st for r in tracks)
        ctx=['plates/primary/'+r['source_path'] for r in plate if r['site']==st and r['document_kind'] in ('core_description_book','smear_slide_book')];age=controls[st];ageid=f"IR{ch:02}.T{int(age['ir_table']):02}"
        physical='figures/core/composite_v2/data/source_tracks.csv#site='+st
        for key in (lith,comp):
            row=register[key];qualify(row,LEAD,ctx if key==lith else [physical,interp+'#site='+st], 'plates/core/data/station_summary.csv#site='+st,'none',
                'Core descriptions and smear-slide sheets provide contextual observations. No complete structured unit/hatching track is established.' if key==lith else 'Published physical samples and splice controls exist for this site. The PR redraw is a distinct figure. Exact IR smoothing, inputs and authorial interpretation columns remain unverified.')
            row['source_kind']='partial interpretive evidence from core descriptions and smear sheets' if key==lith else 'related site physical-property sources and splice controls'
        vector_paths=['figures/core/composite_v2/'+r['vector_overlay'] for r in pr_pages]
        qualify(p,DATA,[physical],'figures/core/composite_v2/data/figure_layers.csv#site='+st,'physical_property_panels_only',
            'GRAPE, susceptibility and three reflectance bands replotted from published sample rows; original 20-point filter unverified. Published depth, polarity, age, graphic lithology and unit columns retained.',
            'figures/core/composite_v2/tools/render_composites.py',joined(vector_paths));p['source_kind']='published shipboard measurements and processed curves'
        fold_item=f"IR{ch:02}.F{int(next(r['site_foldout_figure'] for r in read(root,'plates/core/data/station_summary.csv') if r['site']==st)):02}"
        f=register[fold_item];qualify(f,LEAD,[physical],'plates/core/data/foldouts.csv#'+st,'none','Publisher foldout located. Released site physical-property records are candidates; no identical plotting series or processing chain has been verified.');f['source_kind']='foldout plus same-site physical-property records'
        family_counts=Counter(r['family'] for r in files if r['site']==st)
        bysite.append(dict(site=site,ir_lithology_figure=lith,ir_lithology_source=register[lith]['source_url'],ir_composite_figure=comp,ir_composite_source=register[comp]['source_url'],pr_composite_figure=pr,pr_composite_source=p['source_url'],pr_pdf_pages=p['source_pdf_pages'],pr_replotted_panel_count=3*len(pr_pages),historical_smoothing_verified='no',ir_foldout=fold_item,core_description_and_smear_witnesses=joined(ctx),released_grape_mcd=joined('disc/primary/'+r['path'] for r in files if r['site']==st and r['family']=='grape_mcd'),splice_controls=joined('disc/primary/'+r['path'] for r in files if r['site']==st and r['family']=='splice'),sus_fin_files=family_counts['sus_fin'],color_three_band_files=family_counts['color_three'],physical_source_index=physical,age_control_table=ageid,interpretation_sources=interp+'#site='+st,independently_structured_interpretation=('Site 846: chapter subunit limits and separate print-estimated lithology intervals in previous/ir/data/figures; neither provides the complete original drawing specification.' if site==846 else 'No complete authorial graphic-lithology or unit table documented. Core observations, site narrative and age controls supply partial evidence.')))
    for r in read(root,'figures/core/data/figure_index.csv'):
        item='PR.F'+r['pr_figure'];row=register[item];st=r['site'];row['site']=st
        qualify(row,DATA,['figures/core/data/ir_mean_intervals.csv#site='+st,'figures/core/data/pr_printed_marks.csv#site='+st],'figures/core/data/figure_index.csv#site='+st,'interval_curves_or_selected_marks',
            'IR interval means replotted in PR frames for comparison. Individual source lines and discrete points are incomplete. '+str(r['print_digitized_marks'])+' PR printed marks read independently; MAR input-version identity remains open.',
            'figures/core/tools/draw_atlas.py','figures/core/'+r['svg']);row['source_kind']='published IR interval means, plus selected PR print marks';add(row,'table_ids',f"IR{int(st)-835:02}.T{int(r['ir_mean_table']):02}")
    qualify(register['PR.F15'],TRACE,['sppr/core/data/pr_fig15_backtrack.csv','sppr/core/data/pr_fig15_axis_ticks.csv'],'sppr/core/tools/backtrack.py','printed_backtrack_only','Graphic positions read from the printed backtrack. Original kinematic model inputs and parameters not recovered.','sppr/core/tools/backtrack.py','sppr/core/figures/pr_fig15_graphic_check.pdf');register['PR.F15']['source_kind']='registered print graphic coordinates'
    for item,table,src,renderer,out,detail in [
        ('SR.C06.FIGURE11','', 'sr/core/figures/SR06_Figure11_data.csv','sr/core/tools/figure6_11.py','sr/core/figures/SR06_Figure11_comparison.pdf','Ten original site panels 844–853. Site 854 table retained separately.'),
        ('SR.C27.FIGURE3','SR.C27.TABLE1','sr/core/verified846/print/c27_t1.csv','sr/core/verified846/figure27.py','sr/core/verified846/proofs/Chapter27_Figure3_Comparison.pdf','Four published panels using the individually transcribed print Table 1. Data include processed estimates.')]:
        row=register[item];qualify(row,DATA,[src],renderer,'all_published_data_panels',detail,renderer,out);row['source_kind']='author-published table data';add(row,'table_ids',table)
    # Original multimedia and subsequent caption erratum have distinct provenance.
    row=register['SR.C01.FIGURE7'];assets=[r for r in read(root,'sr/core/assets.csv') if r['item_id']==row['item_id']]
    qualify(row,LEAD,['sr/primary/'+r['source_or_edited_path'] for r in assets],'sr/core/assets.csv#SR.C01.FIGURE7','none','Original movie panels A–F and caption erratum available. No independent rendering from generating data documented.');row['source_kind']='publisher multimedia products and erratum'
    for r in read(root,'sppr/core/data/survey_profiles.csv'):
        for item in ('SP.PROF.'+r['proposed_site'],r['pr_item']):
            if item not in register:continue
            row=register[item];add(row,'site',r['site']);add(row,'evidence_file','sppr/core/data/survey_profiles.csv#site='+r['site']);add(row,'qualification',r['scope']);row['source_kind']='survey profile graphic and cross-publication attribution'
    for r in read(root,'sppr/core/data/pr_site_figures.csv'):
        if r['item_id'] in register:add(register[r['item_id']],'site',r['site'])
    for item,row in register.items():
        if item.startswith('SP.MAP.') or item=='SP.F3':
            qualify(row,LEAD,['sppr/core/data/sp_card_fields.csv'],'sppr/core/data/report_items.csv#'+item,'none','Proposed site coordinates are available. Original tracklines, contours and cartographic reconstruction remain unverified.');row['source_kind']='planning-coordinate context only'
        if item=='PR.OPS.TIME':
            qualify(row,LEAD,['sppr/core/data/pr_time_chart.csv'],'sppr/core/data/report_items.csv#'+item,'none','Published category labels digitized. Complete underlying chart values or graphical redraw unverified.');row['source_kind']='structured print chart labels'
        if not row['evidence_file']:row['evidence_file']='ir/core/chapter_items.csv#'+item
        if item in fold:add(row,'evidence_file','plates/core/data/foldouts.csv#'+item)
        if row['status']==PRINT and not row['qualification']:row['qualification']='Published image or caption located. No identified figure-specific data-to-output link in this register.'
    # Each new entry carries its own renderer, native data and witness-page checks.
    import sys
    sys.path.insert(0,str(root/'edition2'))
    from revisions import figure_edits
    for item,edit in figure_edits(root).items():
        row=register[item]
        if not set((edit.get('source_pages') or edit['source_page']).split('|')).issubset(row['source_pdf_pages'].split('|')):
            raise ValueError(f'Witness page mismatch for {item}')
        # Historical qualifications are available in the previous register version.
        # Report the conclusions of this actual comparison, not the earlier unresolved lead.
        row['qualification']=''
        qualify(row,DATA,edit['inputs'].split('|'),edit['evidence_file']+'#'+item,
            edit['redraw_extent'],edit['qualification'],edit['renderer'],edit['output'])
        row['source_kind']=edit['source_kind']
        add(row,'table_ids',*edit['table_ids'].split('|'))
    for site_row in bysite:
        ir_figure=register[site_row['ir_composite_figure']]
        site_row['ir_composite_redraw_extent']=ir_figure['redraw_extent']
        site_row['ir_composite_redraw_output']=ir_figure['output']
    return list(register.values()),bysite,sources


def write_csv(path,rows):
    with path.open('w',encoding='utf8',newline='') as f:
        writer=csv.DictWriter(f,list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path)
    args=p.parse_args();root=args.root.resolve();dest=args.out or root/'data';dest.mkdir(parents=True,exist_ok=True)
    r,bysite,src=index(root)
    official=[x for x in r if x['object_scope']=='numbered_figure'];counts=Counter(x['series'] for x in official)
    assert counts=={'IR':652,'SR':515,'PR':36,'SP':3} and len(bysite)==11 and len(r)==1231 and len(set(x['item_id'] for x in r))==len(r)
    docs={x['local_source']:int(x['pdf_pages']) for x in read(root,'data/documents.csv')}
    docs.update({'plates/primary/'+x['source_path']:int(x['pdf_pages']) for x in read(root,'plates/core/data/plate_sources.csv')})
    for row in r:
        assert row['source_path'] in src and max(int(v) for v in row['source_pdf_pages'].split('|'))<=docs[row['source_path']]
        for k in ('inputs_or_related_witnesses','renderer','output','evidence_file'):
            for token in row[k].split('|'):
                if token:
                    name=token.split('#')[0];assert name in src or (root/name).is_file(),(row['item_id'],name)
        if row['status'] in (DATA,TRACE):assert row['output'] and row['renderer'] and row['inputs_or_related_witnesses']
    write_csv(dest/'figure_reproduction.csv',r);write_csv(dest/'figure_reproduction_by_site.csv',bysite)
    summary=dict(numbered_figures_by_series=dict(counts),numbered_statuses=dict(Counter(x['status'] for x in official)),numbered_extent=dict(Counter(x['redraw_extent'] for x in official)),all_rows=len(r),related_unnumbered_graphics=len(r)-len(official),resolved_source_pages=len(r),ir_foldout_items=13,sites_with_physical_and_interpretive_notes=len(bysite),historical_PR_20_point_filter_exactly_reproduced=0)
    (dest/'figure_reproduction_checks.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(summary))

if __name__=='__main__':main()
