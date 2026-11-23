"""Rebuild the checked SR.C30 page transcription from its exact PDF witness.

The selected source lines, manual reading-order decisions and amendments below
refer to the publisher's digital witness. No OCR software runs in this build.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

import fitz

from page_register import update_register

SOURCE_SHA = "3b374885d08b1cc78a532aa0f75f969679e3f652a469df258c22b03240f1983b"
SOURCE_URL = "https://www-odp.tamu.edu/publications/138_SR/VOLUME/CHAPTERS/sr138_30.pdf"
DOC = "SR.C30"
OUT = Path(__file__).parent

# Ranges are inclusive ordinals of native non-image lines in PDF content order.
# Authors' paragraphs that span columns have a single block. Captions stand
# outside the prose thread. Physical line order is recoverable in line_evidence.
PLAN = {
    1: [
        ("notice", "0-1"), ("heading", "2-3"), ("byline", "4"),
        ("heading", "5"), ("body", "6-15"), ("heading", "16"),
        ("body", "17-37"), ("body", "38-44"), ("heading", "45-46"),
        ("body", "47-48 55-68"), ("body", "69-80"), ("heading", "81"),
        ("body", "82-95"), ("footnote", "49-50"), ("footnote", "51-52"),
        ("footnote", "53-54"), ("folio", "96"),
    ],
    2: [
        ("running_header", "0"), ("caption", "1-5"), ("caption", "55-56"),
        ("caption", "89-91"), ("body", "57-63"), ("body", "64-74"),
        ("heading", "75"), ("body", "76-78 92-97"), ("body", "98-117"),
        ("heading", "118"), ("body", "119-130"), ("folio", "131"),
    ],
    3: [
        ("running_header", "0"), ("caption", "11-20"), ("caption", "60-65"),
        ("body", "21-31"), ("body", "32-34"), ("heading", "35-38"),
        ("body", "39-52 66-69"), ("heading", "70-71"), ("body", "72-82"),
        ("body", "83-95"), ("heading", "96-97"), ("body", "98-106"),
        ("folio", "107"),
    ],
    4: [
        ("running_header", "0"), ("caption", "10-14"), ("body", "15-31"),
        ("body", "32-38"), ("heading", "39-40"), ("body", "41-56"),
        ("body", "57-65"), ("body", "66-76"), ("heading", "77"),
        ("body", "78-90"), ("body", "91-102"), ("body", "103-108"),
        ("folio", "109"),
    ],
    5: [
        ("running_header", "0"), ("body", "1-3"), ("heading", "4"),
        ("body", "5-15"), ("heading", "16"), ("body", "17-21"),
        ("heading", "22"),
        *[("reference", n) for n in (
            "23-26 27-28 29-30 31-34 35-36 37-39 40-41 42-43 44-46 "
            "47-48 49-51 52-54 55-56 57-59 60-61 62-63 64-65 66-67 "
            "68-71 72-73 74-76 77-81 82-84 85-86 87-88 89-90 91-94 "
            "95-97 98-102 103-105 106-109 110-111 112-113 114-116 "
            "117-119 120-122 123-124 125-127 128-129"
        ).split()],
        ("footnote", "130-132"), ("notice", "133"), ("notice", "134"),
        ("notice", "135"), ("folio", "136"),
    ],
}

# Entries must match exactly once in the selected source line.
CHANGES = {
    (1, 3): [("OCEAN1", "OCEAN¹")],
    (1, 4): [("Kemp,2", "Kemp,²"), ("Baldauf,3", "Baldauf,³"), ("Pearce2", "Pearce²")],
    (1, 11): [("La Nina (anti-El Nino)", "La Niña (anti-El Niño)")],
    (1, 24): [("et al,", "et al.,")],
    (1, 44): [("et al,", "et al.,")],
    (1, 49): [("Pisias,", "¹ Pisias,")],
    (1, 51): [("2 Department", "² Department")],
    (1, 53): [("3 Department", "³ Department")],
    (1, 58): [("13-12", "13–12"), ("10-9.5", "10–9.5"), ("6.3-6.1", "6.3–6.1")],
    (1, 75): [("et al,", "et al.,")],
    (2, 66): [("I03 to I06", "10³ to 10⁶")],
    (2, 93): [("4.4/m3", "4.4/m³")],
    (2, 99): [("anti-El Nino or La Nina", "anti-El Niño or La Niña"), ("the El Nino", "the El Niño")],
    (2, 129): [("La Nina (anti-El Nino)", "La Niña (anti-El Niño)")],
    (3, 23): [("El Nino/La", "El Niño/La")],
    (3, 24): [("Nina cycles", "Niña cycles")],
    (3, 69): [("mesh work", "meshwork")],
    (3, 103): [("andBurckle,", "and Burckle,"), ("1975;Gombos,", "1975; Gombos,")],
    (4, 100): [("Oceano-", "oceano-")],
    (5, 42): [("Chavez, FP,", "Chavez, F.P.,")],
    (5, 75): [("Bull,", "Bull.,")],
    (5, 77): [("Hagelberg, T, Dadey, K,", "Hagelberg, T., Dadey, K.,")],
    (5, 85): [("Janecek, T,", "Janecek, T.,")],
    (5, 87): [("Theyer, F,", "Theyer, F.,")],
    (5, 91): [("Theyer, F,", "Theyer, F.,")],
    (5, 93): [("Theyer, F,", "Theyer, F.,")],
    (5, 96): [("global Oceanographic", "global oceanographic")],
    (5, 98): [("Muller,", "Müller,"), ("Ciesielski, PE,", "Ciesielski, P.F.,")],
    (5, 99): [("9.8^1.5", "9.8–4.5")],
    (5, 101): [("Kristoffersen, Y,", "Kristoffersen, Y.,")],
    (5, 103): [("Sancetta, C,", "Sancetta, C.,")],
    (5, 106): [(", 1983.", "———, 1983.")],
    (5, 110): [("Sancetta, C, Villareal, T,", "Sancetta, C., Villareal, T.,")],
    (5, 119): [("Geol,", "Geol.,")],
    (5, 128): [("Wyrtki, K,", "Wyrtki, K.,")],
    (5, 130): [("Abbreviations", "* Abbreviations")],
}
# Modern-reader font markup positions use Unicode code point offsets.
# Raised digits use Unicode superscript glyphs directly. This preserves meaning
# when all markup is discarded; they must not be elevated a second time.
TAXA = re.compile(
    r"\b(?:Thalassiothrix(?: (?:longissima|antarctica))?|T\. (?:longissima|acuta|heteromorpha|antarctica)"
    r"|Rhizosolenia|Bruniopsis mirabilis|B\. mirabilis|Ethmodiscus(?: rex)?|E\. rex|Thalassionema"
    r"|Synedra Reinboldii|en masse|ad hoc|Atlantis)\b"
)
JOURNALS = (
    "Proc. ODP, Sci. Results", "Proc. ODP, Init. Repts.", "Proc. ODP, Init. Repts",
    "Init. Repts. DSDP", "Geological History of the Polar Oceans: Arctic versus Antarctic",
    "Pacific Neogene Events: Their Timing, Nature and Interrelationship",
    "Geol. Soc. Am. Bull.", "U.S. JGOFS News", "Ambio", "J. Geol.",
    "Deep-Sea Res. Part A", "Micropaleontology", "Geol. Soc. Spec. Publ. London",
    "Diatom Res.", "Paleoceanography", "Disc. Rep.", "Science", "Nature",
    "Limnol. Oceanogr.", "Oikos", "Mar. Geol.", "Mem.—Geol. Soc. Am.",
    "J. Plankt. Res.", "J. Phys. Oceanogr.",
)
CARRY = {
    1: "Final prose continues on page 642 (T. heteromorpha).",
    2: "First prose continues from page 641. Final word breaks across pages: alterna- | tions.",
    3: "Opening fragment completes alterna- on page 642. Final sentence continues on page 644.",
    4: "Opening sentence continues from page 643. Final sentence continues on page 645.",
    5: "Opening sentence continues from page 644.",
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def native_lines(page):
    return [
        (tuple(round(v, 2) for v in line["bbox"]), "".join(s["text"] for s in line["spans"]).strip())
        for block in page.get_text("dict")["blocks"] if "lines" in block for line in block["lines"]
    ]

def indices(spec):
    result = []
    for s in spec.split():
        parts = s.split("-")
        result.extend(range(int(parts[0]), int(parts[-1]) + 1))
    return result

def read_line(page_n, line_n, text, quote_state):
    fixed = text
    for old, new in CHANGES.get((page_n, line_n), ()):
        if fixed.count(old) != 1:
            raise ValueError(f"Unexpected native reading {page_n}:{line_n} {old!r}")
        fixed = fixed.replace(old, new)
    if page_n == 5 and 23 <= line_n <= 129:
        fixed = re.sub(r"(?<=\d)-(?=\d)", "–", fixed)
    # Double quotation marks printed as opening and closing marks in the
    # running text. Internal drawing labels are handled separately.
    out = []
    for char in fixed:
        if char == '"':
            out.append("“" if not quote_state[0] else "”")
            quote_state[0] = not quote_state[0]
        else:
            out.append(char)
    return "".join(out)

def reflow(lines):
    text = ""
    for line in lines:
        if text.endswith("-"):
            text = text[:-1] + line
        elif text.endswith("/"):
            text += line
        else:
            text = f"{text} {line}".strip()
    return text

def styles(text, role, page_n, spec):
    found = {(m.start(), m.end(), "italic") for m in TAXA.finditer(text)}
    if role == "reference":
        for term in JOURNALS:
            for m in re.finditer(re.escape(term), text):
                # In a title these strings may be words rather than journal names.
                if term in {"Paleoceanography", "Nature", "Science"} and (
                    text[m.end():].strip()[:1] not in {",", "."}
                ):
                    continue
                found.add((m.start(), m.end(), "italic"))
        for m in re.finditer(r"\bIn\b", text):
            found.add((m.start(), m.end(), "italic"))
    for key, term in {
        (1, "0-1"): "Proceedings of the Ocean Drilling Program, Scientific Results",
        (1, "49-50"): "Proc. ODP, Sci. Results",
        (5, "130-132"): "Chemical Abstracts Service Source Index",
    }.items():
        if (page_n,spec) == key:
            begin=text.index(term)
            found.add((begin, begin+len(term), "italic"))
    if page_n == 5 and (spec in {"133","134","135"}):
        found.add((0,len(text),"bold"))
    if page_n == 5 and spec in {"22","130-132"}:
        begin=text.index("*")
        found.add((begin,begin+1,"superscript"))
    if page_n == 2 and spec == "55-56":
        for label in ["A", "B"]:
            begin = text.index(f"({label})") + 1
            found.add((begin, begin+1, "bold"))
    # Union identical-style ranges e.g. a taxon nested in an italic book title.
    merged = []
    for style in ("italic", "bold", "superscript"):
        for begin,end,kind in sorted(found):
            if kind != style:
                continue
            if merged and merged[-1]["style"] == style and begin <= merged[-1]["end"]:
                merged[-1]["end"] = max(merged[-1]["end"],end)
            else:
                merged.append(dict(begin=begin,end=end,style=style))
    return sorted(merged,key=lambda i:(i["begin"],i["end"],i["style"]))

def write_csv(path, rows):
    with path.open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream, fieldnames=list(rows[0]),lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def run(source, output):
    if sha(source) != SOURCE_SHA:
        raise ValueError("Source PDF checksum mismatch")
    output.mkdir(parents=True,exist_ok=True)
    document = fitz.open(source)
    if len(document) != 5:
        raise ValueError("Expected five witness pages")
    pages, evidence, corrections, inventory = [], [], [], []
    for page_n,page in enumerate(document,1):
        native = native_lines(page)
        # Publisher OCR omits folios of the two verso pages altogether.
        if page_n in {2,4}:
            native.append(((47,744,65,758), ""))
        visited = set()
        blocks = []
        for seq,(role,spec) in enumerate(PLAN[page_n],1):
            quote_state = [False]
            bid = f"{DOC}.p{page_n:03d}.b{seq:03d}"
            lines=[]
            for line_n in indices(spec):
                assert line_n not in visited
                visited.add(line_n)
                box,original = native[line_n]
                if role=="folio" and not original:
                    corrected = str(640+page_n)
                else:
                    corrected = read_line(page_n,line_n,original,quote_state)
                info = dict(doc_id=DOC,source_page=page_n,printed_page=640+page_n,
                            witness_sha256=SOURCE_SHA,block_id=bid,native_line_ordinal=line_n if original else "",
                            bbox_pt=json.dumps(box,separators=(",",":")),native=original,diplomatic=corrected)
                evidence.append(info)
                if original!=corrected:
                    corrections.append(info)
                lines.append(corrected)
            if quote_state[0]:
                raise ValueError(f"Unmatched quotation in {bid}")
            block=dict(id=bid,role=role,text=reflow(lines),source_lines=lines)
            if role=="caption":
                block["object_id"]=f"{DOC}.FIGURE{int(block['text'].split()[1].rstrip('.'))}"
            block["inline_styles"]=styles(block["text"],role,page_n,spec)
            blocks.append(block)
        scope="Complete article text, including running matter, all captions, bibliography, affiliations and notes. In-figure labels are inventoried separately."
        pages.append(dict(doc_id=DOC,source_page=page_n,printed_page=640+page_n,
                          witness_sha256=SOURCE_SHA,source_url=SOURCE_URL,review_scope=scope,
                          continuation=CARRY[page_n],blocks=blocks))
        text_path=f"SR.C30.p{page_n:03d}.txt"
        (output/text_path).write_text("\n\n".join("\n".join(b["source_lines"]) for b in blocks)+"\n",encoding="utf-8")
        inventory.append(dict(doc_id=DOC,source_page=page_n,printed_page=640+page_n,
                              witness_sha256=SOURCE_SHA,text_path=text_path,
                              scope=scope,status="single_visual_read_against_publisher_scan",
                              source_lines=len(visited),blocks=len(blocks)))
    update_register(output,DOC,pages,inventory)
    write_csv(output/"line_evidence.csv",evidence)
    write_csv(output/"corrections.csv",corrections)

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source",type=Path)
    parser.add_argument("--output",type=Path,default=OUT)
    args=parser.parse_args()
    run(args.source,args.output)
