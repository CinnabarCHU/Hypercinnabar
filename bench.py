#!/usr/bin/env python3
"""Prepare an implementation-independent request or score an external result."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy.io import loadmat

from fixtures import case_tables, detection_panel, lr04_data, rate_section
from records import ROOT, catalog, digest, record_bytes
from scoring import read_json, score_case, score_task


def dump(directory, name, value):
    (directory / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def csv_table(directory, name, columns, data):
    np.savetxt(directory / (name + ".csv"), data, delimiter=",", header=",".join(columns),
               comments="", fmt="%.17g")


def prepare_case(case, target):
    raw, _ = case_tables(case)
    if raw.size:
        csv_table(target, "data", case["input_columns"], raw)
    if "controls" in case["fixture"]:
        csv_table(target, "controls", ["depth_m", "age_ka"], case["fixture"]["controls"])
    return {key: case[key] for key in ("operation", "description", "params", "input_columns", "output_columns")}


def prepare_task(name, task, target):
    for source in task.get("packet_files", []):
        shutil.copyfile(ROOT / source, target / Path(source).name)
    if name == "lr04-gaps":
        visible, hidden, block = lr04_data()
        csv_table(target, "data", ["age_ka", "benthic_d18O_permil"], visible)
        csv_table(target, "queries", ["age_ka", "block_gap"], np.column_stack((hidden[:, 0], block)))
    elif name == "synthetic-rate-step":
        csv_table(target, "data", ["depth_m", "proxy"], rate_section())
        csv_table(target, "windows", ["start_m", "end_m"], [[3,37],[45,94]])
    elif name == "synthetic-detection":
        series, _ = detection_panel()
        csv_table(target, "data", ["record_id","sample","proxy"], series)
    elif name == "cenogrid-modulation":
        for isotope in ("carbon", "oxygen"):
            dat = loadmat(ROOT / f"fixtures/cenogrid/v28-{isotope}.mat", variable_names=["t","y"])
            csv_table(target, isotope, ["age_ka","isotope"], np.column_stack((dat["t"],dat["y"])))
    else:
        for role, source in task["inputs"].items():
            (target / (role + ".csv")).write_bytes(record_bytes(source))
    return {key: task[key] for key in ("title", "params", "output_fields")}


def metadata(submission):
    meta = read_json(submission / "method.json")
    for field in ("method", "version"):
        if not isinstance(meta.get(field), str) or not meta[field].strip():
            raise ValueError(f"method.json requires a nonempty {field}")
    return meta


def execute(args):
    cases, tasks = catalog("cases"), catalog("tasks")
    if args.command == "list":
        for track, entries in [("case", cases), ("task", tasks)]:
            for name, entry in entries.items():
                print(f"{track:5}  {name:36} {entry.get('title', entry.get('description'))}")
        return 0
    if args.command == "verify":
        for path, sha in catalog("checksums").items():
            if digest((ROOT / path).read_bytes()) != sha:
                raise ValueError(f"SHA-256 mismatch for {path}")
        for name, rec in catalog("records").items():
            if args.sources or "file" in rec:
                record_bytes(name, rebuild=args.sources)
        print("Verified frozen files" + (" and reconstructed upstream inputs." if args.sources else "."))
        return 0
    if args.command == "dataset":
        args.output.write_bytes(record_bytes(args.id))
        return 0
    if args.id not in cases and args.id not in tasks:
        raise ValueError(f"Unknown ID {args.id}")
    is_case = args.id in cases
    if args.command == "prepare":
        target = args.directory
        if target.exists() and any(target.iterdir()):
            raise ValueError(f"Request directory {target} must be new or empty")
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=target.parent) as stage:
            packet_dir = Path(stage) / "request"
            packet_dir.mkdir()
            packet = prepare_case(cases[args.id], packet_dir) if is_case else prepare_task(args.id, tasks[args.id], packet_dir)
            dump(packet_dir, "request.json", {"schema_version":1, "id":args.id, "track":"case" if is_case else "task", **packet})
            if target.exists():
                target.rmdir()
            packet_dir.rename(target)
        return 0
    candidate = metadata(args.directory)
    result = score_case(cases[args.id], args.directory) if is_case else score_task(tasks[args.id], args.directory)
    print(json.dumps(dict(id=args.id, candidate=candidate, **result), indent=2, allow_nan=False))
    return int(result["status"] in ("mismatch", "criterion_unmet"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    sub.add_parser("verify").add_argument("--sources", action="store_true", help="also reconstruct remote inputs")
    data = sub.add_parser("dataset")
    data.add_argument("id", choices=sorted(catalog("records")))
    data.add_argument("output", type=Path)
    for cmd in ("prepare", "score"):
        p = sub.add_parser(cmd)
        p.add_argument("id")
        p.add_argument("directory", type=Path)
    try:
        return execute(parser.parse_args())
    except (ValueError, KeyError, OSError, OverflowError) as exc:
        print(json.dumps({"status":"invalid","reason":str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
