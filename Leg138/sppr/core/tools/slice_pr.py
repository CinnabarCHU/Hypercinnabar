"""Allocate the PR's shipboard science and operations narratives to the actual site headings."""
from pathlib import Path
import csv,json,gzip,hashlib,re
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data'
def main():
    with gzip.open(D/'pages.jsonl.gz','rt') as f:
        pages={r['pdf_page']:r for r in map(json.loads,f) if r['doc_id']=='PR'}
    with (D/'pr_sections.csv').open() as f:sections=list(csv.DictReader(f))
    chunks=[];meta=[]
    for section,final in [('Scientific report',26),('Operations report including transit',97)]:
        loc=sorted((r for r in sections if r['section']==section),key=lambda r:int(r['site']))
        for i,r in enumerate(loc):
            first=int(r['pdf_page']);last=int(loc[i+1]['pdf_page']) if i+1<len(loc) else final
            for n in range(first,last+1):
                original=pages[n]['page_text'].splitlines()
                start=int(r['start_line_in_layout'])-1 if n==first else 0
                end=int(loc[i+1]['start_line_in_layout'])-1 if (n==last and i+1<len(loc)) else len(original)
                if section=='Scientific report' and r['site']=='847' and n==16:
                    end=next(j for j,l in enumerate(original[:end]) if l.strip()=='WESTERN TRANSECT')
                while start<end and (not original[start].strip() or re.match(r'^(?:Leg 138|(?:Scientific|Preliminary|Operations) Report|Page \d+)$',original[start].strip())):start+=1
                while start<end and not original[end-1].strip():end-=1
                if start==end:continue
                body='\n'.join(original[start:end])
                item='PR.'+('SCI' if section=='Scientific report' else 'OPS')+'.'+r['site']
                key=f'{item}.p{n}'
                anchor={'chunk_id':key,'item_id':item,'site':r['site'],'doc_id':'PR','section':section,'pdf_page':n,'print_page':pages[n]['printed_page'] or '','source_layout_line_first':start+1,'source_layout_line_last':end,'word_count_source_split':len(body.split()),'text_status':'source OCR, section boundaries collated','source_url':f'https://www-odp.tamu.edu/publications/prelim/138PREL.PDF#page={n}'}
                chunks.append(dict(**anchor,page_fragment=body))
                meta.append(anchor)
    with (D/'pr_site_text_index.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,list(meta[0]));w.writeheader();w.writerows(meta)
    with (D/'pr_site_text_blocks.jsonl.gz').open('wb') as f:
        with gzip.GzipFile(fileobj=f,mtime=0,mode='wb') as z:
            for r in chunks:z.write((json.dumps(r,ensure_ascii=False)+'\n').encode())
    assert len({r['item_id'] for r in chunks})==22 and len({r['chunk_id'] for r in chunks})==len(chunks)
    for sec in ['Scientific report','Operations report including transit']:
        spans={}
        for r in (r for r in chunks if r['section']==sec):
            last=spans.get(r['pdf_page'],0);assert last<r['source_layout_line_first']
            spans[r['pdf_page']]=r['source_layout_line_last']
    print(len(chunks),'source-page fragments across 22 site sections')
if __name__=='__main__':main()
