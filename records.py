"""Resolve the exact numeric series used by the benchmark."""
from __future__ import annotations

import bz2
import csv
import hashlib
import io
import json
import os
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np

ROOT = Path(__file__).resolve().parent


def catalog(name):
    return json.loads((ROOT / "catalog" / (name + ".json")).read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def source_bytes(asset):
    sha = asset["sha256"]
    cache = Path(os.environ.get("CYCLOBENCH_CACHE", Path.home() / ".cache" / "cyclobench"))
    target = cache / sha
    if target.exists():
        data = target.read_bytes()
        if digest(data) != sha:
            raise ValueError(f"Corrupt cached source {target}. Remove this file to download it again.")
        return data
    request = Request(asset["url"], headers={"User-Agent": "Cyclostratigraphy-Benchmark/0.1"})
    with urlopen(request, timeout=60) as response:
        data = response.read()
    if digest(data) != sha:
        raise ValueError(f"Source SHA-256 mismatch for {asset['url']}")
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=cache, delete=False) as temp:
        temp.write(data)
    Path(temp.name).replace(target)
    return data


def numeric_csv(columns, rows):
    stream = io.StringIO()
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([format(float(value), ".12g") for value in row])
    return stream.getvalue().encode()


def decode_source(data, record):
    reader = record["reader"]
    if reader == "xlsx":
        from openpyxl import load_workbook
        book = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        try:
            rows = list(book.worksheets[record["sheet"]].values)
        finally:
            book.close()
    elif reader in ("bz2-whitespace", "bz2-indexed"):
        rows = (line.split() for line in bz2.decompress(data).decode().splitlines()[1:])
        if reader == "bz2-indexed":
            rows = ((i, *values) for i, values in enumerate(rows))
    elif reader == "pangaea":
        body = data.decode().split("*/", 1)[1].strip().splitlines()
        rows = csv.reader(body[1:], delimiter="\t")
    else:
        rows = csv.reader(data.decode("utf-8-sig", errors="replace").splitlines()[1:],
                          delimiter=record.get("delimiter", ","))
    selected = []
    bounds = record.get("selection")
    for row in rows:
        match = record.get("row_equals")
        if match and row[match["index"]] != match["value"]:
            continue
        suffix = record.get("exclude_suffix")
        if suffix and row[suffix["index"]].endswith(suffix["value"]):
            continue
        try:
            values = [float(row[i]) for i in record["indices"]]
        except (IndexError, ValueError, TypeError):
            continue
        if np.isfinite(values).all() and (bounds is None or bounds[0] <= values[0] <= bounds[1]):
            selected.append(values)
    if record.get("sort_first"):
        selected.sort(key=lambda values: values[0], reverse=record["sort_first"] == "descending")
    return numeric_csv(record["columns"], selected)


def record_bytes(name, rebuild=False):
    item = catalog("records")[name]
    if "file" in item and not (rebuild and "asset" in item):
        data = (ROOT / item["file"]).read_bytes()
    else:
        asset = catalog("assets")[item["asset"]]
        data = decode_source(source_bytes(asset), item)
    if digest(data) != item["sha256"]:
        raise ValueError(f"Prepared table checksum mismatch for {name}")
    return data


def record_array(name):
    return np.loadtxt(io.BytesIO(record_bytes(name)), delimiter=",", skiprows=1, ndmin=2)
