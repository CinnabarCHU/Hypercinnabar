"""Compare the actual PDFs in a rebuilt paired edition with the published edition catalogue."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

def sha(file):
    with file.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def rows(file):
    with file.open(encoding='utf-8-sig',newline='') as stream:
        return {row['doc_id']:row for row in csv.DictReader(stream)}

def compare(expected,output):
    old=rows(expected)
    fresh=rows(output/'documents.csv')
    if old.keys()!=fresh.keys():
        raise ValueError('Document ID sets differ')
    differences=[]
    for key,r in fresh.items():
        actual=sha(output/r['pdf']);canon=old[key]
        if not (actual==canon['edition_pdf_sha256']==r['edition_pdf_sha256'] and
                r['source_pdf_sha256']==canon['source_pdf_sha256'] and r['edition_pdf_pages']==canon['edition_pdf_pages']):
            differences.append({'doc_id':key,'expected_sha256':canon['edition_pdf_sha256'],'output_sha256':actual})
    return {'documents':len(fresh),'identical_pdf_files':len(fresh)-len(differences),'source_pages':sum(int(r['source_pdf_pages']) for r in fresh.values()),'edition_pages':sum(int(r['edition_pdf_pages']) for r in fresh.values()),'reference_catalog_sha256':sha(expected),'differences':differences}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rebuilt',type=Path)
    parser.add_argument('--catalog',type=Path,default=Path(__file__).resolve().parents[1]/'edition2/documents.csv')
    parser.add_argument('--write',type=Path)
    a=parser.parse_args();res=compare(a.catalog,a.rebuilt);data=json.dumps(res,indent=2)+'\n'
    if a.write:a.write.write_text(data)
    print(data);raise SystemExit(int(bool(res['differences'])))
