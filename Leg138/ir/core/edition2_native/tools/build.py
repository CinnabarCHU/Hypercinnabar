"""Build the 92 column-labelled companions to release-one's lossless ASCII tables."""
from selection import HERE,CORE,PRIMARY,TARGET,items,readcsv,family
import numeric,fossils,reversals
from pathlib import Path
import csv,gzip,io,json,re,hashlib,os
from collections import Counter

def write(path,cols,rows):
    with path.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,cols);w.writeheader();w.writerows(rows)

def build():
    meta=[];links=[];coverage=[];status_rows=[];issues=[];headers=[];fams=Counter();stats=Counter();source_catalog={r['path']:r['sha256'] for r in readcsv(CORE/'sources.csv')}
    for id,e in TARGET.items():
        route=e['native_path'];src=(PRIMARY/route).read_bytes();digest=hashlib.sha256(src).hexdigest();assert digest==source_catalog[route]
        bits=re.findall(rb'([^\r\n]*)(\r\n|\n|\r|$)',src)[:-1];assert b''.join(l+end for l,end in bits)==src
        lines=[x.decode('latin1') for x,end in bits];site=int(e['site']) if e['site'] else '';fam=family(e);data={};roles={};notes={}
        def emit(ln,d,ns):
            assert ln not in roles
            data[ln]=d;roles[ln]='data';notes[ln]=sorted(set(ns))
        def mark(ln,kind):roles[ln]=kind
        if fam=='fossils':names=fossils.decode(id,site,lines,emit,mark)
        elif fam=='reversals':names=reversals.decode(id,site,lines,emit,mark)
        else:names=numeric.decode(id,site,fam,lines,emit,mark)
        assert data and all(len(v) for v in data.values()),id
        first=min(data);last=max(data);field_count=Counter()
        for ln,text in enumerate(lines,1):
            if ln not in roles:
                if not text.strip(' \t\x1a'):roles[ln]='blank_or_eof'
                elif ln<first:roles[ln]='header'
                elif ln>last:roles[ln]='trailing_note'
                elif re.match(r'^\s*(?:Notes?|[TB]\s*=|\(t\)\s*=)',text,re.I):roles[ln]='internal_note'
                else:roles[ln]='unresolved_internal_line';notes[ln]=['unresolved_internal_line']
            status_rows.append(dict(item_id=id,source_line=ln,role=roles[ln],raw_text=text,line_ending={b'\r\n':'CRLF',b'\n':'LF',b'\r':'CR',b'':'none'}[bits[ln-1][1]]))
            if roles[ln] in ('header','trailing_note','internal_note','hole_heading','core_heading'):
                headers.append(dict(item_id=id,source_line=ln,role=roles[ln],text=text))
            for n in notes.get(ln,[]):issues.append(dict(item_id=id,source_line=ln,issue=n,source_text=text))
        out=[]
        for ln,d in data.items():
            for name in d:
                if d[name]!='':field_count[name]+=1
            out.append(dict(item_id=id,site=site,source_path=route,source_line=ln,verification_flags='|'.join(notes.get(ln,[])),**d,raw_source_line=lines[ln-1]))
        local=f'tables/{id.replace(".","_")}.csv';cols=['item_id','site','source_path','source_line','verification_flags']+names+['unresolved_source_fragment','raw_source_line'];assert len(set(cols))==len(cols);write(HERE/local,cols,out)
        dataset=id+'.native.fields';flagged=sum(bool(ns) for ns in notes.values());offset=Counter(roles.values());quality='with_source_or_alignment_flags' if flagged else 'verified_column_layout'
        meta.append(dict(dataset_id=dataset,source_items=id,scope=e['site'] or 'cross-site',data_path='edition2_native/'+local,row_count=len(out),representation='named_fields_from_distributed_table',description=f'Published {fam} table positions and literal values, including source locator and text. {quality}; see edition2_native/coverage.csv.'))
        links.append(dict(dataset_id=dataset,item_id=id));coverage.append(dict(item_id=id,family=fam,source_path=route,source_sha256=digest,source_lines=len(lines),named_rows=len(out),flagged_lines=flagged,unresolved_internal_lines=offset['unresolved_internal_line'],first_data_line=first,last_data_line=last,quality=quality,fields=json.dumps(names,ensure_ascii=False)))
        fams[fam]+=1;stats.update(roles.values())
    assert len(meta)==len(TARGET)==92
    for f,rows in [('datasets.csv',meta),('dataset_items.csv',links),('coverage.csv',coverage),('original_headings_and_notes.csv',headers),('review_queue.csv',issues)]:write(HERE/f,list(rows[0]),rows)
    with gzip.GzipFile(filename=str(HERE/'source_lines.csv.gz'),mode='wb',mtime=0) as g:
        with io.TextIOWrapper(g,encoding='utf8',newline='') as f:
            w=csv.DictWriter(f,list(status_rows[0]));w.writeheader();w.writerows(status_rows)
    stat={'tables':len(meta),'source_lines':len(status_rows),'named_rows':sum(r['named_rows'] for r in coverage),'source_roles':dict(stats),'families':dict(fams),'tables_with_source_or_alignment_flags':sum(bool(r['flagged_lines']) for r in coverage),'flagged_lines':sum(r['flagged_lines'] for r in coverage),'flags':dict(Counter(v['issue'] for v in issues))};(HERE/'verification.json').write_text(json.dumps(stat,indent=2)+'\n');print(json.dumps(stat))
if __name__=='__main__':build()
