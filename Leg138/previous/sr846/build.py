"""Rebuild the offline Site 846 SR catalogue. Python 3.10+, standard library."""
import argparse
import csv
import hashlib
import json
import re
import sqlite3
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAT = ROOT / "catalogue"
DATA = "official/VOLUME/DATA/"
PAPER = "official/VOLUME/CHAPTERS/"
LOCATOR = ["row_no", "source_line", "source_line_end", "print_page", "panel", "print_row", "pdf_y_pt", "record_note", "raw_literal"]
def readcsv(p):
    with p.open(encoding="utf-8-sig", newline="") as fp:
        return list(csv.DictReader(fp))
def line_rows(file):
    return file.read_bytes().decode("latin1").splitlines()
def whole(rows,keys):
    return [[r.get(k,"") for k in keys] for r in rows]
def qident(k):
    if not re.fullmatch("[a-z][a-z0-9_]*",k):
        raise ValueError(k)
    return '"'+k+'"'
def positioned(vals,lo=None,hi=None,page=None,panel=None,pr=None,y=None,note="",raw=""):
    return [lo,hi if hi is not None else lo,page,panel,pr,y,note,raw,*vals]

def build(target,sources):
    temp=target.with_suffix(target.suffix+".building")
    temp.unlink(missing_ok=True)
    con=sqlite3.connect(temp)
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript("""
    CREATE TABLE sources(source TEXT PRIMARY KEY, channel TEXT, kind TEXT, chapter INTEGER, title TEXT, doi TEXT, url TEXT, bytes INTEGER, sha256 TEXT, pages INTEGER);
    CREATE TABLE items(item TEXT PRIMARY KEY, chapter INTEGER, kind TEXT, number TEXT, title TEXT, page_from INTEGER, page_to INTEGER, pdf_page_from INTEGER, pdf_page_to INTEGER, scope TEXT, note TEXT);
    CREATE TABLE datasets(dataset TEXT PRIMARY KEY, item TEXT REFERENCES items, source TEXT REFERENCES sources, edition TEXT, scope TEXT, row_count INTEGER, description TEXT);
    CREATE TABLE fields(dataset TEXT REFERENCES datasets, position INTEGER, field TEXT, label TEXT, PRIMARY KEY(dataset,field));
    CREATE TABLE relations(child TEXT REFERENCES items, parent TEXT REFERENCES items, relation TEXT, basis TEXT);
    CREATE TABLE assets(item TEXT REFERENCES items, source TEXT REFERENCES sources, role TEXT);
    CREATE TABLE cell_reviews(chapter INTEGER,page INTEGER,printed_row TEXT,field TEXT,pdf_text_layer TEXT,print_reading TEXT,repository_comparator TEXT,editorial_note TEXT);
    CREATE VIEW chapters AS SELECT chapter,title,doi,url,pages,source FROM sources WHERE kind IN ('chapter','chapter_reprint');
    CREATE VIEW catalogue AS SELECT i.chapter,i.number,i.title,d.* FROM items i JOIN datasets d USING(item);
    """)
    def insert(file,name):
        rows=readcsv(file)
        con.executemany('INSERT INTO '+name+' VALUES ('+','.join('?' for _ in rows[0])+')',[list(r.values()) for r in rows])
    insert(CAT/"sources.csv","sources");insert(CAT/"items.csv","items")
    insert(CAT/"print/cell_reviews.csv","cell_reviews")
    # Validate every used byte source once before the first extraction.
    filemeta={r["source"]:r for r in readcsv(CAT/"sources.csv")}
    checked={}
    def source_path(s):
        if s not in checked:
            p=sources/s
            if hashlib.sha256(p.read_bytes()).hexdigest()!=filemeta[s]["sha256"]:
                raise ValueError("Source hash mismatch: "+s)
            checked[s]=p
        return checked[s]
    def table(key,item,source,edition,scope,description,columns,rows,labels=None):
        source_path(source)
        con.execute("INSERT INTO datasets VALUES (?,?,?,?,?,?,?)",(key,item,source,edition,scope,len(rows),description))
        con.executemany("INSERT INTO fields VALUES (?,?,?,?)",[(key,i+1,n,l) for i,(n,l) in enumerate(zip(columns,labels or columns))])
        cols=", ".join(qident(k)+" TEXT" for k in columns)
        con.execute('CREATE TABLE '+qident(key)+' (row_no INTEGER PRIMARY KEY, source_line INTEGER, source_line_end INTEGER, print_page INTEGER, panel INTEGER, print_row INTEGER, pdf_y_pt REAL, record_note TEXT, raw_literal TEXT, '+cols+')')
        ph=','.join('?' for j in range(len(columns)+len(LOCATOR)))
        for i,r in enumerate(rows,1):
            if len(r)+1!=len(columns)+len(LOCATOR):raise ValueError((key,i,r))
        con.executemany('INSERT INTO '+qident(key)+' VALUES ('+ph+')',([i,*r] for i,r in enumerate(rows,1)))
    # Page transcriptions are the maintained critical text. Complete source scans are independent witnesses.
    for file in sorted((CAT/"print").glob("c*.csv")):
        if file.stem=="cell_reviews":continue
        name=file.stem; chapter=int(name[1:3]);records=readcsv(file)
        item="c33_app" if name in ("c33_app1","c33_app2") else name
        keys=[k for k in records[0] if k not in ("page","panel","printed_row","pdf_y_pt")]
        desc={
          "c15_t2":"事件的样品上下界。","c15_t4":"从原始同位素值到作者规定的类群参比的加法系数，单位 ‰。","c15_t8":"各周期的相干与相位（度）；原表空白原样保留。",
          "c27_t1":"碳分析、GRAPE 湿密度和烯酮指标与年龄、估算干密度、温度及堆积速率同表。龄 ka，深度 m；BAR 与碳酸钙通量 g cm⁻² kyr⁻¹，TOC 通量 mg cm⁻² kyr⁻¹。",
          "c27_t2":"原刊相位含一处难解字形，最后一格照录 11É ±21°。","c33_t1":"三频带的相位和相干，保留 NC。","c33_t2":"样品统计量；coretop_* 属于被比较的东太平洋表层样品。","c33_t3":"因子得分；末行是方差百分数。",
          "c33_app1":"印本前半，十个具名物种的相对丰度（%）；mcd 是船上复合深度。","c33_app2":"后半段重新列样，同一表头跨用；保留十列刊面读数，slot_08 有三位整数，其余各列亦不据复用表头推断物种或单位。",
          "c43_appa":"印本的逐次底栖分析。p.852 表注说明已作类群校正：C. wuellerstorfi δ18O 加 0.64‰，U. peregrina δ13C 加 0.90‰，不要再加。",
          "c43_appb":"印本年龄（Ma）、修订复合深度（rmcd）和沉积速率（m/Myr），保留作者列出的 10 cm 网格。"}[name]
        rows=[positioned([r[k] for k in keys],page=int(r["page"]),panel=int(r["panel"]) if "panel" in r else None,pr=int(r["printed_row"]),y=float(r["pdf_y_pt"]) if "pdf_y_pt" in r else None) for r in records]
        table(name+"_print",item,PAPER+f"sr138_{chapter:02}.pdf","print","846",desc,keys,rows)
    # Chapter 15, including explicit physical-line spans on wrapped analyses.
    config={
      1:("hole sample depth_mbsf depth_mcd depth_rmcd dry_over_150_g dry_under_150_g coarse_pct","筛分两份干重和粗组分比例。"),
      3:("hole sample depth_mbsf depth_mcd depth_rmcd analysis_id species d18o_raw d13c_raw d18o_adjusted d13c_adjusted d18o_used","按分析编号原行保留。raw 是论文所报，adjusted 是类群调整，used 是入选值。"),
      5:("depth_mbsf depth_rmcd age_ma d18o d13c","按作者方法选择片段、平均同一样品校正值并赋龄。"),
      6:("depth_rmcd age_ma","本文的修订复合深度年龄控制点。"),
      7:("age_ma d18o d13c","3 kyr 网格，5.99 kyr 全宽，-9999.00 为作者空缺标志。")}
    for n,(fields,desc) in config.items():
        src=DATA+f"CHAP15/138117T{n}.TXT";ll=line_rows(source_path(src)); rows=[];pending=[];hole=""
        start=4 if n==3 else 2
        for i,s in enumerate(ll[start:],start+1):
            t=s.strip()
            if not t:continue
            if t.lower().startswith("note"):break
            hdr=re.match(r"^(?:138-)?846([A-D])[-$]",t)
            if hdr and n in (1,3):
                hole=hdr[1]
                if not re.search(r"\b[PS]\d+/\s*\d+",t):continue
            if n==3:
                if re.search(r"\b[PS]\d+/\s*\d+",t):pending.append([i,i,hole,t])
                else:pending[-1][1]=i;pending[-1][3]+=" "+t
            elif n==1:
                label,tail=t.split("\t",1);rows.append(positioned([hole,label.strip(),*tail.split()],i,raw=s))
            else:rows.append(positioned(t.split(),i,raw=s))
        for lo,hi,h,t in pending:
            m=re.fullmatch(r"(.+?)\s+([\d.]+|NA)\s+([\d.]+|NA)\s+([\d.]+|NA)\s+([PS]\d+/\s*\d+)\s+(\S+)\s+(.+)",t)
            if not m:raise ValueError((lo,t))
            rows.append(positioned([h,*m.groups()[:6],*m[7].split()],lo,hi,raw="\n".join(ll[lo-1:hi])))
        table(f"c15_t{n}_cd",f"c15_t{n}",src,"publisher_cd","846",desc,fields.split(),rows)
    def file_table(key,item,rel,edition,scope,desc,fields,parser):
        src=rel if not rel.startswith('CHAP') else DATA+rel
        ll=line_rows(source_path(src));rows=parser(ll)
        table(key,item,src,edition,scope,desc,fields.split(),rows)
    for h in "ABCD":
        def depth(ll):
            rows=[]
            for i,x in enumerate(ll,1):
                if not x.strip().startswith("138"):continue
                v=x.split()
                if len(v)==12:
                    # In A–C hundreds are separated in TOP. BOT independently encodes the same point.
                    if v[6]!="1" or Decimal(v[8])-Decimal(v[7])!=100:raise ValueError((i,x))
                    v=v[:6]+[v[8]]+v[8:];note="原 TOP 百位与余数分隔；用 BOT 及十进制和值验证。"
                else:note=""
                if len(v)!=11 or v[6]!=v[7] or v[2]!=h:raise ValueError((i,x))
                rows.append(positioned(v,i,note=note,raw=x))
            return rows
        file_table("c03_"+h.lower()+"_cd","c03_app",f"CHAP_3/846{h}.TXT","publisher_cd","846"+h,"GRAPE 取值位置的深度转换表，文件内没有密度列。","leg site hole core core_type section top_cm bottom_cm depth_mbsf depth_mcd depth_rmcd",depth)
    for n,f,desc in [(3,"age_ma depth_mcd","年龄模型控制点（mcd）。"),(20,"age_ma depth_mcd rate_m_myr","0.2 Myr 重叠区间导出的速率，端点空白照录。")]:
        def age(ll):
            rows=[]
            for i,x in enumerate(ll[2:],3):
                if not x.strip():continue
                v=x.split();v+=[""]*(len(f.split())-len(v));rows.append(positioned(v,i,raw=x))
            return rows
        file_table(f"c06_t{n}_cd",f"c06_t{n}",f"CHAP_6/38106T{n:02}.TXT","publisher_cd","846",desc,f,age)
    def limits(ll):
        rows=[]
        for idx in range(4,next(i for i,t in enumerate(ll) if "849 t" in t)):
            x=ll[idx];c=x.split("\t")
            if not re.match(r"^[bt] ",x):continue
            lo=idx+1;hi=lo;note=""
            if idx+1<len(ll) and re.fullmatch(r"\s*\d+[.]\d+\s*",ll[idx+1]):hi+=1
            if len(c)!=11 or hi!=lo:
                vals=["",""];note="原盘列数或换行异常，846 两列待考。完整原行存于 raw_literal。"
            else:vals=c[5:7]
            rows.append(positioned([c[0],*vals],lo,hi,note=note,raw="\n".join(ll[idx:hi])))
        return rows
    file_table("c23_t3_cd","c23_t3","CHAP23/38127T03.TXT","publisher_cd","846 columns","保留原表所有事件行及 n.a；遇额外值或断行不猜栏。","datum shallow_mcd older_mcd",limits)
    def eventages(ll):
        rows=[]
        for i,x in enumerate(ll,1):
            c=x.strip().split("\t")
            if len(c)!=4 or c[-1].strip()!="846":continue
            age,group=c[2].split();rows.append(positioned([c[0],c[1],age,group,c[3]],i,raw=x))
        return rows
    file_table("c23_t5_cd","c23_t5","CHAP23/38127TO5.TXT","publisher_cd","846","生物事件名、范围上/下限、估计年龄、化石组、站号。","datum limit_type age_ma fossil_group site",eventages)
    for letter,fields,desc in [
      ("A","hole depth_mcd age_ma lsr_cm_kyr dbd caco3_pct caco3_mar contributor","汇集不同作者/船上碳酸钙结果；干密度为估计值，MAR 为计算量。"),
      ("B","hole depth_mcd age_ma lsr_cm_kyr dbd caco3_pct opal_pct terrig_pct caco3_mar opal_mar terrig_mar contributor","蛋白石等组成及堆积速率；陆源比例采用差值。"),
      ("C","hole depth_mcd age_ma abundance preservation etching overgrowth","钙质超微化石组合的半定量描述，年龄另有来源。")]:
        def hole_rows(ll):return [positioned(x.strip().split(),i,raw=x) for i,x in enumerate(ll,1) if re.match(r"^846[A-D]\s",x.strip())]
        file_table("c35_app"+letter.lower()+"_cd","c35_app"+letter.lower(),f"CHAP35/38143AP{letter}.TXT","publisher_cd","846",desc,fields,hole_rows)
    def old39(ll):
        if [x.strip() for x in ll if re.fullmatch(r"138-\d{3}[A-Z]-\s*",x)]!=["138-844B-"]:raise ValueError("unexpected original release coverage")
        rows=[]
        for i,x in enumerate(ll,1):
            if not re.match(r"^\s*\d+[A-Z][\w-]*,",x):continue
            rows.append(positioned(["844B",x.strip()],i,raw=x))
        return rows
    file_table("c39_t2_cd","c39_t2","CHAP39/138150T2.TXT","publisher_cd","844B only","原盘共 197 个 844B 分析行；保留逐行对照，846 行数为零。","hole source_record",old39)
    def new39(ll):
        return [positioned(x.split("\t")[:8],i,raw=x) for i,x in enumerate(ll,1) if re.match(r"^846[A-D]-",x)]
    file_table("c39_t2_corrected","c39_t2","official/39_02.txt","publisher_correction","846","2000-03-29，更正文件中的 846 行；分析对象为全沉积物。","sample depth_mbsf delta_m depth_mcd age_ma laboratory_id d18o d13c",new39)
    # External editions retain their native row shape, headers and units.
    for ident,item in [(696445,"c15_t1"),(696446,"c15_t2"),(696447,"c15_t3"),(696449,"c15_t5"),(696451,"c15_t7"),(807824,"c27_t1"),(808207,"c33_app"),(60252,"c43_appa"),(60253,"c43_appb")]:
        src=f"PANGAEA/{ident}.txt";ll=source_path(src).read_text(encoding="utf-8-sig").splitlines();head=ll.index("*/")+1;labels=ll[head].split("\t");key=f"pangaea_{ident}"
        cols=[f"col_{j:02}" for j in range(1,len(labels)+1)]
        rows=[positioned(x.split("\t"),i,raw=x) for i,x in enumerate(ll[head+1:],head+2) if x.strip()]
        table(key,item,src,"PANGAEA","846","独立发布形态，保留原字段、原行及单位。"+{696445:"保留筛分干重与单位。",696446:"按命名事件保留原有界限。",696449:"以 ka BP 发布年龄，碳/氧顺序依仓储。",696451:"仓储按有氧同位素值的年龄行分发，注意与等距盘表的空缺差异。",808207:"两段沿用表头；第二段列义有疑。",60253:"通用 Depth sed 表头和单位沿用；印本深度是 rmcd。",696447:"按类群展开的宽表，行数不等于光盘的分析行数。",807824:"TOC 堆积量以 g cm⁻² kyr⁻¹ 表示。",60252:"同一行可按类群分列。"}[ident],cols,rows,labels)
    for name,item,f,desc in [
       ("846_appendix_a.txt","c43_appa","section species laboratory offset_cm depth_mbsf depth_mcd depth_rmcd d18o d13c","NOAA 说明称 raw data，所列同位素已包含印本说明的类群校正。"),
       ("846_appendix_b.txt","c43_appb","age_ma depth_rmcd rate_m_myr","作者归档年龄模型：Ma、rmcd、m/Myr。"),
       ("846_final_d18o_d13c.age","c43_appa","depth_rmcd age_ma d18o d13c","作者另发的最终时间序列。同一样品的重复分析可在此呈现为平均值。此文件没有独立的纸本附录号。")]:
        def noaa(ll):return [positioned(x.split(),i,raw=x) for i,x in enumerate(ll,1) if re.match(r"^\s*(?:846[abcd]|\d+\.\d+)",x)]
        file_table("noaa_"+("final" if "final" in name else name[4:-4]),item,"NOAA/"+name,"NOAA","846",desc,f,noaa)
    for item,source,role in [
       ("c15_t9",DATA+"CHAP15/138117T9.TXT","Site 677 reference / unchanged source"),
       ("c01_f7",PAPER+"138_corx.pdf","publisher caption correction"),("c39_t2","official/index.html","publisher correction notice"),
       ("c43_appa","NOAA/readme_mix1995.txt","depositor metadata"),("c43_appb","NOAA/readme_mix1995.txt","depositor metadata")]+[
       ("c01_f7",DATA+f"CHAP_1/WIN/FIGURE7{x}.MOV","original panel "+x) for x in "ABCDEF"]:
        source_path(source);con.execute("INSERT INTO assets VALUES (?,?,?)",(item,source,role))
    for child,parent,rel,why in [
       ("c15_t3","c15_t4","applies","类群调整，见第 15 章表 4。"),("c15_t5","c15_t3","selects_and_averages","表 5 及表注。"),("c15_t5","c15_t6","assigns_age","表 5 及表注；表 6 仅覆盖其所列区间。"),("c15_t7","c15_t5","interpolates","p.343、354。"),("c15_f5","c15_t5","plots_and_smooths","p.346，8.99 kyr；表 7 为 5.99 kyr。"),("c15_f6","c15_t5","plots_and_smooths","p.347。"),("c06_t20","c06_t3","derives_rates","第 6 章表 20。"),("c27_f3","c27_t1","plots","第 27 章表 1 和图 3。"),("c27_t1","c43_appb","uses_chronology","第 27 章 p.609 表注引用 Mix 等的赋龄。")]:
        con.execute("INSERT INTO relations VALUES (?,?,?,?)",(child,parent,rel,why))
    con.executescript("""
    CREATE VIEW c15_interpolated_numeric AS SELECT row_no,source_line,CAST(age_ma AS REAL) AS age_ma,
      CAST(NULLIF(d18o,'-9999.00') AS REAL) AS d18o, CAST(NULLIF(d13c,'-9999.00') AS REAL) AS d13c FROM c15_t7_cd;
    CREATE VIEW c27_figure3 AS SELECT row_no, print_page, print_row, sample, CAST(rmcd AS REAL) AS depth_rmcd,
      CAST(NULLIF(toc_pct,'') AS REAL) AS toc_pct,CAST(NULLIF(caco3_pct,'') AS REAL) AS caco3_pct,
      CAST(NULLIF(dbd,'') AS REAL) AS dbd,CAST(NULLIF(uk37,'') AS REAL) AS uk37 FROM c27_t1_print;
    """)
    con.execute("CREATE TABLE field_notes(dataset TEXT,field TEXT,label TEXT,unit TEXT,role TEXT,PRIMARY KEY(dataset,field),FOREIGN KEY(dataset,field) REFERENCES fields(dataset,field))")
    insert(CAT/"field_notes.csv","field_notes")
    assert con.execute("SELECT count(*) FROM fields").fetchone()==con.execute("SELECT count(*) FROM field_notes").fetchone()
    assert con.execute("PRAGMA foreign_key_check").fetchall()==[]
    assert con.execute("PRAGMA integrity_check").fetchone()==("ok",)
    con.commit();con.close();temp.replace(target)
if __name__=="__main__":
    cli=argparse.ArgumentParser(description=__doc__);cli.add_argument("--sources",required=True,type=Path);cli.add_argument("--out",type=Path,default=ROOT/"Site846_SR.sqlite")
    args=cli.parse_args();build(args.out,args.sources)
