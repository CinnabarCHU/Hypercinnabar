"""Catalogue each scientific text file in its native presentation; preserve source lines and local exceptions."""
from pathlib import Path
from decimal import Decimal, InvalidOperation
import csv,gzip,json,re,collections,sys
C=Path(__file__).resolve().parents[1];R=C.parent;P=R/'primary'
def text_lines(path):return path.read_bytes().decode('latin-1').splitlines()
def write(name,headers,rows):
    with (C/name).open('w',newline='') as f:
        w=csv.writer(f);w.writerow(headers);w.writerows(rows)
def table_meta(src):
    p=Path(src);ch=int(re.search(r'CHAP_?(\d+)',src)[1]) if 'CHAP' in src else 39
    if ch==3:n='APPENDIX1';suffix=p.stem
    elif ch==35:n='APPENDIX'+p.stem[-1];suffix=''
    elif ch==39:n='TABLE2';suffix='CORRECTED' if src.endswith('39_02.txt') else 'CD'
    elif ch==23:n='TABLE'+('3' if p.stem.endswith('03') else '5');suffix=''
    else:n='TABLE'+str(int(re.search(r'T(\d+)$',p.stem)[1]));suffix=''
    item=f'SR.C{ch:02d}.{n}';key=item+('.'+suffix if suffix else '')
    return ch,n,item,key
def build():
    sources=[r for r in csv.DictReader((C/'source_manifest.csv').open()) if r['kind'] in ('cd_data','erratum_ch39_table2')]
    summaries=[];unresolved=[];nond=[];site_ev=[]
    with (C/'records.jsonl.gz').open('wb') as fh,gzip.GzipFile(fileobj=fh,mode='wb',mtime=0) as output:
        for s in sorted(sources,key=lambda s:s['source']):
            src=s['source'];a=text_lines(P/src);ch,n,item,key=table_meta(src);used=set();named=[];un=[];se=collections.Counter();bounds={};num=0;fields=[];desc=''
            def setfields(items,meaning):
                nonlocal fields,desc
                fields=items.split();desc=meaning
            def emit(i,vals,sites=(),j=None,note='',bad=False):
                nonlocal num
                j=j or i
                used.update(range(i,j+1));num+=1
                if len(vals)!=len(fields):bad=True;note=note or 'field_count_mismatch'
                if bad:
                    un.append((i,j,note));unresolved.append([key,src,i,j,note,'\n'.join(a[i-1:j])])
                sites=[v for v in sorted(set(int(q) for q in sites if q!=''))]
                for v in sites:
                    se[v]+=1;bounds.setdefault(v,[i,j]);bounds[v][1]=j
                data=dict(d=key,n=num,lo=i,hi=j,s=sites,v=None if bad else vals)
                if note:data['note']=note
                output.write((json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n').encode())
            if ch==3:
                setfields('leg site hole core core_type section top_cm bottom_cm depth_mbsf depth_mcd depth_rmcd','GRAPE sample positions and three depth assignments; this file contains no density readings.')
                for i,line in enumerate(a,1):
                    x=line.split()
                    if not x or x[0]!='138':continue
                    note=''
                    if len(x)==12 and x[6]=='1' and Decimal(x[8])-Decimal(x[7])==100:
                        x=x[:6]+[x[8]]+x[8:];note='top_cm_hundreds_split_verified_by_bottom_cm'
                    if len(x)!=11 or x[1]+x[2]!=Path(src).stem or x[6]!=x[7]:emit(i,x,[x[1]],note='column_or_interval_exception',bad=True)
                    else:emit(i,x,[x[1]],note=note)
            elif ch==6:
                tn=int(n[5:]);site=''
                if tn<=12 or tn>=18:
                    fields2='age_ma depth_mcd'+(' rate_m_per_myr' if tn>=18 else '')
                    setfields(fields2,'Age and composite depth control points.' if tn<=12 else 'Accumulation rate estimated in overlapping 0.2 Myr intervals; source end cells may be empty.')
                    if tn<=11:site=843+tn
                    if tn>=18:site=826+tn
                    for i,line in enumerate(a,1):
                        if mh:=re.fullmatch(r'\s*Site\s+(\d+)\s*',line):site=int(mh[1]);continue
                        if re.match(r'^\s*\d',line):
                            x=line.split();x+=['']*(len(fields)-len(x));emit(i,x,[site])
                elif tn==13:
                    setfields('interval_lower_Ma interval_upper_Ma_with_note COH_41_kyr COH_23_kyr COH_19_kyr','Published spectral coherence and time-interval labels; footnote letters retained.')
                    for i,l in enumerate(a,1):
                        if re.match(r'^\s*\d',l):emit(i,l.split())
                else:
                    f={14:'event_id hole_850A hole_850B hole_851B hole_851C hole_851E mean event_name',15:'event_id hole_852B hole_852C hole_852D mean event_name',16:'event_id SBP90 H91 CK92 this_study event_name',17:'anomaly Berggren_1985 CK92 this_study'}[tn]
                    setfields(f,'Comparison of published age estimates for polarity boundaries; preserve source symbols/footnotes.')
                    ss={14:[850,851],15:[852],16:[],17:[]}[tn]
                    for i,l in enumerate(a,1):
                        if re.match(r'^\s*C\d',l):
                            x=[v.strip() for v in l.split('\t')]
                            while len(x)>len(fields) and not x[-1]:x.pop()
                            if len(x)<len(fields):x+=['']*(len(fields)-len(x))
                            emit(i,x,ss)
            elif ch==15:
                tn=int(n[5:]);ss=[677] if tn==9 else [846]
                field_by={1:'hole sample depth_mbsf depth_mcd depth_rmcd dry_over_150_g dry_under_150_g coarse_pct',3:'hole sample depth_mbsf depth_mcd depth_rmcd analysis_id species d18o_raw d13c_raw d18o_adjusted d13c_adjusted d18o_used',5:'depth_mbsf depth_rmcd age_ma d18o d13c',6:'depth_rmcd age_ma',7:'age_ma d18o d13c',9:'hole sample_label_as_printed coarse_pct depth_mbsf depth_offset_m depth_mcd benthic_d18o benthic_d13c planktonic_d18o planktonic_d13c'}
                descs={1:'Two dry-weight fractions and published coarse fraction.',3:'Published isotope analyses, adjusted and selected columns beside original analytical values.',5:'Author-spliced and averaged time series with assigned ages.',6:'Published rmcd age-model control points.',7:'Regular 3 kyr interpolated time series; author sentinel -9999.00 retained.',9:'Site 677 (Leg 111) external reference series; original and shortened sample labels retained.'}
                setfields(field_by[tn],descs[tn])
                if tn in (1,3):
                    hole='';pending=[]
                    for i in range(5 if tn==3 else 3,len(a)+1):
                        t=a[i-1].strip()
                        if not t:continue
                        if t.lower().startswith('note'):break
                        if h:=re.match(r'^(?:138-)?846([A-D])[-$]',t):
                            hole='846'+h[1]
                            if not re.search(r'\b[PS]\d+/\s*\d+',t):continue
                        if tn==3:
                            if re.search(r'\b[PS]\d+/\s*\d+',t):pending.append([i,i,hole,t])
                            elif pending:pending[-1][1]=i;pending[-1][3]+=' '+t
                        else:
                            t0,tail=t.split('\t',1);emit(i,[hole,t0.strip(),*tail.split()],ss)
                    for lo,hi,h,t in pending:
                        m=re.fullmatch(r'(.+?)\s+([\d.]+|NA)\s+([\d.]+|NA)\s+([\d.]+|NA)\s+([PS]\d+/\s*\d+)\s+(\S+)\s+(.+)',t)
                        x=[h,*m.groups()[:6],*m[7].split()] if m else []
                        emit(lo,x,ss,hi)
                elif tn in (5,6,7):
                    for i,l in enumerate(a,1):
                        if re.match(r'^\s*\d',l):emit(i,l.split(),ss)
                else:
                    hole=''
                    value=re.compile(r'(?:-?\d+(?:\.\d+)?|\.?NA|N\.A\.?|,)$',re.I)
                    for i,l in enumerate(a,1):
                        t=l.strip()
                        if i<=5 or not t:continue
                        if t.lower().startswith('note'):break
                        if mh:=re.match(r'^(?:111-)?(677[AB])-\s*(.*)',t):
                            hole=mh[1];t=mh[2]
                            if not t.replace(',','').strip():continue
                            emit(i,[],ss,note='hole_heading_mixed_with_partial_record',bad=True);continue
                        if not t.replace(',','').strip():continue
                        tok=t.split()
                        if len(tok)>=9 and all(value.fullmatch(v) for v in tok[-8:]):
                            emit(i,[hole,' '.join(tok[:-8]),*tok[-8:]],ss)
                        else:emit(i,[],ss,note='source_row_missing_or_ambiguous_fields',bad=True)
            elif ch==23:
                if n=='TABLE5':
                    setfields('datum limit_type age_Ma fossil_group site','Datum classification, age, and study site in the published long table.')
                    for i,l in enumerate(a,1):
                        x=[w.strip() for w in l.split('\t')]
                        if len(x)==4 and re.fullmatch(r'8[45]\d',x[3]):
                            y=x[2].split();emit(i,[x[0],x[1],*y,x[3]],[x[3]])
                else:
                    # The printed ASCII has two independently headed panels and repeated event rows.
                    # Keep a single 22-column schema with unrelated panel columns empty.
                    setfields('datum '+' '.join(f'site{k}_{code}_mcd' for k in range(844,855) for code in ['t','o']),'Source event depths in two independent printed column panels; n.a retained. Ambiguous cells stay unassigned.')
                    panel=[]
                    for i,l in enumerate(a,1):
                        if re.match(r'^\s*(?:844|849) t\t',l):
                            panel=[int(k) for k in re.findall(r'(\d+) t',l)];continue
                        if not re.match(r'^\s*[bt] ',l):continue
                        cells=[v.strip() for v in l.split('\t')];hi=i
                        if i<len(a) and re.fullmatch(r'\s*\d+[.]\d+\s*',a[i]):hi+=1
                        if len(cells)!=1+2*len(panel) or hi!=i:
                            emit(i,[],panel,hi,note='excess_cells_or_physical_line_break',bad=True)
                        else:
                            offset=2*(panel[0]-844);full=['']*22;full[offset:offset+len(cells)-1]=cells[1:];emit(i,[cells[0],*full],panel)
            elif ch==35:
                letter=n[-1]
                f={'A':'hole depth_mcd age_ma lsr_cm_kyr dbd_g_cm3 caco3_pct caco3_mar source_label','B':'hole depth_mcd age_ma lsr_cm_kyr dbd_g_cm3 caco3_pct opal_pct terrigenous_pct caco3_mar opal_mar terrigenous_mar opal_source','C':'hole depth_mcd age_ma abundance preservation etching overgrowth'}[letter]
                setfields(f,'Published sediment parameters with chronology and calculated accumulation fields.' if letter!='C' else 'Semi-quantitative nannofossil characterization on the published age model.')
                for i,l in enumerate(a,1):
                    if m:=re.match(r'^\s*(8[45]\d)[A-E]\b',l):
                        x=[v.strip() for v in l.split('\t')] if letter!='B' else l.split()
                        emit(i,x,[m[1]])
            elif ch==39:
                setfields('sample depth_mbsf depth_offset_m depth_mcd age_ma laboratory_id d18o d13c','Whole-sediment isotope data and assigned depths/ages. Original and corrected publisher files are separate editions.')
                if src.endswith('39_02.txt'):
                    for i,l in enumerate(a,1):
                        if m:=re.match(r'^\s*(8[45]\d)[A-E]-',l):
                            x=[v.strip() for v in l.split('\t')]
                            while len(x)>8 and not x[-1]:x.pop()
                            note=''
                            if len(x)==9 and re.fullmatch(r'8[45]\d[A-E]-\d+[A-Z]-\d+,0-',x[0]) and x[1].isdigit() and re.fullmatch(r'[PS]\d+/\d+',x[6]):
                                x=[x[0]+x[1],*x[2:]]
                                note='sample_interval_split_across_tabs_source_bytes_retained'
                            emit(i,x,[m[1]],note=note)
                else:
                    hole=''
                    for i,l in enumerate(a,1):
                        if m:=re.match(r'^\s*138-(8[45]\d[A-E])-',l):hole=m[1];continue
                        if hole and l.strip():
                            m=re.fullmatch(r'\s*(.+?)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([A-Z]\d+/\s*\d+)\s+(\S+)\s+(\S+)\s*',l)
                            x=[hole+'-'+m[1],*m.groups()[1:]] if m else []
                            emit(i,x,[hole[:3]])
            else:raise ValueError(src)
            for i,l in enumerate(a,1):
                if l.strip() and i not in used:nond.append([key,src,i,l])
            for site,count in se.items():site_ev.append([ch,item,site,'source_table_rows',key,src,*bounds[site],count])
            assert num>0,(src,num)
            summaries.append([key,item,ch,src,s['sha256'],num,num-len(un),len(un),'|'.join(str(q) for q in sorted(se)),json.dumps(fields),desc])
    write('datasets.csv','dataset_id item_id chapter source sha256 records field_mapped_records unresolved_records sites fields_json description'.split(),summaries)
    write('dataset_site_evidence.csv','chapter item_id site evidence_role dataset_id source first_line last_line records_including_site'.split(),site_ev)
    write('unresolved_records.csv','dataset_id source first_line last_line reason original_text'.split(),unresolved)
    write('nonrecord_lines.csv','dataset_id source source_line original_text'.split(),nond)
    print('tables,records,unresolved,nonrecord nonempty lines',len(summaries),sum(x[5] for x in summaries),len(unresolved),len(nond))
if __name__=='__main__':build()
