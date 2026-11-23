"""Check coverage, primary-source locators and selected edition comparisons."""
import argparse
import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter
from decimal import Decimal as D
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def verify(db,source_root=None):
    c=sqlite3.connect(db);c.row_factory=sqlite3.Row
    def scalar(sql):return c.execute(sql).fetchone()[0]
    def rows(sql):return [tuple(x) for x in c.execute(sql)]
    assert scalar("PRAGMA integrity_check")=="ok" and not rows("PRAGMA foreign_key_check")
    assert scalar("SELECT count(*) FROM chapters")==47
    primary=dict(rows("SELECT kind,count(*) FROM items WHERE chapter IN(15,27,33,43) GROUP BY kind"))
    assert primary=={"table":14,"figure":36,"appendix":3}
    for r in c.execute("SELECT dataset,row_count FROM datasets"):
        assert scalar('SELECT count(*) FROM "'+r[0]+'"')==r[1]
    assert rows("SELECT substr(sample,1,4),count(*) FROM c39_t2_corrected GROUP BY substr(sample,1,4)")==[("846B",264),("846D",2)]
    assert rows("SELECT hole,count(*) FROM c39_t2_cd GROUP BY hole")==[("844B",197)]
    assert rows("SELECT d18o,d13c FROM c43_appa_print WHERE section='846B-1H-1' AND offset_cm='33' ORDER BY row_no")==[('3.65','-0.10'),('3.88','-0.06')]
    assert rows("SELECT d18o,d13c FROM noaa_final WHERE depth_rmcd='0.330'")==[('3.765','-0.080')]
    assert scalar("SELECT count(*) FROM c23_t3_cd WHERE record_note!=''")==5
    # Cross-compare all 16 numeric columns, including blanks. Use publication units as the common reference.
    primary27=list(c.execute("SELECT * FROM c27_t1_print ORDER BY row_no"));external27=list(c.execute("SELECT * FROM pangaea_807824 ORDER BY row_no"))
    vnames="mbsf rmcd age_ka lsr_cm_ka wbd dbd bar tc_pct caco3_pct caco3_ar toc_pct toc_sd toc_ar_mg uk37 sst_c sst_sd".split()
    def dec(v):return None if v in ('','-9999.00') else D(v)
    diff27=[]
    for x,y in zip(primary27,external27,strict=True):
        assert re.sub(r'^138-846([A-D])-(\d+)H-',r'\1\2-',y["col_01"])==x['sample']
        for j,name in enumerate(vnames,2):
            a,b=dec(x[name]),dec(y[f"col_{j:02}"])
            if b is not None and name=="toc_ar_mg":b*=1000
            if a!=b:diff27.append((x['row_no'],name,str(a),str(b)))
    assert diff27==[(171,"sst_c","25.3","23.3")]
    # The second appendix block is compared by column position, without asserting species identities.
    pos33=Counter()
    ext33=list(c.execute("SELECT * FROM pangaea_808207 ORDER BY row_no"))
    for i,x in enumerate(list(c.execute("SELECT * FROM c33_app1_print ORDER BY row_no"))+list(c.execute("SELECT * FROM c33_app2_print ORDER BY row_no"))):
        y=ext33[i];keys=list(x.keys())[10:]
        dest=[y[f"col_{j:02}"] for j in [2,3,4,5,6,7,8,9,10,11 if i<239 else 12,13,14]]
        for name,v in zip(keys,dest,strict=True):
            if dec(x[name])!=dec(v):pos33[(x["print_page"],x["print_row"],name,x[name],v)]+=1
    assert list(pos33)==[(688,14,"rmcd","1.59","1.54"),(690,63,"rmcd","23.83","2383.00")]
    numfields="offset_cm depth_mbsf depth_mcd depth_rmcd d18o d13c".split()
    pc=list(c.execute("SELECT * FROM c43_appa_print ORDER BY row_no")); nc=list(c.execute("SELECT * FROM noaa_appendix_a ORDER BY row_no"));names43=0
    for x,y in zip(pc,nc,strict=True):
        assert all(dec(x[n])==dec(y[n]) for n in numfields)
        normalized=re.sub(r'846([bcd])0?(\d+)(h)(\d+)',r'846\1-\2\3-\4',y["section"]).upper()
        names43+=normalized!=x["section"]
    assert names43==21
    p43=rows("SELECT depth_rmcd,age_ma,rate_m_myr FROM c43_appb_print ORDER BY row_no")
    e43=rows("SELECT col_01,col_02,col_03 FROM pangaea_60253 ORDER BY row_no")
    for (a,b,e),(x,y,z) in zip(p43,e43,strict=True):assert D(a)==D(x) and D(b)*1000==D(y) and D(e)==D(z)*10
    p15=rows("SELECT age_ma,d18o,d13c FROM c15_t7_cd WHERE d18o!='-9999.00' ORDER BY row_no")
    e15=rows("SELECT col_01,col_02,col_03 FROM pangaea_696451 ORDER BY row_no")
    for (a,b,e),(x,y,z) in zip(p15,e15,strict=True):assert D(a)*1000==D(x) and D(b)==D(y) and dec(e)==dec(z)
    result={"chapters_indexed":47,"focus_items":primary,"data_editions":scalar("SELECT count(*) FROM datasets"),
            "edition_rows_including_parallel_releases_and_reference":scalar("SELECT sum(row_count) FROM datasets"),
            "ch27_table1_checked_numeric_positions":16*len(primary27),"ch27_numeric_differences":diff27,
            "ch33_print_pangaea_numeric_differences":[list(k) for k in pos33],"ch43_A_print_vs_NOAA_section_spelling_or_identifier_differences":names43,
            "ch43_A_numeric_positions_vs_NOAA":6*len(pc),"ch43_B_unit_converted_rows_vs_PANGAEA":len(p43),
            "ch15_T7_rows_corresponding_to_PANGAEA":len(p15),"ch15_T7_published_grid_rows":scalar("SELECT count(*) FROM c15_t7_cd"),
            "ch39_original_846":0,"ch39_corrected_846":266,"ch23_unresolved_datum_rows":5}
    if source_root:
        for s in c.execute("SELECT source,bytes,sha256 FROM sources"):
            content=(source_root/s[0]).read_bytes()
            assert len(content)==s[1] and hashlib.sha256(content).hexdigest()==s[2],s[0]
        n=0
        for name,key,edition in rows("SELECT dataset,source,edition FROM datasets WHERE edition!='print'"):
            encoding="utf-8-sig" if edition=="PANGAEA" else "latin1"
            ll=(source_root/key).read_bytes().decode(encoding).splitlines()
            for lo,hi,raw in rows('SELECT source_line,source_line_end,raw_literal FROM "'+name+'"'):
                assert 1<=lo<=hi<=len(ll) and raw=="\n".join(ll[lo-1:hi]),(name,lo,hi)
                n+=1
        result.update(source_files_hashed=scalar("SELECT count(*) FROM sources"),source_line_spans_verified=n)
    c.close();return result
if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--sources",type=Path);ap.add_argument("--db",type=Path,default=ROOT/"Site846_SR.sqlite")
    a=ap.parse_args();print(json.dumps(verify(a.db,a.sources),ensure_ascii=False,indent=2))
