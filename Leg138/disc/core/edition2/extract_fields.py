"""Parse the 11 interstitial-water files and 65 log products without unit conversion."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import re
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

WATER = "depth_mbsf pH salinity chloride sodium alkalinity sulfate magnesium calcium potassium strontium lithium silica ammonia".split()
WATER_RECORD = re.compile(r"(?:(?:(138)-)?(\d{3})-?([A-Z])-)?(\d+)([HX])-([\d]+)\s+(\d+)([-_])(\d+)\s+(.+)")
HOLE_HEADER = re.compile(r"(?:(138)-)?(\d{3})-?([A-Z])-?")
NUMERIC = re.compile(r"[-+]?\d+(?:\.\d+)?")
ROLES = {"ACT_GST":"geochemical yields and calculated indicators","DIT_SDT":"resistivity and transit times","EL_ERROR":"elemental error product","GEOCHEM":"natural gamma and elemental channels","GPIT":"hole geometry and magnetic field","NGT_LDT":"natural gamma and density channels where published","OX_ERROR":"processed oxide bounds and FACT quality curve","OXIDES":"normalized oxide product","XRF":"published XRF and composition columns"}

@contextmanager
def writer(path, header):
    if path.suffix == ".gz":
        stream = io.TextIOWrapper(gzip.GzipFile(filename=str(path),mode="wb",mtime=0),encoding="utf-8",newline="")
    else:
        stream = path.open("w",encoding="utf-8",newline="")
    with stream:
        dest = csv.writer(stream,lineterminator="\n")
        dest.writerow(header)
        yield dest

def write_rows(path, header, rows):
    with writer(path,header) as out:
        out.writerows(rows)

def parse_water(path, root, metadata, signals):
    site = path.suffix[1:]
    rel = path.relative_to(root).as_posix()
    hole = None
    leg = ""
    header_line = ""
    rows=[]
    for n,line in enumerate(path.read_text(encoding="ascii").splitlines(),1):
        s=line.strip()
        if m := HOLE_HEADER.fullmatch(s):
            printed_leg, printed_site, hole = m.groups()
            assert printed_site==site
            leg=printed_leg or ""
            header_line=n
        elif re.match(r"138\s+8[45]\d\s+[A-Z]\s+",s):
            parts=s.split()
            leg, printed_site, hole, core, core_type, section, top, bottom = parts[:8]
            assert printed_site==site
            values=parts[8:]
            sample=s[:s.index(values[0],line.strip().index(bottom)+len(bottom))].strip()
            rows.append([rel,n,"",site,leg,hole,core,core_type,section,top,bottom,sample,*values])
        elif m:=WATER_RECORD.fullmatch(s):
            row_leg,row_site,row_hole,core,core_type,section,top,separator,bottom,tail=m.groups()
            assert (row_site or site)==site
            assert row_hole or hole
            values=tail.split()
            rows.append([rel,n,"" if row_hole else header_line,site,row_leg or ("" if row_hole else leg),row_hole or hole,core,core_type,section,top,bottom,s[:-len(tail)].rstrip(),*values])
        else:
            if re.match(r"\d",s):
                raise ValueError((path,n,s))
            metadata.append((rel,n,"header_note_or_blank",line))
            continue
        if re.match(r"\d",s) and HOLE_HEADER.fullmatch(s):
            metadata.append((rel,n,"hole_context",line))
            continue
        fields=WATER[:-1] if site in {"844","848"} else WATER
        assert len(values)==len(fields),(rel,n,values)
        for name, token in zip(fields,values):
            if not NUMERIC.fullmatch(token):
                assert token in {"**","-","_","<<10","<10"},(rel,n,name,token)
                signals.append((rel,n,name,token,"threshold_as_printed" if token.startswith("<") else "non_numeric_mark_as_printed"))
        if len(fields)<len(WATER):
            rows[-1].append("")
    return rows

def read_acronyms(primary):
    result={}
    p=primary/"READ_DIR"/"LOGS.ACR"
    for n,line in enumerate(p.read_text(encoding="ascii").splitlines(),1):
        if m:=re.match(r"^(\w+)\s*\t(.+)",line):
            result[m[1]] = n,m[2].strip()
    return result

def fixed_tokens(line):
    tokens=[line[i:i+11].strip() for i in range(0,len(line.rstrip()),11)]
    if not all(NUMERIC.fullmatch(x) or re.fullmatch(r"\*+",x) for x in tokens):
        raise ValueError(line)
    return tokens

def parse_log(path,primary,outdir,schemas,metadata):
    rel = path.relative_to(primary).as_posix()
    kind=path.stem
    group=kind.split("_")[0] if kind.startswith("GPIT") else kind
    lex=read_acronyms(primary)
    lines=path.read_text(encoding="ascii").splitlines()
    data=[]
    for n,l in enumerate(lines,1):
        if re.match(r"^\s*[-+\d*]",l): data.append((n,fixed_tokens(l)))
        elif l: metadata.append((rel,n,"header_or_title",l))
        else: metadata.append((rel,n,"blank",l))
    hd=[(n+1,l) for n,l in enumerate(lines[:data[0][0]-1])]
    if kind=="OX_ERROR":
        labels=hd[0][1].split()[:2]+hd[1][1].split()+hd[2][1].split()
        assert len(labels)==15,(path,hd)
        headerlines=[1]*2+[2]*7+[3]*6
    else:
        (hl,hs),= [(n,l) for n,l in hd if l.lstrip().startswith("DEPTH ")]
        labels=hs.split()
        headerlines=[hl]*len(labels)
    hole_match=re.search(r"8[45]\d\s*-?\s*([A-E])\b",lines[0],re.I)
    hole=hole_match[1].upper() if hole_match else ""
    counts=Counter(labels)
    occurrence=Counter()
    keys=[]
    for pos,(label,hl) in enumerate(zip(labels,headerlines),1):
        occurrence[label]+=1
        key=label if counts[label]==1 else label+"__"+str(occurrence[label])
        role=ROLES[group]
        ref,desc=lex.get(label,("",""))
        if kind=="OX_ERROR" and pos>=4:
            role="lower error bound" if pos%2==0 else "upper error bound"
        elif label=="FACT": role="quality control curve"
        if kind=="EL_ERROR" and pos>=3: role="elemental error product; pair position "+str((pos-3)%2+1)
        if label in {"DEPTH","THICKNESS"}:
            desc="Best-estimate depth in meters below seafloor." if label=="DEPTH" else "Distance between sequential measurements."
            reference="READ_DIR/OXIDES.LOG (depth and thickness in oxide product)" 
        else:
            reference=("READ_DIR/LOGS.ACR:"+str(ref)) if ref else ""
            if kind in {"OXIDES","OX_ERROR"} and not reference: reference="READ_DIR/OXIDES.LOG"
        schemas.append([rel,hl,pos,key,label,role,desc,reference])
        keys.append(key)
    numbers=Counter()
    starts=[]
    height=3 if kind=="OX_ERROR" else 1
    assert len(data)%height==0
    location=outdir/"logs"/(path.name+".csv.gz")
    with writer(location,["source_line_1","source_line_2","source_line_3",*keys]) as w:
        for j in range(0,len(data),height):
            segment=data[j:j+height]
            vv=sum([v for n,v in segment],[])
            assert len(vv)==len(labels)
            if height==3: assert [len(v) for n,v in segment]==[2,7,6]
            starts.append(float(vv[0]))
            numbers.update(x for x in vv if x.startswith("*") or x=="-999.2500")
            line_ids=[n for n,v in segment]
            w.writerow([*line_ids, *([""]*(3-height)), *vv])
    return [rel,kind,path.suffix[1:],hole,len(lines),len(starts),len(labels),len(starts)*len(labels),min(starts),max(starts),sum(b<=a for a,b in zip(starts,starts[1:])),numbers["-999.2500"],sum(v for k,v in numbers.items() if k.startswith("*")),hashlib.sha256(path.read_bytes()).hexdigest(),location.relative_to(outdir).as_posix()]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("primary",type=Path)
    parser.add_argument("output",type=Path)
    a=parser.parse_args()
    (a.output/"logs").mkdir(parents=True,exist_ok=True)
    meta,signals,water,schemas,files=[],[],[],[],[]
    water_manifest=[]
    for path in sorted(a.primary.glob("SITE_*/CHEM/INTERSTI.*")):
        rows=parse_water(path,a.primary,meta,signals)
        water.extend(rows)
        water_manifest.append([path.relative_to(a.primary).as_posix(),len(rows),len(path.read_bytes().splitlines()),hashlib.sha256(path.read_bytes()).hexdigest()])
    for path in sorted(a.primary.glob("SITE_*/LOGS/*")):
        if path.suffix[1:].isdigit():
            files.append(parse_log(path,a.primary,a.output,schemas,meta))
    assert len(files)==65 and len(water_manifest)==11
    write_rows(a.output/"water.csv.gz",["source_file","source_line","hole_context_line","directory_site","leg_printed_or_inherited","hole","core","core_type","section","interval_top_cm","interval_bottom_cm","native_sample_prefix",*WATER],water)
    write_rows(a.output/"water_marks.csv",["source_file","line","field","source_token","type"],signals)
    write_rows(a.output/"water_sources.csv",["source_file","data_rows","physical_lines","sha256"],water_manifest)
    write_rows(a.output/"native_headers.csv.gz",["source_file","line","type","source_text"],meta)
    write_rows(a.output/"log_dictionary.csv.gz",["source_file","source_header_line","column_number","field_key","label_printed","role","official_acronym_description","reference"],schemas)
    write_rows(a.output/"log_sources.csv",["source_file","file_series","directory_site","hole_in_header","physical_lines","data_records","fields_per_row","data_cells","min_depth","max_depth","nonincreasing_steps","minus999p25_cells","asterisk_cells","sha256","extract_path"],files)
    report={"porewater_files":len(water_manifest),"porewater_rows":len(water),"water_source_mark_counts":dict(Counter(r[3] for r in signals)),"logging_files":len(files),"logging_records":sum(r[5] for r in files),"logging_cells":sum(r[7] for r in files),"logging_minus999p25_cells":sum(r[11] for r in files),"logging_asterisk_cells":sum(r[12] for r in files)}
    (a.output/"fields_verification.json").write_text(json.dumps(report,indent=2)+"\n")
    print(report)

if __name__=="__main__":
    main()
