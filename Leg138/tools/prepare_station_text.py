"""Segment PR scientific station sections by verified headings, retaining page- and line-level origin."""
from pathlib import Path
import argparse,csv,json,gzip,re,subprocess
def write(root,out):
    sections=[r for r in csv.DictReader((root/'sppr/core/data/pr_sections.csv').open()) if r['section']=='Scientific report']
    p=subprocess.run(['pdftotext','-layout',str(root/'sppr/primary/PR.pdf'),'-'],capture_output=True,check=True).stdout.decode().split('\f')
    rows=[]
    for k,s in enumerate(sections):
        start=int(s['pdf_page']);a=int(s['start_line_in_layout']);end=int(s['pdf_last'])
        nxt=sections[k+1] if k+1<len(sections) else None
        for n in range(start,end+1):
            lines=p[n-1].splitlines()
            if n==start:
                first=a+1
                assert s['site'] in lines[a-1],(s,lines[a-1])
            else:first=1
            last=(int(nxt['start_line_in_layout'])-1 if nxt and n==int(nxt['pdf_page']) else len(lines))
            buf=[];lo=None
            def flush():
                nonlocal buf,lo
                if buf:
                    text=' '.join(v.strip() for _,v in buf)
                    rows.append(dict(site=s['site'],pdf_page=n,source_line_first=lo,source_line_last=buf[-1][0],quality='PR_text_layer_reflow_unproofed',text=text))
                buf=[];lo=None
            for ln in range(first,last+1):
                raw=lines[ln-1];t=raw.strip()
                if not t or t in ['Leg 138','Preliminary Report','Scientific Report','WESTERN TRANSECT','EASTERN TRANSECT'] or re.fullmatch(r'Page \d+',t):flush();continue
                if len(raw)-len(raw.lstrip())>=4 and buf and (buf[-1][1].rstrip().endswith(('.','?','!')) or len(raw)-len(raw.lstrip())>=8):flush()
                if lo is None:lo=ln
                buf.append((ln,raw))
            flush()
    assert {r['site'] for r in rows}=={str(n) for n in range(844,855)}
    with gzip.open(out/'pr_science_blocks.jsonl.gz','wt') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    print('Source-linked PR scientific blocks',len(rows))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('out',type=Path);a=p.parse_args();write(a.root,a.out)
