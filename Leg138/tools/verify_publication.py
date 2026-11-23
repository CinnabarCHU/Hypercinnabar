"""Check the electronic edition's volumes, PDF files and crosswalk to the original pages."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as source:
        return list(csv.DictReader(source))

def sha(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source,'sha256').hexdigest()

def check(root,inspect_pdfs):
    documents=read(root/'edition2/documents.csv')
    readers=read(root/'publication/chapters/catalog.csv')
    summaries={r['doc_id']:r for r in documents}
    if len(readers)!=76 or set(summaries)!={r['doc_id'] for r in readers}:
        raise ValueError('The publication and the source catalogue contain different volumes')
    archival_file=root/'publication/chapters/archival_readers.csv'
    archival={r['doc_id']:r for r in read(archival_file)} if archival_file.is_file() else {}
    retained=[]
    total_source=total_reader=total_links=0
    for r in readers:
        d=summaries[r['doc_id']]
        src=int(r['source_pages']);count=int(r['reading_pages']);file=root/'publication/chapters'/r['local_path']
        assert int(d['source_pdf_pages'])==src
        if r['doc_id'] in archival and r['sha256']==archival[r['doc_id']]['sha256']:
            retained.append(r['doc_id'])
            assert count==int(archival[r['doc_id']]['reading_pages'])
        else:assert int(d['edition_pdf_pages'])==src+count
        assert r['source_url']==d['source_url']
        assert file.stat().st_size==int(r['bytes']) and sha(file)==r['sha256'],file
        if inspect_pdfs:
            import fitz
            with fitz.open(file) as doc:
                assert len(doc)==count
                seen=0
                for page in doc:
                    for link in page.get_links():
                        if link['kind']==fitz.LINK_GOTO:
                            assert 0<=link['page']<len(doc),(file,page.number,link['page'])
                        seen+=1
                assert seen==int(r['links']),(file,seen,r['links'])
        total_source+=src;total_reader+=count;total_links+=int(r['links'])
    assert total_source==1922
    proof=json.loads((root/'data/edition_parts.json').read_text())
    report=root/'publication/ODP138_Leg_Report_Edition.pdf'
    assert sha(report)==proof['output_sha256'] and proof['total_pages']==84
    for part in proof['parts']:
        assert sha(root/part['path'])==part['input_sha256'],part['path']
    return {'checked_compact_volumes':len(readers),'source_pages':total_source,'compact_reading_pages':total_reader,
            'paired_edition_pages':sum(int(r['edition_pdf_pages']) for r in documents),'prior_public_readers':retained,'compact_pdf_links':total_links,
            'compact_pdf_bytes':sum(int(r['bytes']) for r in readers),'station_reader_pages':proof['total_pages'],
            'reference_pages_online':True,'inspected_internal_pdf_links':inspect_pdfs}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--inspect-pdfs',action='store_true',help='Also open every PDF and inspect every jump target using PyMuPDF')
    p.add_argument('--output',type=Path);a=p.parse_args()
    data=json.dumps(check(a.root,a.inspect_pdfs),indent=2)+'\n'
    if a.output:a.output.write_text(data)
    print(data)
