"""Rebuild the Site 846 report catalogue from the files in this folder, offline."""

import argparse
import csv
import gzip
import hashlib
import os
import re
import sqlite3
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
METADATA = (
    "section", "item", "source", "item_source", "section_source", "location",
    "dataset", "item_dataset", "editorial_note", "report_page",
)


def quote_name(name):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValueError(f"Unexpected SQL identifier: {name!r}")
    return '"' + name + '"'


def insert_csv(db, name, path, *, data=False):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8-sig", newline="") as stream:
        rows = csv.reader(stream)
        columns = next(rows)
        query_name = quote_name(name)
        names = ", ".join(quote_name(c) for c in columns)
        if data:
            definitions = ", ".join(quote_name(c) + " TEXT NOT NULL" for c in columns)
            db.execute(f"CREATE TABLE {query_name} (edition_row INTEGER PRIMARY KEY, {definitions})")
        values = ", ".join("?" for _ in columns)
        # Source data retain literal blanks; empty optional catalogue fields are SQL NULL.
        records = rows if data else ([v if v else None for v in row] for row in rows)
        db.executemany(f"INSERT INTO {query_name} ({names}) VALUES ({values})", records)


def verify(db):
    if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise ValueError("SQLite integrity check failed")
    if db.execute("PRAGMA foreign_key_check").fetchone():
        raise ValueError("A catalogue link has no target")
    for name, count in db.execute("SELECT sql_name, row_count FROM dataset"):
        if db.execute("SELECT count(*) FROM " + quote_name(name)).fetchone()[0] != count:
            raise ValueError(f"Wrong row count: {name}")
    for file_path, expected, size, contents in db.execute(
        "SELECT path, sha256, bytes, contents FROM original_table_text JOIN source USING(path)"
    ):
        if len(contents) != size or hashlib.sha256(contents).hexdigest() != expected:
            raise ValueError(f"Original bytes differ: {file_path}")
        name = "t" + file_path.rsplit(".", 1)[1].zfill(2)
        source_lines = contents.decode("latin1").splitlines()
        cursor = db.execute("SELECT * FROM " + quote_name(name) + " ORDER BY edition_row")
        columns = [c[0] for c in cursor.description]
        auxiliary = {"edition_row", "source_line", "row_kind", "hole_context", "editorial_hole_assignment"}
        for record in cursor:
            line_number = int(record[columns.index("source_line")])
            if not 1 <= line_number <= len(source_lines):
                raise ValueError(f"Missing original line: {name}, {line_number}")
            original = "".join(source_lines[line_number-1].split())
            cells = "".join(str(v) for k, v in zip(columns, record) if k not in auxiliary)
            if original != "".join(cells.split()):
                raise ValueError(f"Text differs from source: {name}, line {line_number}")
    for kind, expected in (("table", 21), ("figure", 52)):
        numbers = {row[0] for row in db.execute("SELECT number FROM item WHERE kind=?", (kind,))}
        if numbers != set(range(1, expected + 1)):
            raise ValueError(f"Missing original {kind} number")
    if db.execute("SELECT count(*) FROM original_table_text").fetchone()[0] != 17:
        raise ValueError("Expected 17 distributed chapter tables")
    for name, row, field, expected in csv.reader(
        (ROOT / "metadata" / "print-checks.csv").read_text(encoding="utf-8").splitlines()[1:]
    ):
        value = db.execute(
            f"SELECT {quote_name(field)} FROM {quote_name(name)} WHERE edition_row=?", (row,)
        ).fetchone()
        if value != (expected,):
            raise ValueError(f"Print check failed: {name}, row {row}, {field}")


def build(destination):
    # Replace only on success. An interrupted build leaves the previous catalogue intact.
    directory = destination.parent
    with tempfile.NamedTemporaryFile(dir=directory, delete=False) as staging:
        temporary = Path(staging.name)
    db = sqlite3.connect(temporary)
    try:
        db.executescript((ROOT / "schema.sql").read_text(encoding="utf-8"))
        for name in METADATA:
            insert_csv(db, name, ROOT / "metadata" / (name + ".csv"))
        for name, filename in db.execute("SELECT sql_name, csv_path FROM dataset").fetchall():
            insert_csv(db, name, ROOT / filename, data=True)
        for path, member in db.execute(
            "SELECT path, member FROM source WHERE kind='chapter_table' ORDER BY path"
        ).fetchall():
            db.execute("INSERT INTO original_table_text VALUES (?, ?)", (path, (ROOT / member).read_bytes()))
        db.commit()
        verify(db)
        db.close()
        os.replace(temporary, destination)
    finally:
        db.close()
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "Site846.sqlite")
    parser.add_argument("--verify", action="store_true", help="Verify an existing database")
    args = parser.parse_args()
    if args.verify:
        import contextlib
        with contextlib.closing(sqlite3.connect(args.output.resolve().as_uri() + "?mode=ro", uri=True)) as conn:
            verify(conn)
        print("Verified", args.output)
    else:
        build(args.output)
        print("Built", args.output)
