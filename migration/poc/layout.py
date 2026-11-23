"""Translate the pinned public graphics properties into MATLAB constructors."""
from collections import Counter
import re
from pathlib import Path

import numpy as np
from scipy.io import loadmat, savemat

# Internal graphics caches, rulers, default axes labels and scribe overlays are
# recreated by MATLAB. Only public appearance, interaction and layout are copied.
COMMON = "Tag Units Position Visible HandleVisibility"
FONT = "FontUnits FontName FontSize FontWeight FontAngle ForegroundColor BackgroundColor"
PROPS = {
    "figure": "Units Position Color Name NumberTitle MenuBar ToolBar Resize DockControls WindowStyle IntegerHandle HandleVisibility Tag",
    "uicontrol": "Style " + COMMON + " " + FONT + " HorizontalAlignment Min Max SliderStep String Value ListboxTop Enable TooltipString",
    "uipanel": COMMON + " " + FONT + " Title TitlePosition BorderType BorderWidth HighlightColor ShadowColor",
    "uitools.uibuttongroup": COMMON + " " + FONT + " Title",
    "uimenu": "Label Tag Separator Accelerator Checked Enable Visible",
    "uicontextmenu": "Tag",
    "axes": "Tag Units Position FontUnits FontName FontSize Color XColor YColor ZColor",
    "uitoolbar": "Tag",
    "uipushtool": "Tag CData Enable Separator TooltipString HandleVisibility",
    "uitoggletool": "Tag CData Enable Separator TooltipString HandleVisibility",
    "uitable": COMMON + " " + FONT + " ColumnName RowName ColumnFormat ColumnWidth ColumnEditable Data Enable TooltipString",
}
CALLBACK = re.compile(r"(\w+)\('(\w+)',\s*hObject,\s*eventdata,\s*guidata\(hObject\)\)")
# Two stale callbacks in the pinned assets have no corresponding source function.
STALE = {("DYNOS", "pushbutton4_ButtonDownFcn"), ("evofftGUI", "uipanel2_SelectionChangedFcn")}


def string(s):
    return "'" + s.replace("'", "''") + "'"


def emit_layout(fig_file, output):
    raw = loadmat(fig_file, squeeze_me=True, struct_as_record=False)
    root = raw[next(key for key in raw if key.startswith("hgS_"))]
    name = fig_file.stem
    func = "aclayout_" + name
    lines = [f"function [fig,h,init] = {func}()", "% Generated from public graphics properties at the pinned baseline.",
             "h = struct();", "init = {};"]
    callbacks, assets, counts = [], {}, Counter()
    source = fig_file.with_suffix(".m").read_text(encoding="utf-8-sig", errors="replace")
    serial = 0

    def expression(v, key):
        if isinstance(v, str) and "\n" not in v and "\r" not in v:
            return string(v)
        if np.size(v) == 0:
            return "''" if key in ("String", "Tag", "Accelerator", "TooltipString") else "[]"
        if isinstance(v, (int, float, np.number)):
            return str(v)
        a = np.asarray(v)
        if a.dtype.kind in "fiu" and a.ndim == 1 and a.size <= 8:
            return "[" + " ".join(format(float(x), ".17g") for x in a) + "]"
        if a.dtype.kind == "U" and a.ndim == 1:
            return "{" + ";".join(string(str(x).rstrip()) for x in a) + "}"
        key_asset = "v" + str(len(assets) + 1)
        assets[key_asset] = v
        return "a." + key_asset

    def walk(node, parent):
        nonlocal serial
        kind = node.type
        if kind in ("text", "scribe.scribeaxes"):
            return
        if kind not in PROPS:
            raise ValueError(f"{name}: unsupported node {kind}")
        serial += 1
        counts[kind] += 1
        obj = "fig" if parent is None else f"c{serial}"
        typ = "uibuttongroup" if kind == "uitools.uibuttongroup" else kind
        args = [] if parent is None else ["'Parent'", parent]
        p = node.properties
        for key in PROPS[kind].split():
            if not hasattr(p, key):
                continue
            value = getattr(p, key)
            if key in ("TooltipString","FontName","FontSize") and not np.size(value):
                continue
            v = expression(value, key)
            if key == "ColumnEditable":
                v = f"logical({v})"
            args.extend((string(key), v))
        if parent is None:
            args.extend(("'Visible'", "'off'"))
        lines.append(f"{obj} = {typ}(" + ",".join(args) + ");")
        tag = getattr(p, "Tag", None)
        if isinstance(tag, str) and re.fullmatch(r"[A-Za-z]\w*", tag):
            lines.append(f"h.{tag} = {obj};")
        for key in p._fieldnames:
            if not key.endswith(("Callback", "Fcn")):
                continue
            v = getattr(p, key)
            if isinstance(v, str):
                if v in ("%default", "closereq", ""):
                    continue
                raise ValueError(f"{name}/{tag}: unsupported callback {v}")
            if not np.size(v):
                continue
            function = v.item().function_handle.function
            if "addToolbarExplorationButtons" in function:
                continue  # MATLAB creates axes exploration controls on demand.
            if any(owner == name and string(cb) in function for owner, cb in STALE):
                continue
            match = CALLBACK.search(function)
            if not match:
                raise ValueError(f"{name}/{tag}: unknown saved callback {function}")
            callback = match[2]
            if not re.search(r"(?m)^function\b[^\n]*?\b" + callback + r"\s*\(", source):
                raise ValueError(f"{name}: missing {callback}")
            call = f"acgui.event(@{name},{string(callback)}"
            if key == "CreateFcn":
                callbacks.append(f"init{{end+1}} = @(){call},{obj},[]);")
            else:
                key = {"SelectionChangeFcn": "SelectionChangedFcn", "ResizeFcn": "SizeChangedFcn"}.get(key, key)
                callbacks.append(f"set({obj},{string(key)},@(obj,evt){call},obj,evt));")
        for child in np.atleast_1d(node.children).flat:
            walk(child, obj)

    walk(root, None)
    if assets:
        asset_name = func + "_assets.mat"
        savemat(output / asset_name, assets, do_compression=True, oned_as="row")
        lines.insert(2, f"a = load(fullfile(fileparts(mfilename('fullpath')),'{asset_name}'));")
    lines.extend(callbacks)
    lines.append("end")
    (output / (func + ".m")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dict(counts)
