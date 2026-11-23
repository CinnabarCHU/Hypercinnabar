"""Create asset indexes from the retained PDF distributions. Includes explicit source-plane identities."""
from __future__ import annotations
from pathlib import Path
import argparse,csv,gzip,hashlib,json,re
from collections import Counter
import fitz
def read(data,name):
    with (data/name).open() as f:return list(csv.DictReader(f))
def write(data,name,fields,rows):
    with (data/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def print_ids(source_text):
    s=source_text.upper().replace('—','-').replace('–','-').replace('•',' ').replace('|',' ').replace('[',' ').replace(']',' ')
    form=re.search(r'SI(?:TE|T[E8]|I\s?B|1\s?B)\s*(8\s?\d\s?\d)\s*HOLE\s*([A-E])\s*CORE\s*[.:;I]?\s*(\d{1,2})\s*([HXR])',s)
    photo=re.search(r'(?<!\d)(8[4-5]\d)\s*([A-E])\s*-\s*(\d\d?)\s*([HXR])',s)
    return tuple(''.join(m.groups()).replace(' ','') if m else '' for m in (form,photo))
def build(primary,data):
    sources=read(data,'plate_sources.csv')
    fixes={(r['site'],int(r['pdf_page'])):r for r in read(data,'vcd_checked_headers.csv')}
    photos={Path(r['source_path']).stem.upper():r for r in sources if r['document_kind']=='core_photo'}
    native=[];vcd=[];smear=[];folds=[];stats=[];page_text=[]
    srcby={a['source_path']:a for a in sources}
    for core,r in photos.items():
        with fitz.open(primary/r['source_path']) as d:
            p=d[0];images=p.get_images(full=True)
            for img in images:
                xref,mask,w,h,bpc,cs,_,name,filter_,_=img
                binary=d.xref_stream_raw(xref)
                native.append(dict(core_id=core,source_path=r['source_path'],pdf_page=1,
                    page_width_pt=p.rect.width,page_height_pt=p.rect.height,n_image_objects=len(images),xref=xref,soft_mask_xref=mask,
                    width_px=w,height_px=h,bits_per_component=bpc,colorspace=cs,compression=filter_,
                    native_stream_sha256=hashlib.sha256(binary).hexdigest(),standalone_native_jpeg=int(filter_=='DCTDecode' and binary.startswith(b'\xff\xd8'))))
    for r in sources:
        kind=r['document_kind'];site=r['site'];path=r['source_path']
        if kind=='core_photo':continue
        with fitz.open(primary/path) as d:
            for num,page in enumerate(d,1):
                page_text.append(dict(source_path=path,document_kind=kind,site=site,pdf_page=num,
                    width_pt=page.rect.width,height_pt=page.rect.height,source_text_layer=page.get_text()))
            if kind=='core_description_book':
                for num,p in enumerate(d,1):
                    head=' '.join(w[4] for w in p.get_text('words',sort=True) if w[1]<110)
                    form,photo=print_ids(head)
                    original_form,original_photo=form,photo
                    if fix:=fixes.get((site,num)):
                        form,photo,evidence=fix['printed_form_core'],fix['printed_photo_core'],fix['review']
                    elif form and photo and form==photo:evidence='two_source_OCR_identifiers_agree'
                    elif form and photo:evidence='two_source_OCR_identifiers_disagree'
                    elif photo:evidence='only_printed_photo_identifier_resolved_in_source_OCR'
                    elif form:evidence='only_form_header_resolved_in_source_OCR'
                    else:evidence='unresolved'
                    src=photos.get(photo)
                    # Never assign an unidentified printed photograph using only a matching form label.
                    candidate='' if photo or not form else photos.get(form,{}).get('source_path','')
                    vcd.append(dict(site=site,pdf_page=num,printed_form_core=form,printed_photo_core=photo,photo_file=src['source_path'] if src else '',
                        identity_evidence=evidence,source_path=path,form_based_photo_candidate=candidate,source_ocr_form_token=original_form,source_ocr_photo_token=original_photo,
                        source_ocr_header=head[:200],volume_label_mismatch=int(bool(form and not form.startswith(site)))))
            if kind=='smear_slide_book':
                for num,p in enumerate(d,1):
                    smear.append(dict(site=site,source_path=path,pdf_page=num,width_pt=p.rect.width,height_pt=p.rect.height,
                         contents='smear-slide sample description and composition tables',status='page_index_only; sample values not transcribed'))
            if kind=='back_pocket':
                page=d[0];words=page.get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks']
                for block in words:
                    for line in block.get('lines',[]):
                        text=''.join(span['text'] for span in line['spans']).strip()
                        mo=re.match(r'Initial Reports, Volume 138, Chapter (\d+), Figure (\d+)',text)
                        if not mo:continue
                        chapter,fig=[int(v) for v in mo.groups()];x0,y0,x1,y1=line['bbox']
                        desc='Optical reflectance, density and magnetic susceptibility by composite depth'
                        sites=str(chapter+835) if 9<=chapter<=19 else 'multiple'
                        if chapter==14:desc='GRAPE density and reflectance by composite depth'
                        if chapter==5:desc='GRAPE density compared with downhole density logs'
                        if chapter==6:desc='GRAPE densities with intersite correlations versus depth'
                        folds.append(dict(source_path=path,pdf_page=1,chapter=chapter,figure=fig,scope=sites,description=desc,
                            caption_anchor_left_pt=f'{x0:.2f}',caption_anchor_top_pt=f'{y0:.2f}',caption_anchor_right_pt=f'{x1:.2f}',caption_anchor_bottom_pt=f'{y1:.2f}',source_ocr_first_caption_line=text))
    for site in range(844,855):
        ss=str(site);f=next(x for x in folds if x['scope']==ss)
        stats.append(dict(site=site,photo_pdf_count=sum(x['site']==ss for x in photos.values()),
                          vcd_pdf_pages=sum(x['site']==ss for x in vcd),smear_pdf_pages=sum(x['site']==ss for x in smear),
                          site_foldout_chapter=f['chapter'],site_foldout_figure=f['figure'],verified_optical_pair_count=1))
    for file,rows in [('native_photo_catalog.csv',native),('vcd_pages.csv',vcd),('smear_pages.csv',smear),('foldouts.csv',folds),('station_summary.csv',stats)]:
        assert rows;write(data,file,list(rows[0]),rows)
    with (data/'plate_page_text.jsonl.gz').open('wb') as stream:
        with gzip.GzipFile(filename='',mode='wb',fileobj=stream,mtime=0) as packed:
            for row in page_text:
                packed.write((json.dumps(row,ensure_ascii=False)+'\n').encode('utf-8'))
    assert len(page_text)==620
    witness='VOLUME/CORES/IMAGES/index.html'
    raw=(primary/witness).read_bytes()
    write(data,'plate_directory_witness.csv',['source_path','url','bytes','sha256'],[dict(source_path=witness,
        url='https://www-odp.tamu.edu/publications/138_IR/VOLUME/CORES/IMAGES/',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())])
    assert len(vcd)==592 and len(folds)==13 and len(photos)==593 and len(stats)==11
    print(len(vcd),'VCD pages;',len(smear),'smear pages;',len(folds),'foldout illustrations;',len(native),'native images')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path);p.add_argument('data',type=Path);q=p.parse_args();build(q.primary,q.data)
