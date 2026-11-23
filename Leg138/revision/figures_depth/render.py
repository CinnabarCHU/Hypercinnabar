"""Reconstruct the Leg 138 shipboard sedimentation-rate diagrams from their TABLE files."""
import argparse
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

HERE = Path(__file__).resolve().parent
LEG = HERE.parents[1]
NUMBER = re.compile(r"\d+(?:\.\d+)?")
LINE_ENDINGS = {"CRLF": "\r\n", "LF": "\n", "CR": "\r", "": "", "NONE": ""}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def rows(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def save_csv(path, records):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, records[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def extract_tables(specs):
    native = {r["item_id"]: r for r in rows(LEG / "ir/core/native_tables.csv")}
    ids = {s["table_id"] for s in specs}
    by_id = {key: [] for key in ids}
    for r in rows(LEG / "ir/core/native_lines.csv.gz"):
        if r["item_id"] in ids:
            by_id[r["item_id"]].append(r)
    intervals = {}
    unmatched = []
    for key in sorted(ids):
        table = by_id[key]
        raw = "".join(r["raw_text"] + LINE_ENDINGS[r["line_ending"]] for r in table)
        source_hash = digest(raw.encode("latin-1"))
        meta = native[key]
        if len(table) != int(meta["line_count"]) or source_hash != meta["sha256"]:
            raise ValueError(f"{key}: reconstructed native file does not match its manifest")
        intervals[key] = []
        ties = []
        interleaved = key[:4] in {"IR09", "IR11", "IR12", "IR18"}
        pending = None
        for rec in table:
            line = rec["raw_text"].strip()
            tokens = []
            for word in line.split():
                if not NUMBER.fullmatch(word):
                    break
                tokens.append(word)
            if not tokens:
                continue
            ln = rec["line_number"]
            if interleaved and len(tokens) == 1:
                if pending is not None:
                    raise ValueError(f"{key}:{ln}: unexpected consecutive free-standing rates")
                pending = (tokens[0], ln)
                continue
            if interleaved:
                if len(tokens) != 2:
                    raise ValueError(f"{key}:{ln}: unsupported interleaved layout")
                d, a = tokens
                v, rate_ln = pending or ("", "")
                pending = None
            elif len(tokens) == 2:
                d, a = tokens
                v, rate_ln = "", ""
            elif len(tokens) == 3:
                # Printed CHAP_10 Table 10 identifies the second column as
                # rate and the third as age, contrary to the electronic header.
                d, v, a = tokens
                rate_ln = ln
            else:
                raise ValueError(f"{key}:{ln}: unexpected data line")
            ties.append(dict(depth=d, age=a, line=ln, rate=v, rate_line=rate_ln))
        if pending or len(ties) < 2:
            raise ValueError(key)
        for i, (top, base) in enumerate(zip(ties, ties[1:]), 1):
            # Table 7 at Site 854 writes the rate on the upper anchor line.
            rate_row = top if key == "IR19.T07" else base
            v = rate_row["rate"]
            a0, a1 = float(top["age"]), float(base["age"])
            d0, d1 = float(top["depth"]), float(base["depth"])
            if not a1 > a0 or not d1 > d0:
                raise ValueError(f"{key}: reversed anchors")
            intervals[key].append(dict(table_id=key, site=meta["site"], interval=i,
                native_source="ir/primary/"+meta["source_path"], native_sha256=source_hash,
                top_line=top["line"], base_line=base["line"], rate_line=rate_row["rate_line"],
                top_ma=top["age"], base_ma=base["age"], top_mcd=top["depth"],
                base_mcd=base["depth"], rate_m_per_myr=v,
                endpoint_quotient_m_per_myr=f"{(d1-d0)/(a1-a0):.6f}",
                role="published_interval_rate" if v else "published_rate_blank"))
        if key == "IR19.T07":
            last = ties[-1]
            unmatched.append(dict(table_id=key,source_line=last["line"],age_ma=last["age"],
                depth_mcd=last["depth"],rate_m_per_myr=last["rate"],
                reason="Table ends here. No second control point for this forward rate."))
    return intervals, unmatched


def series(spec, values):
    coordinate_keys = ("top_ma","base_ma") if spec["axis"] == "age" else ("top_mcd","base_mcd")
    upper = spec["omit_after"]
    out = []
    for interval in values:
        y0, y1 = (float(interval[k]) for k in coordinate_keys)
        if upper is not None:
            if y0 >= upper:
                continue
            y1 = min(y1, upper)
        out.append((float(interval["rate_m_per_myr"]) if interval["rate_m_per_myr"] else None,
                    y0, y1, int(interval["interval"])))
    return out


def render(spec, segments, path):
    left0, top0, right0, bottom0 = spec["frame_pdf_xyxy_pt"]
    cx, cy = spec["caption_pdf_xy_pt"]
    w, h = right0-left0, bottom0-top0
    margin_l = max(36.0, left0-cx+3)
    margin_t = 27.0
    cw = margin_l+w+8.0
    ch = margin_t+(cy-top0)+len(spec["caption_lines"])*9+8
    c = Canvas(str(path), pagesize=(cw,ch), invariant=1, pageCompression=1)
    c.setTitle(spec["item_id"]+" | Sedimentation-rate diagram, ODP Leg 138")
    c.setAuthor("Leg 138 digital collation; plotted from "+spec["table_id"])
    c.setSubject("Independent vector replot of published TABLE values. See figure manifest for print differences.")
    left, top = margin_l, ch-margin_t
    right, bottom = left+w, top-h
    x_max, y_max = spec["x_max"], spec["y_max"]
    def x(v):
        return left + w*v/x_max
    def y(v):
        return top - h*v/y_max
    c.setFont("Helvetica",7)
    c.setLineWidth(.52)
    c.rect(left,bottom,w,h)
    for i in range(int(x_max*2/spec["x_major"])+1):
        v=i*spec["x_major"]/2
        length=3.7 if not i%2 else 1.9
        c.line(x(v),top,x(v),top-length)
        c.line(x(v),bottom,x(v),bottom+length)
        if not i%2:
            c.drawCentredString(x(v),top+2.5,f"{v:g}")
    for i in range(int(y_max*2/spec["y_major"])+1):
        v=i*spec["y_major"]/2
        length=3.7 if not i%2 else 1.9
        c.line(left,y(v),left+length,y(v))
        c.line(right,y(v),right-length,y(v))
        if not i%2:
            c.drawRightString(left-3,y(v)-2.3,f"{v:g}")
    c.setFont("Helvetica",8.2)
    c.drawCentredString((left+right)/2,top+13,"Sedimentation rate (m/m.y.)")
    c.saveState()
    c.translate(left-23.5,(top+bottom)/2)
    c.rotate(90)
    c.drawCentredString(0,0,spec["label"])
    c.restoreState()
    c.saveState()
    frame=c.beginPath()
    frame.rect(left,bottom,w,h)
    c.clipPath(frame,stroke=0)
    c.setLineWidth(.76)
    line=c.beginPath()
    previous=None
    for value,a,b,_index in segments:
        if value is None:
            previous=None
            continue
        if previous == a:
            line.lineTo(x(value),y(a))
        else:
            line.moveTo(x(value),y(a))
        line.lineTo(x(value),y(b))
        previous=b
    c.drawPath(line)
    c.restoreState()
    c.setFont("Times-Roman",8.1)
    for i,line in enumerate(spec["caption_lines"]):
        text = c.beginText(left+cx-left0,top-(cy-top0)-6.3-i*9)
        text.setFont("Times-Roman",8.1)
        available_width = cw - 2 - (left+cx-left0)
        text.setHorizScale(100*min(1, available_width/stringWidth(line,"Times-Roman",8.1)))
        text.textOut(line)
        c.drawText(text)
    c.showPage()
    c.save()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,default=HERE)
    args=p.parse_args()
    out=args.out
    (out/"plots").mkdir(parents=True,exist_ok=True)
    specs=json.loads((HERE/"layout.json").read_text())
    tables,unmatched=extract_tables(specs)
    save_csv(out/"intervals.csv",[r for key in sorted(tables) for r in tables[key]])
    save_csv(out/"unbounded_rates.csv",unmatched)
    for s in specs:
        render(s, series(s,tables[s["table_id"]]),out/"plots"/(s["item_id"]+".pdf"))


if __name__ == "__main__":
    main()
