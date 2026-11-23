"""Write two small astrochron call records. Run: python record.py NEW_DIRECTORY"""
import json
import sys
from pathlib import Path

import hdf5storage
import numpy as np
import pandas as pd
from rpy2 import robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr


def plain_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def event(folder, attr, **info):
    with (folder / "events.jsonl").open("a", encoding="utf-8") as stream:
        print(json.dumps({"attr": attr, "info": info}, ensure_ascii=False), file=stream)


def snapshot(folder, role, value):
    name = f"events.jsonl.{role}.mat"
    hdf5storage.savemat(folder / name, {"value": value}, fmt="7.3",
                       store_python_metadata=False, truncate_existing=False)
    return name


def table_info(r_table):
    return {"kind": "data.frame", "columns": list(ro.r["colnames"](r_table)),
            "row_names": list(ro.r["rownames"](r_table))}


def record(folder, symbol, arguments, with_rng=False, with_figure=False):
    folder.mkdir()
    astro = importr("astrochron")
    gr = importr("grDevices")
    graphics = importr("graphics")
    converter = ro.default_converter + pandas2ri.converter
    actual, schema, payload = {}, {}, {}
    for name, val in arguments.items():
        if isinstance(val, pd.DataFrame):
            with converter.context() as c:
                actual[name] = c.py2rpy(val)
            schema[name] = table_info(actual[name])
            payload[name] = np.array(ro.r["as.matrix"](actual[name]))
        else:
            actual[name] = val
            kind = {int: "integer", float: "double", bool: "logical"}[type(val)]
            schema[name] = {"kind": kind}
            payload[name] = np.int32(val) if kind == "integer" else val
    meta = {"backend": "R", "package": "astrochron", "function": symbol,
            "r_version": str(ro.r('as.character(getRversion())')[0]),
            "package_version": str(ro.r('as.character(packageVersion("astrochron"))')[0]),
            "arguments": schema}
    if with_rng:
        state = np.array(ro.globalenv[".Random.seed"], dtype=np.int32).reshape(-1, 1)
        meta["rng"] = {"kind": list(ro.r["RNGkind"]()), "file": snapshot(folder, "rng", state)}
    if with_figure:
        meta["graphics"] = {"file": "tune.png", "width": 800, "height": 600, "res": 120,
                            "bg": "white"}
    plain_json(folder / "manifest.json", meta)
    event(folder, "init", op=f"astrochron::{symbol}", params=snapshot(folder, "params", payload))
    opened = None
    try:
        if with_figure:
            opts = meta["graphics"].copy()
            name = opts.pop("file")
            gr.png(str(folder / name), **opts)
            opened = int(gr.dev_cur()[0])
        try:
            value = getattr(astro, symbol)(**actual)
            if with_figure:
                marker = {"v": 85, "col": "#B55023", "lty": 2}
                pane = [int(x) for x in graphics.par("mfg")]
                graphics.abline(**marker)
                event(folder, "event", logging="Reference age",
                      details={"op": "graphics::abline", "panel": pane, "args": marker})
        finally:
            if opened is not None:
                gr.dev_off(which=opened)
        meta["return"] = table_info(value)
        plain_json(folder / "manifest.json", meta)
        ref = snapshot(folder, "retval", np.array(ro.r["as.matrix"](value)))
    except Exception as exc:
        event(folder, "error", logging=str(exc), details={})
        event(folder, "fin", status="cancelled", retval=None)
        raise
    event(folder, "fin", status="done", retval=ref)


if __name__ == "__main__":
    root = Path(sys.argv[1])
    root.mkdir()
    depth = np.linspace(0, 12, 81)
    datum = pd.DataFrame({"depth_m": depth, "proxy": np.sin(2 * np.pi * depth / 3.2)})
    anchors = pd.DataFrame({"depth_m": [0., 4., 8., 12.], "age_ka": [0., 45., 85., 140.]})
    record(root / "tune", "tune", {"dat": datum, "controlPts": anchors,
           "genplot": True, "verbose": False}, with_figure=True)
    ro.r("set.seed(263); invisible(runif(9))")
    record(root / "ar1", "ar1", {"npts": 32, "rho": 0.72, "genplot": False,
           "verbose": False}, with_rng=True)
