"""Check source payloads, printed-page mappings, visual readings and figure grafts.

Usage: python revision/verify_release.py ARCHIVE_ROOT PAIRED_EDITION
ARCHIVE_ROOT is the Leg138 tree with the published witnesses materialized. Both
public reading volumes and the privately regenerable SP/PR readings are checked.
"""
import argparse
import csv
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import fitz
from lxml import html

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "edition2"))
from revisions import checked_lines, figure_edits, page_blocks, partially_collated, readings
from page_text import runs

DPI = 144


def require(ok, *context):
    if not ok:
        raise ValueError(": ".join(map(str, context)))


def csv_rows(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


@lru_cache(maxsize=None)
def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def addr(line):
    return tuple(int(line[k]) for k in ("block", "line", "part"))


def render_equal(p, q):
    if p.rect != q.rect:
        return False
    matrix=fitz.Matrix(DPI/72,DPI/72)
    first=p.get_pixmap(matrix=matrix,colorspace=fitz.csRGB,annots=False)
    second=q.get_pixmap(matrix=matrix,colorspace=fitz.csRGB,annots=False)
    return first.width==second.width and first.height==second.height and first.samples_mv==second.samples_mv


def check_witness(source, witness, label, counts):
    require(source.rect == witness.rect, label, "page geometry")
    require(source.read_contents() == witness.read_contents(), label, "decoded drawing streams")
    flags=fitz.TEXTFLAGS_TEXT
    require(source.get_text("text",flags=flags)==witness.get_text("text",flags=flags),label,"publisher OCR")
    originals=source.get_images(full=True)
    copies=witness.get_images(full=True)
    require(len(originals)==len(copies),label,"image-stream count")
    for a,b in zip(originals,copies):
        require(a[2:9]==b[2:9] and source.parent.xref_stream_raw(a[0])==witness.parent.xref_stream_raw(b[0]),
                label,"original image payload")
        counts["source_image_streams_preserved"]+=1
    counts["source_witness_pages_preserved"]+=1


def declared_figure_hashes(f):
    inputs=f["inputs"].split("|")
    if f.get("input_sha256"):
        hashes=f["input_sha256"].split("|")
        require(len(hashes)==len(inputs),f["item_id"],"input hash cardinality")
        yield from zip(inputs,hashes)
    for path_field, hash_field in (("native_source","native_sha256"),("calibration_source","calibration_sha256")):
        if f.get(hash_field):
            yield f[path_field],f[hash_field]
    for hash_field,fragment in (("chem_sha256","/CHEM/"),("ir_table_sha256","/TABLES/")):
        if f.get(hash_field):
            matches=[rel for rel in inputs if fragment in rel]
            require(len(matches)==1,f["item_id"],hash_field,matches)
            yield matches[0],f[hash_field]


def check_manifest(root,out,figures,inventory,docs):
    register={r["item_id"]:r for r in csv_rows(root/"data/figure_reproduction.csv")}
    expected={}
    for name,f in figures.items():
        idx=register[name]
        doc=docs[idx["doc_id"]]
        witness=doc["source_local"]
        declared=f.get("source_pdf_sha256") or f["source_sha256"]
        require(declared==doc["source_pdf_sha256"]==inventory[witness]["sha256"],name,"witness hash")
        require(f.get("source_path",witness)==witness,name,"witness path")
        pages=list(map(int,(f.get("source_pages") or f["source_page"]).split("|")))
        require(len(set(pages))==len(pages) and pages[0]==int(f["source_page"]) and
            set(pages)<=set(map(int,idx["source_pdf_pages"].split("|"))),name,"source-page anchor")
        for rel in f["inputs"].split("|"):
            require((root/rel).is_file(),name,"missing input",rel)
            if rel in inventory:
                require(sha(root/rel)==inventory[rel]["sha256"],name,"input/external inventory",rel)
        for rel,expected_sha in declared_figure_hashes(f):
            require(sha(root/rel)==expected_sha,name,"declared source hash",rel)
        output_hash=f.get("output_sha256") or f.get("plot_sha256") or f["pdf_sha256"]
        require(sha(root/f["output"])==output_hash,name,"vector file hash")
        with fitz.open(root/f["output"]) as vector:
            require(len(vector)==len(pages),name,"source to asset page cardinality")
        for j,n in enumerate(pages,1):
            expected[name,n]=(idx["doc_id"],j,output_hash)
    mounts=defaultdict(list)
    for r in csv_rows(out/"resources.csv"):
        if r["kind"] in ("figure","card"):
            mounts[r["doc_id"],int(r["source_page"])].append(r)
    actual={(r["item_id"],n):(doc,int(r["asset_page"]),r["sha256"])
        for (doc,n),items in mounts.items() for r in items if r["representation"]=="source_data_replot"}
    require(actual==expected,"source-to-graft mappings",set(actual)^set(expected))
    return mounts


def html_styles(element):
    """Read the effective styles at every Unicode codepoint, including nested scripts."""
    tags={"i":"italic","b":"bold","sub":"subscript","sup":"superscript","u":"underline"}
    output=[]
    def visit(node,active):
        style=tags.get(node.tag)
        styles=active | {style} if style else active
        output.extend([styles]*len(node.text or ""))
        for child in node:
            visit(child,styles)
            output.extend([styles]*len(child.tail or ""))
    visit(element,frozenset())
    return output


def check_text(source, ledger, proof, fields, section, counts):
    doc,n=ledger["doc_id"],ledger["source_page"]
    packets=ledger["packets"]
    # Reread the PDF text layer and positional IDs instead of trusting the ledger.
    require(runs(source)[1]==packets,doc,n,"source packet/range mismatch")
    physical={addr(line):line for pk in packets for line in pk["lines"]}
    require(ledger.get("visual_collation")==proof,doc,n,"visual collation in audit")
    require({addr(r):r for r in ledger.get("line_collations",[])}==fields,doc,n,"field collation in audit")
    article=section.xpath('./div[@class="article"]')[0]
    elements=article.xpath('./p | ./h3 | ./div[@class="table-scroll"]/table/caption | '
                           './div[@class="table-scroll"]/table/*/tr')
    actual=["".join(x.itertext()) for x in elements]
    if proof:
        source_hash=sha(Path(source.parent.name))
        require(proof["witness_sha256"]==source_hash,doc,n,"reading source hash")
        visible=page_blocks(proof,packets,fields)
        require(actual==[r["text"] for r in visible],doc,n,"HTML reading or ordering")
        require(all(b["text"] in actual for b in proof["blocks"]),doc,n,"missing visual text block")
        for element,block in zip(elements,visible):
            if block["role"] in ("table_header","table_row"):
                cells=list(element)
                expected_tag="th" if block["role"]=="table_header" else "td"
                require(element.tag=="tr" and all(cell.tag==expected_tag for cell in cells)
                        and ["".join(cell.itertext()) for cell in cells]==block["text"].split("\t"),
                        doc,n,block["id"],"printed table cells")
                if block["id"]=="SR.C15.p018.b005":
                    require([int(c.get("colspan","1")) for c in cells]==[1,3,2,2],doc,n,"orbital period header spans")
                counts["collated_table_rows_checked_in_html"]+=1
                counts["blank_collated_table_cells_checked_in_html"]+=sum(not "".join(c.itertext()) for c in cells)
            if spans:=block.get("inline_styles"):
                expected=[set() for _ in block["text"]]
                for span in spans:
                    for pos in range(span["begin"],span["end"]):
                        expected[pos].add(span["style"])
                require(html_styles(element)==expected,doc,n,block.get("id"),"HTML inline style spans")
                counts["inline_style_spans_verified_in_html"]+=len(spans)
        if proof.get("overlay_only"):
            occupied=set()
            for block in proof["blocks"]:
                claimed=[tuple(a) for a in block["source_addresses"]]
                require(claimed and len(set(claimed))==len(claimed) and
                    set(claimed)<=physical.keys() and occupied.isdisjoint(claimed),doc,n,block["id"],"partial block anchors")
                occupied.update(claimed)
            counts["partial_overlay_pages"]+=1
            counts["partial_overlay_source_addresses_checked"]+=len(occupied)
        counts["visually_collated_pages_with_stated_scope"]+=1
        counts["visually_collated_blocks_checked_in_html_and_audit"]+=len(proof["blocks"])
        counts["inline_style_spans_in_source_ledger"]+=sum(len(b.get("inline_styles",[])) for b in proof["blocks"])
    elif fields:
        expected=[t for _,t in partially_collated(packets,fields,sha(Path(source.parent.name)))]
        require(actual==expected,doc,n,"field-only HTML reading")
    for address,f in fields.items():
        require(physical[address]["text"]==f["publisher"],doc,n,address,"field source text")
        bounds=list(map(float,f["bbox_pt"].split()))
        require(len(bounds)==4 and all(abs(x-y)<=.02 for x,y in zip(bounds,physical[address]["bbox"])),
                doc,n,address,"field source position")
        require(f["witness_sha256"]==sha(Path(source.parent.name)),doc,n,address,"field source hash")
        require(any(f["reading"] in text for text in actual),doc,n,address,"field reading missing from HTML")
    counts["visually_checked_hole_header_lines"]+=len(fields)
    counts["hole_header_pages"]+=bool(fields)
    counts["hole_header_pages_without_page_level_collation"]+=bool(fields and not proof)


def check_epoch_table(root, section, pdf, first, last):
    """Compare every field and style of the unnumbered p. 285 table in both readers."""
    rows=csv_rows(root/"revision/text_ir/epoch_boundaries.csv")
    fields=("boundary_as_printed","hole","mbsf","mcd","event_as_printed")
    expected=[["Boundary","Hole","Depth (mbsf)","Depths (mcd)","Event"],
              *[[r[k] for k in fields] for r in rows]]
    require(len(rows)==5,"IR.C11 p21 epoch count")
    tables=section.xpath('./div[@class="article"]/div[@class="table-scroll"]/table')
    require(len(tables)==1,"IR.C11 p21 epoch table")
    table=tables[0]
    intro=table.getparent().getprevious()
    note=table.getparent().getnext()
    require(intro.tag=="p" and table.get("aria-labelledby")==intro.get("id") and
            intro.text_content()=="Epoch boundaries are best approximated in Hole 846B as follows:",
            "IR.C11 p21 epoch table introduction")
    require(note.text_content()=="Note: B = begin, T = terminate.","IR.C11 p21 epoch table note")
    actual=[[c.text_content() for c in tr] for tr in table.xpath("./thead/tr | ./tbody/tr")]
    require(actual==expected,"IR.C11 p21 epoch fields in HTML vs. released CSV")

    # PDF cells must share a baseline in printed field order. A text-only check
    # would also pass when all five fields were concatenated into a paragraph.
    pdf_rows=[]
    for n in range(first,last+1):
        for block in pdf[n-1].get_text("dict")["blocks"]:
            for line in block.get("lines",[]):
                spans=line["spans"]
                pdf_rows.append((n,spans[0]["origin"][1],line["bbox"][0],
                                 "".join(s["text"] for s in spans),spans))
    previous=(0,0)
    for i,values in enumerate(expected):
        anchors=[(n,y) for n,y,_,text,_ in pdf_rows if text==values[0]]
        require(len(anchors)==1 and anchors[0]>previous,"IR.C11 p21 epoch row anchor",i)
        previous=anchors[0]
        cells=sorted((x,text,spans) for n,y,x,text,spans in pdf_rows if n==previous[0] and abs(y-previous[1])<.2)
        require([t for _,t,_ in cells]==values,"IR.C11 p21 epoch fields and PDF alignment",i)
        if i:
            taxon=values[-1].split(" ",1)[1].removesuffix(" s.l.")
            italic="".join(s["text"] for s in cells[-1][2] if s["flags"]&2)
            require(italic==taxon,"IR.C11 p21 epoch taxon PDF emphasis",i)
    return len(rows)


def verify(root,out):
    inventory={r["local_path"]:r for r in csv_rows(root/"data/source_inventory.csv.gz")}
    docs={r["doc_id"]:r for r in csv_rows(out/"documents.csv")}
    catalog={r["doc_id"]:r for r in csv_rows(root/"publication/chapters/catalog.csv")}
    archival={r["doc_id"]:r for r in csv_rows(root/"publication/chapters/archival_readers.csv")}
    require(set(docs)==set(catalog),"compact publication coverage")
    require(set(docs)=={r["doc_id"] for r in csv_rows(root/"data/documents.csv")},"original document coverage")
    proofs=readings(root)
    fields=checked_lines(root)
    edits=figure_edits(root)
    mounts=check_manifest(root,out,edits,inventory,docs)
    data_pages=defaultdict(list)
    for row in csv_rows(out/"pages.csv"):
        data_pages[row["doc_id"]].append(row)
    counts=Counter(); reviewed=Counter(); variants=Counter()
    visited_proofs=set(); visited_fields=set()
    for doc,d in docs.items():
        origin=root/d["source_local"]
        edition=out/d["pdf"]
        cat=catalog[doc]
        compact=root/"publication/chapters"/cat["local_path"]
        require(sha(origin)==d["source_pdf_sha256"]==inventory[d["source_local"]]["sha256"],doc,"source PDF hash")
        require(sha(edition)==d["edition_pdf_sha256"],doc,"paired edition hash")
        require(sha(compact)==cat["sha256"] and compact.stat().st_size==int(cat["bytes"]),doc,"branch PDF hash/size")
        if doc in archival:
            require(sha(compact)==archival[doc]["sha256"],doc,"archival public reader")
        mapped=data_pages[doc]
        with fitz.open(origin) as original, fitz.open(edition) as full, fitz.open(compact) as public, gzip.open(out/"audit"/(doc+".jsonl.gz"),"rt",encoding="utf-8") as ledger:
            require(len(original)==int(d["source_pdf_pages"])==len(mapped),doc,"physical page count")
            require(len(full)==int(d["edition_pdf_pages"]) and len(public)==int(cat["reading_pages"]),doc,"edition count")
            if doc not in archival:
                require(len(full)-len(original)==len(public),doc,"compact retained page count")
            # Use libxml's UTF-8 parser, preserving inline-script and emphasis boundaries.
            tree=html.parse(out/d["html"],html.HTMLParser(encoding="utf-8"))
            sections={el.get("id"):el for el in tree.xpath("//section[@id]")}
            for n,r in enumerate(mapped,1):
                key=(doc,n)
                record=json.loads(next(ledger))
                require(int(r["source_page"])==n==record["source_page"] and record["doc_id"]==doc,doc,n,"page identity")
                src,wit=original[n-1],full[int(r["edition_witness"])-1]
                check_witness(src,wit,key,counts)
                if key in proofs or key in fields:
                    witness_url=d["source_url"].split("#")[0]
                    anchor=witness_url+"#page="+str(n)
                    if key in proofs:
                        require(proofs[key]["source_url"] in {anchor,witness_url},doc,n,"proof source URL")
                    require(all(f["source_url"]==anchor for f in fields.get(key,{}).values()),doc,n,"field source URL")
                    require("p"+str(n) in sections,doc,n,"HTML source anchor")
                    check_text(src,record,proofs.get(key),fields.get(key,{}),sections["p"+str(n)],counts)
                    if key==("IR.C11",21):
                        first,last=int(r["edition_first"]),int(r["edition_reading_last"])
                        section=sections["p21"]
                        counts["ir_epoch_rows_verified_in_html_csv_and_paired_pdf"]+=check_epoch_table(root,section,full,first,last)
                        if doc not in archival:
                            counts["ir_epoch_rows_verified_in_public_pdf"]+=check_epoch_table(root,section,public,first-n+1,last-n+1)
                    if key in proofs:
                        visited_proofs.add(key);reviewed[doc]+=1
                        if proofs[key].get("coverage_kind"):
                            variants[proofs[key]["coverage_kind"]]+=1
                    if key in fields:visited_fields.add(key)
                else:
                    require(not record.get("visual_collation") and not record.get("line_collations"),doc,n,"unexpected collation")
                mounted=mounts.get(key,[])
                require(len(mounted)==int(r["graphics_count"]),doc,n,"graft count")
                for offset,asset in enumerate(mounted,1):
                    if asset["representation"]!="source_data_replot":
                        continue
                    fid=asset["item_id"]
                    path=root/edits[fid]["output"]
                    require(sha(out/asset["file"])==asset["sha256"]==sha(path),fid,"resource copy")
                    with fitz.open(path) as fig:
                        leaf=fig[int(asset["asset_page"])-1]
                        dest=int(r["edition_reading_last"])+offset-1
                        require(render_equal(leaf,full[dest]),fid,n,"paired graft differs at 144 dpi")
                        if doc not in archival:
                            require(render_equal(leaf,public[dest-(n-1)]),fid,n,"public graft differs at 144 dpi")
                            counts["public_replot_grafts_pixel_identical"]+=1
                        counts["paired_replot_grafts_pixel_identical"]+=1
                    href="../"+asset["file"]+"#page="+asset["asset_page"]
                    require(sections["p"+str(n)].xpath(".//a[@href=$url]",url=href),fid,"missing HTML mounted figure")
            require(next(ledger,None) is None,doc,"extra audit rows")
        counts["branch_pdfs_intact"]+=1
    require(visited_proofs==set(proofs) and visited_fields==set(fields),"unverified editorial pages")
    return {"verification":"passed","pixel_test_dpi":DPI,"comparison":"RGB bitmap byte equality with annotations hidden",
        "revised_numbered_figures":len(edits),"documents":len(docs),"public_archival_readers":sorted(archival),
        **dict(sorted(counts.items())),"visually_collated_pages_by_document":dict(sorted(reviewed.items())),
        "coverage_kinds_where_declared":dict(sorted(variants.items())),
        "accounting":"Scoped page collations include partial overlays. Hole-header lines and their pages are counted separately."}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive_root",type=Path)
    parser.add_argument("paired_edition",type=Path)
    parser.add_argument("--output",type=Path,default=HERE/"verification.json")
    a=parser.parse_args()
    result=verify(a.archive_root.resolve(),a.paired_edition.resolve())
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
