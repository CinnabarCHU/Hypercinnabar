"""Check the assembled product, including all original control parents and tags."""
import json
from pathlib import Path
import re
import sys

import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[2]


def check(out):
    manifest = json.loads((out/"acycle-runtime.json").read_text())
    catalog = json.loads((out/"code/interface/catalogue.json").read_text())
    assert not list(out.rglob("*.fig"))
    # Only active MATLAB statements matter. Results saved by users may be .fig files.
    guide = re.compile(r"(?im)^\s*(?!%)[^%\n]*?\b(?:gui_mainfcn|guidata|guihandles)\s*\(")
    for path in out.rglob("*.m"):
        source = path.read_text(encoding="utf-8-sig",errors="replace")
        assert not guide.search(source), f"Designer dependency in {path}"
    assert len(catalog["engines"]) == manifest["operations"] == 516
    entries = [m for m in catalog["menus"] if m["entry"]]
    assert len(entries) == manifest["menuGroups"] == 118
    for m in entries:
        name = m["entry"][6:]
        wrapper = out/"matlab/+accli"/(name[0].lower()+name[1:]+".m")
        assert f"'{m['tag']}'" in wrapper.read_text(), m["tag"]
    controls = 0
    for tree in manifest["revisions"]:
        src = ROOT/"upstream"/tree
        original = sorted(src.rglob("*.fig"))
        assert {str(p.relative_to(src)) for p in original} == set(manifest["windows"][tree])
        for fig in original:
            layout = out/"upstream"/tree/fig.parent.relative_to(src)/("aclayout_"+fig.stem+".m")
            code = layout.read_text()
            root = loadmat(fig,squeeze_me=True,struct_as_record=False)
            nodes = [(root[next(k for k in root if k.startswith("hgS_"))],None)]
            names = {}
            serial = 0
            while nodes:
                node,parent = nodes.pop()
                if node.type in ("text","scribe.scribeaxes"):
                    continue
                serial += 1
                symbol = "fig" if parent is None else f"c{serial}"
                constructor = "uibuttongroup" if node.type == "uitools.uibuttongroup" else node.type
                header = f"{symbol} = {constructor}("
                if parent is not None:
                    header += f"'Parent',{parent},"
                assert header in code, (layout,node.type,parent)
                line = next(line for line in code.splitlines() if line.startswith(header))
                position = getattr(node.properties,"Position",None)
                if position is not None:
                    match = re.search(r"'Position',\[([^\]]+)\]",line)
                    assert match and np.allclose(np.fromstring(match[1],sep=" "),position,rtol=1e-14,atol=1e-14), (layout,node.type,"Position")
                for prop in ("Label","Style","Units","Separator","Accelerator","Checked","Enable","Visible"):
                    raw = getattr(node.properties,prop,None)
                    if isinstance(raw,str) and raw and not (parent is None and prop=="Visible"):
                        literal = "'" + raw.replace("'","''") + "'"
                        assert f"'{prop}',{literal}" in line, (layout,node.type,prop,raw)
                tag = getattr(node.properties,"Tag",None)
                if isinstance(tag,str) and re.fullmatch(r"[A-Za-z]\w*",tag):
                    assert f"h.{tag} = {symbol};" in code, (layout,tag)
                    names[tag] = symbol
                nodes.extend((child,symbol) for child in reversed(list(np.atleast_1d(node.children).flat)))
            controls += serial
    print(f"Checked {controls} graphics objects across both revisions, {len(entries)} feature wrappers and all 516 selectors.")


if __name__ == "__main__":
    check(Path(sys.argv[1]))
