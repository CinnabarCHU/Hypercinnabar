"""Rebuild the checked Site 846 isotope readings across the 19 physical chapter pages."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
import fitz

from build_ch30 import indices, native_lines, reflow, write_csv
from page_register import update_register
import ch15_other_pages as extra

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"edition2"))
from page_text import runs

def source_address_map(page):
    addresses = {}
    _,packets = runs(page)
    for packet in packets:
        for row in packet["lines"]:
            key = row["block"],row["line"]
            addresses.setdefault(key,[]).append([*key,row["part"]])
    result = {}
    for block in page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]:
        if "lines" not in block:
            continue
        for i,line in enumerate(block["lines"],1):
            bbox=tuple(round(v,2) for v in line["bbox"])
            raw="".join(span["text"] for span in line["spans"]).strip()
            key=(bbox,raw)
            result[key]=addresses.get((block["number"],i),[])
    return result


DOC = "SR.C15"
SHA = "d0f66756ed538ce258339351b9681cac13c2c43a686bd90460ae6071d298f705"
URL = "https://www-odp.tamu.edu/publications/138_SR/VOLUME/CHAPTERS/sr138_15.pdf"
SCOPE = {
    3: "Entire visible page, including the two columns, running matter and Table 2 with seven rows and note.",
    5: "Complete article text, Figure 1 caption and Table 4 with thirteen rows. Figure 1 graph, axes and internal labels excluded.",
    6: "Complete article text and Figure 2 caption. Figure 2 graph, axes and internal labels excluded.",
}
CARRY = {
    3: "Opens continuing the statistical discussion on p. 338. Boundary to p. 340 is a table page.",
    5: "Final sentence continues on p. 342.",
    6: "Opening paragraph continues from p. 341. Last sentence resumes after the following table leaf.",
}
# Range items are source-line ordinals; selected isotope fragments on the
# same baseline are then rejoined. Table cells have their own physical fields.
PLAN = {
 3:[("running_header","0"),("body","1-6"),("heading","7"),("body","8-23"),
    ("heading","24"),("body","25-47"),("body","48-63"),("caption","67"),
    ("table_header","68-70"),*[("table_row",s) for s in
      "71-73 74-76 77-79 80-82 83-85 86-87 88-90".split()],
    ("notice","91"),("heading","64"),("body","65-66 92-96"),
    ("body","97-118"),("body","119-130"),("body","131-143"),("body","144-150"),("folio","151")],
 5:[("running_header","0"),("caption","41-42"),("heading","43"),
    ("body","44-51"),("body","52-57"),("caption","58-62"),
    ("table_header","63 77 91-92 106-107"),
    *[("table_row",f"{64+k} {78+k} {93+k} {108+k}") for k in range(13)],("folio","121")],
 6:[("running_header","0"),("caption","40-41"),("body","42-51"),
    ("body","52-72"),("folio","73")],
}
SAME_LINE = {
 3:{13,43,52,54,55,57,62,108,112,115,118},
 5:{47,59,61},
 6:{48,51,69},
}
CHANGES={
 3:{
    13: [("3 sample","³ sample")],
    29: [('"mbsf\'','“mbsf”'),('"mcd"','“mcd”')],
    36: [('"rmcd"','“rmcd”')],46:[('"depth"','“depth”'),('"rmcd,"','“rmcd,”')],
    52: [("13C","¹³C")],54:[("13C","¹³C")],62:[("13C","¹³C")],
    71:[("Globigerinoidesfistulosus","Globigerinoides fistulosus")],
    80:[("FAT)","FAD")],
    121:[("65 °N","65°N")],143:[("65 °N","65°N")],
    131:[("1.7-3,3-4, and 4-5","1.7–3, 3–4, and 4–5")],
    140:[("1.7-3","1.7–3")],145:[('"rmcd"','“rmcd”')]
 },
 5:{42:[("inteΦolation","interpolation")],
    61:[("13C","¹³C")],92:[("1 8o","¹⁸O")],107:[("1 3c","¹³C")]},
 6:{0:[("NJ.","N.J.")],50:[("benthic 6","benthic δ")],51:[("18O","¹⁸O")],
    67:[("Gl (G","G1 (G")],68:[("C3n.ln.δ","C3n.1n.δ")],69:[("18O.l","¹⁸O.1")]}
}
PLAN.update(extra.PLAN)
SCOPE.update(extra.SCOPE)
CARRY.update(extra.CARRY)
CHANGES.update(extra.CHANGES)
SAME_LINE.update(extra.SAME_LINE)
TAXA=re.compile(r"\b(?:Globigerinoides fistulosus|Globorotalia limbata|Globoquadrina (?:altispira|dehiscens)|Sphaeroidinellopsis seminulina|Pulleniatina spectabilis|Uvigerina|Hoeglundina elegans|Cibicidoides(?: wuellerstorfi)?|C\. kullenbergi|Oridorsalis(?: umbonifera)?|JOIDES Resolution|U\. senticosa|C\. wuellerstorfi|G\. pacifica|Nothofagus|Globocassidulina subglobosa|C\. kull\.|C\. wuell\.|Nuttalides|Cib\.|Sphaeroidina bulloides|Gyroidina|Globobulimina pacifica)")
def corrected(page_n,line_n,text):
    fixed=text.replace("1 8θ","¹⁸O")
    for before,after in CHANGES.get(page_n,{}).get(line_n,[]):
        if fixed.count(before)!=1:
            raise ValueError(f"Unexpected source {page_n}:{line_n} {before}")
        fixed=fixed.replace(before,after)
    if page_n in extra.PLAN:
        if line_n == 0:
            fixed = fixed.replace("NJ. SHACKLETON","N.J. SHACKLETON")
        if page_n == 17:
            fixed = fixed.replace("Shackleton, NJ.","Shackleton, N.J.")
            fixed = re.sub(r"(?<=\d)-(?=\d)", "–", fixed)
            if line_n in (26,31):
                fixed = fixed.removesuffix("-")+"–"
            if line_n == 83:
                fixed=fixed.replace("V28–238","V28-238")
        fixed=re.sub(r"^(13C|18O)(?=\W|$)", lambda m: {"13C":"¹³C","18O":"¹⁸O"}[m.group()], fixed)
        if page_n == 18:
            if 277<=line_n<=289:
                fixed=fixed.replace("-", "–")
            if 306<=line_n<=364 and fixed.startswith("-"):
                fixed="−"+fixed[1:]
        fixed = fixed.replace("today's","today’s").replace("Keigwin's","Keigwin’s")
        fixed = re.sub(r'"([^"]+)"',r'“\1”',fixed)
        fixed = fixed.replace("'golden age'","‘golden age’").replace("'fill-in'","‘fill-in’")
    if page_n==5 and line_n in {94,98,102,109,117}:
        fixed=fixed.replace("-","−")
    return fixed

def collapse_row(page_n,role,numbers,raw,readings):
    if page_n==3 and numbers[0]==86:
        # Two separate right-column values share one native OCR segment.
        readings=[readings[0],*readings[1].split(" 846D ")]
        readings[2]="846D "+readings[2]
    if page_n==5 and role=="table_header":
        readings=[readings[0],readings[1],readings[2]+readings[3],readings[4]+readings[5]]
    return readings

def run(source, output):
    if hashlib.sha256(source.read_bytes()).hexdigest()!=SHA:
        raise ValueError("Source PDF checksum mismatch")
    output.mkdir(parents=True,exist_ok=True)
    pdf=fitz.open(source)
    table_id={3:2,5:4,18:8}
    pages, inventory, ledger, tables=[],[],[],[]
    for pn in sorted(PLAN):
        defs=PLAN[pn]
        nl=native_lines(pdf[pn-1])
        addresses=source_address_map(pdf[pn-1])
        if pn in (6,12):
            nl.append(((47,742,65,758),""))
        blocks=[]
        for bi,(role,spec) in enumerate(defs,1):
            bid=f"{DOC}.p{pn:03d}.b{bi:03d}"
            groups=[]
            for n in indices(spec):
                if role.startswith("table_") and groups:
                    groups[-1].append(n)
                elif n in SAME_LINE.get(pn,set()) and groups:
                    groups[-1].append(n)
                else:
                    groups.append([n])
            physical=[]
            for group in groups:
                raw=[nl[n][1] for n in group]
                words=[corrected(pn,n,t) for n,t in zip(group,raw)]
                before=(" ".join(raw) if role.startswith("table_") else "".join(raw))
                if role=="folio" and not before:
                    words=[str(336+pn)]
                if role.startswith("table_"):
                    words=(extra.table8_row(spec,words) if pn==18 else collapse_row(pn,role,group,raw,words))
                    read="\t".join(words)
                    tables.append(dict(object_id=f"{DOC}.TABLE{table_id[pn]}",source_page=pn,
                                  printed_page=336+pn,witness_sha256=SHA,block_id=bid,
                                  kind=role,fields_json=json.dumps(words,ensure_ascii=False,separators=(",",":"))))
                else:
                    read="".join(words)
                physical.append(read)
                boxes=[nl[n][0] for n in group]
                bound=[min(v[0] for v in boxes),min(v[1] for v in boxes),max(v[2] for v in boxes),max(v[3] for v in boxes)]
                ledger.append(dict(doc_id=DOC,source_page=pn,printed_page=pn+336,witness_sha256=SHA,block_id=bid,
                          native_line_ordinals=" ".join(str(n) for n in group) if any(raw) else "",
                          bbox_pt=json.dumps(bound,separators=(",",":")),native=before,diplomatic=read))
            if pn in extra.PLAN:
                text=extra.reflow_text(physical,pn,spec)
            else:
                text=reflow(physical)
            styles=[dict(begin=m.start(),end=m.end(),style="italic") for m in TAXA.finditer(text)]
            if role=="caption" and text.startswith("Table "):
                styles.insert(0,dict(begin=0,end=len(text),style="bold"))
            block=dict(id=bid,role=role,text=text,source_lines=physical,inline_styles=styles)
            if pn in extra.OVERLAY:
                block["source_addresses"]=[a for n in indices(spec) for a in addresses[nl[n]]]
                if not block["source_addresses"]:
                    raise ValueError(f"Missing source address for partial block {bid}")
            styles.extend(extra.print_styles(text,role,pn,spec))
            label=re.match(r"(Table|Figure) (\d+)\.",text) if role=="caption" else None
            if label:
                block["object_id"]=f"{DOC}.{label.group(1).upper()}{label.group(2)}"
            elif role.startswith("table_"):
                block["object_id"]=f"{DOC}.TABLE{table_id[pn]}"
            blocks.append(block)
        pages.append(dict(doc_id=DOC,source_page=pn,printed_page=pn+336,witness_sha256=SHA,
                     source_url=URL,review_scope=SCOPE[pn],continuation=CARRY[pn],overlay_only=pn in extra.OVERLAY,blocks=blocks))
        text_path=f"{DOC}.p{pn:03d}.txt"
        (output/text_path).write_text("\n\n".join("\n".join(b["source_lines"]) for b in blocks)+"\n",encoding="utf-8")
        inventory.append(dict(doc_id=DOC,source_page=pn,printed_page=pn+336,witness_sha256=SHA,
                 text_path=text_path,scope=SCOPE[pn],status="single_visual_read_against_publisher_scan",
                 source_lines=sum(len(b["source_lines"]) for b in blocks),blocks=len(blocks)))
    update_register(output,DOC,pages,inventory)
    write_csv(output/"ch15_line_evidence.csv",ledger)
    write_csv(output/"ch15_corrections.csv",[r for r in ledger if r["native"]!=r["diplomatic"]])
    write_csv(output/"ch15_printed_table_rows.csv",tables)

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source",type=Path)
    parser.add_argument("--output",type=Path,default=Path(__file__).parent)
    args=parser.parse_args()
    run(args.source,args.output)
