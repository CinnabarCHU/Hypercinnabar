"""Check all pages for original-stream transfer, resource hashes, reading order and local link integrity."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
import argparse,gzip,json
import fitz
from companions import read,digest


class Links(HTMLParser):
    def __init__(self):super().__init__();self.paths=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ('href','src','data-url') and v and not urlsplit(v).scheme:self.paths.append(v)


def check(root,out):
    docs=read(out/'documents.csv');pages=read(out/'pages.csv');assets=read(out/'resources.csv')
    unique={}
    for a in assets:
        path=out/a['file']
        if path not in unique:unique[path]=digest(path)
        assert unique[path]==a['sha256'],a['file']
    hashes={};total_images=0;total_lines=0;nlinks=0;struct_tables=0;seen=set()
    for r in docs:
        code=r['doc_id'];sourcepath=root/r['source_local'];target=out/r['pdf']
        assert digest(sourcepath)==r['source_pdf_sha256'] and digest(target)==r['edition_pdf_sha256']
        parser=Links();htmlpath=out/r['html'];parser.feed(htmlpath.read_text())
        for link in parser.paths:
            rel=unquote(urlsplit(link).path)
            assert not rel or (htmlpath.parent/rel).is_file(),(code,link)
            nlinks+=1
        with fitz.open(sourcepath) as a,fitz.open(target) as b,gzip.open(out/'audit'/(code+'.jsonl.gz'),'rt') as stream:
            records=[json.loads(line) for line in stream]
            mapped=[rr for rr in pages if rr['doc_id']==code]
            assert len(a)==len(records)==len(mapped)==int(r['source_pdf_pages'])
            assert len(b)==int(r['edition_pdf_pages'])
            assert [int(rr['source_page']) for rr in mapped]==list(range(1,len(a)+1))
            for rp,block in zip(mapped,records):
                n=int(rp['source_page']);seen.add((code,n));source=a[n-1];w=b[int(rp['edition_witness'])-1]
                assert source.rect==w.rect
                # PDF grafting preserves native image bitstreams, independent of display size.
                ims=source.get_images(full=True);copies=w.get_images(full=True);assert len(ims)==len(copies)
                for im,copy in zip(ims,copies):
                    assert im[2:9]==copy[2:9]
                    assert a.xref_stream_raw(im[0])==b.xref_stream_raw(copy[0]),(code,n,im[0])
                    total_images+=1
                assert source.get_text('text',flags=fitz.TEXTFLAGS_TEXT)==w.get_text('text',flags=fitz.TEXTFLAGS_TEXT),(code,n,'source OCR')
                slots=[(p['block'],l['line'],l['part']) for p in block['packets'] for l in p['lines']]
                assert len(set(slots))==len(slots)==int(rp['source_line_segments'])
                total_lines+=len(slots)
                physical={(blk['number'],j) for blk in source.get_text('dict',flags=fitz.TEXTFLAGS_TEXT)['blocks'] if blk['type']==0 for j,line in enumerate(blk['lines'],1) if ''.join(s['text'] for s in line['spans']).strip()}
                assert {(x,y) for x,y,z in slots}==physical,(code,n,'omitted physical line')
                for bounds in [(p['bbox'],p['lines']) for p in block['packets']]:
                    assert all(l['bbox'][0]<=l['bbox'][2] and l['bbox'][1]<=l['bbox'][3] for l in bounds[1])
                struct_tables+=int(rp['pdf_table_assets'])
            if code in ('IR.C09','SR.C01'):
                reading=records[1]['packets']
                left,right=('Four holes were drilled','siliceous clays with') if code=='IR.C09' else ('Because of the historic voyage','rarely preserved in sedimentary')
                def index(prefix):
                    return next((i,p['lane']) for i,p in enumerate(reading) if p['lines'][0]['text'].startswith(prefix))
                li,ll=index(left);ri,rl=index(right);assert ll=='left' and rl=='right' and li<ri
    parser=Links();parser.feed((out/'index.html').read_text())
    assert all((out/unquote(urlsplit(p).path)).is_file() for p in parser.paths)
    return dict(documents=len(docs),source_pages=len(seen),intact_source_image_stream_references=total_images,
                source_line_segments_checked=total_lines,source_ocr_page_equality=len(seen),pdf_table_representations=struct_tables,
                checked_local_chapter_links=nlinks,resource_relations=len(assets),distinct_companion_files=len(unique))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();result=check(a.root,a.output);(a.output/'independent_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
