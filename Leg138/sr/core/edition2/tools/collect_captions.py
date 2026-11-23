"""Collect caption-line layout evidence, references, appendix headings and source-page geometry."""
from pathlib import Path
import csv,gzip,json,re
import fitz
E=Path(__file__).resolve().parents[1];C=E.parent;P=C.parent/'primary'
HEAD=re.compile(r'^\s*[(“\'‘]?\s*(Figure|Fig\.?|Table|Plate)\s*\.?\s*([\dIl]{1,2})([A-Da-d]?)\s*([.,:;)]|\(continued\)|\s+|$)',re.I)
REF=re.compile(r'\b(Figures?|Figs?\.?|Tables?|Plates?)\s+([1-9]\d?[a-d]?)(?!\w)(?:\s*(?:and|,|–|-|to|through)\s*([1-9]\d?[a-d]?)(?!\w))?',re.I)
APP=re.compile(r'^\s*APPENDI[XI](?:\s+([A-Z1-9]))?\.?\s*$',re.I)
def broad():
    chapters=list(csv.DictReader((C/'chapters.csv').open()))
    events=[];refs=[];appendices=[]
    for v in chapters:
        ch=int(v['chapter'])
        with fitz.open(P/v['source']) as doc:
            for idx,pg in enumerate(doc,1):
                blocks=pg.get_text('dict',flags=fitz.TEXTFLAGS_DICT&~fitz.TEXT_PRESERVE_IMAGES)['blocks']
                for b in blocks:
                    lines=b.get('lines',[])
                    for j,line in enumerate(lines):
                        spans=line['spans']
                        txt=''.join(x['text'] for x in spans).strip()
                        direction=line['dir'];font=spans[0]['font'];size=spans[0]['size']
                        folio=int(v['print_page_first'])+idx-1 if int(v['print_page_last'])-int(v['print_page_first'])+1==len(doc) else ''
                        geometry=dict(source=v['source'],chapter=ch,pdf_page=idx,print_page=folio,bbox=[round(k,2) for k in line['bbox']],direction=direction,font=font,font_pt=round(size,2),block_id=b['number'],line_id=j)
                        if m:=HEAD.match(txt):
                            kind=m[1].lower().rstrip('.')
                            if kind=='fig':kind='figure'
                            base=m[2].upper().replace('I','1').replace('L','1')
                            number=str(int(base))+m[3].upper()
                            context=' '.join(''.join(s['text'] for s in l['spans']).strip() for l in lines[max(j-1,0):min(j+3,len(lines))])[:680]
                            events.append(dict(item_id=f'SR.C{ch:02d}.{kind.upper()}{number}',kind=kind,number=number,text=txt,separator=m[4],context=context,**geometry))
                        if m:=APP.match(txt):
                            appendices.append(dict(id=f"SR.C{ch:02d}.APPENDIX{(m[1] or '').upper()}",text=txt,**geometry))
                        for match in REF.finditer(txt):
                            kind=match[1].lower().rstrip('s.'); kind='figure' if kind.startswith('fig') else 'plate' if kind.startswith('plate') else 'table'
                            refs.append([ch,kind,match[2].upper(),match[3].upper() if match[3] else '',idx,txt[:230]])
    for name,arr in [('candidate_lines.jsonl.gz',events),('appendix_headings.jsonl.gz',appendices)]:
        with (E/'data'/name).open('wb') as f,gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:
            for x in arr:z.write((json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n').encode())
    with (E/'data/reference_mentions.csv.gz').open('wb') as h,gzip.GzipFile(fileobj=h,mode='wb',mtime=0) as z:
        import io
        with io.TextIOWrapper(z,encoding='utf-8',newline='') as out:
            w=csv.writer(out);w.writerow(['chapter','kind','first','second','pdf_page','context']);w.writerows(refs)
    print(len(events),len(appendices),len(refs))
if __name__=='__main__':broad()
