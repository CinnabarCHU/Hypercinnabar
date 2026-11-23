"""Build a portable, code-only Acycle distribution from two pinned revisions."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from layout import emit_layout
from integrate import integrate

ROOT = Path(__file__).resolve().parents[2]
PINS = {"acycle": "b52ea9f510f3be00bde9a0238b9898a1e2315b74", "master": "dcba4279168745b563e0535b954297023dd62fc7"}
INITIALIZATION = re.compile(r"(?ms)^% Begin initialization code.*?^% End initialization code[^\n]*")


def convert(src, dest, tree):
    ignored = shutil.ignore_patterns(".git", "*.fig", "__pycache__", ".DS_Store", "ac_pwd*.txt")
    shutil.copytree(src, dest, ignore=ignored)
    if tree == "master":
        # Unreferenced development backup with no matching layout in this revision.
        (dest/"code/guicode/spectrumBKUP.m").unlink()
    inventory = {}
    for fig in sorted(src.rglob("*.fig")):
        rel = fig.relative_to(src)
        target = (dest / rel).with_suffix(".m")
        inventory[str(rel)] = emit_layout(fig,target.parent)
        s = target.read_text(encoding="utf-8-sig")
        name = fig.stem
        launcher = f"""% Code-only entry. All window state belongs to its figure.
if nargin && (ischar(varargin{{1}}) || isstring(varargin{{1}}))
    [varargout{{1:nargout}}] = feval(varargin{{:}});
    return
end
[varargout{{1:nargout}}] = acgui.window('{name}',@aclayout_{name},@{name}_OpeningFcn,@{name}_OutputFcn,varargin{{:}});"""
        s, n = INITIALIZATION.subn(launcher,s)
        if n != 1:
            raise ValueError(f"{rel}: expected one serialized launcher")
        target.write_text(s,encoding="utf-8")
    for f in dest.rglob("*.m"):
        raw = f.read_bytes()
        # Preserve non-UTF8 scientific resources verbatim if they need no edit.
        if b"guidata" in raw.lower():
            raw = re.sub(rb"\bguidata(?=\s*\()",b"acgui.state",raw,flags=re.I)
            f.write_bytes(raw)
        if re.search(rb"(?im)^\s*[^%\r\n]*\bgui_mainfcn\s*\(",raw):
            raise ValueError(f"GUIDE launcher escaped conversion: {f}")
    integrate(dest,tree)
    return inventory


def assemble(dest):
    windows = {}
    for tree, pin in PINS.items():
        src = ROOT / "upstream" / tree
        actual = subprocess.check_output(["git","-C",str(src),"rev-parse","HEAD"],text=True).strip()
        if actual != pin:
            raise ValueError(f"Initialize upstream/{tree} at {pin} before building")
        windows[tree] = convert(src,dest/"upstream"/tree,tree)
    for name in ("code","matlab","upstream/recovered","upstream/compatibility"):
        shutil.copytree(ROOT/name,dest/name)
    for name in ("ac.m","setup_acycle.m","LICENSE"):
        shutil.copyfile(ROOT/name,dest/name)
    shutil.copyfile(ROOT/"migration/poc/native.m",dest/"code/method/acMenuNative.m")
    shutil.copyfile(ROOT/"migration/poc/README.zh-CN.md",dest/"README.zh-CN.md")
    # Function-specific MATLAB wrappers for all menus, generated from the same register.
    catalog = json.loads((dest/"code/interface/catalogue.json").read_text())
    for menu in catalog["menus"]:
        if not menu["entry"]:
            continue
        stem = menu["entry"].removeprefix("acMenu")
        name = stem[:1].lower() + stem[1:]
        (dest/"matlab/+accli"/(name+".m")).write_text(
            f"function session = {name}(varargin)\n% {menu['guide'] or menu['master']}\n"
            f"session = accli.run('{menu['tag']}',varargin{{:}});\nend\n",encoding="utf-8")
    manifest = {"revisions":PINS,"windows":windows,"menuGroups":sum(bool(m["entry"]) for m in catalog["menus"]),
                "operations":len(catalog["engines"])}
    (dest/"acycle-runtime.json").write_text(json.dumps(manifest,indent=2)+"\n")
    if list(dest.rglob("*.fig")):
        raise ValueError("Runtime contains a serialized figure layout")
    return manifest


def build(target):
    target = target.resolve()
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists() and (not (target/"acycle-runtime.json").is_file() or target == ROOT):
        raise ValueError("Output must be new or an existing generated Acycle runtime")
    with tempfile.TemporaryDirectory(prefix=".acycle-build-",dir=target.parent) as temp:
        stage = Path(temp)/"runtime"
        stage.mkdir()
        manifest = assemble(stage)
        old = Path(temp)/"previous"
        if target.exists():
            target.rename(old)
        try:
            stage.rename(target)
        except OSError:
            if old.exists():
                old.rename(target)
            raise
    print(f"{len(manifest['windows']['acycle'])} code-only windows, {manifest['menuGroups']} menu groups, "
          f"{manifest['operations']} pinned operations: {target}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=Path,required=True)
    build(ap.parse_args().output)
