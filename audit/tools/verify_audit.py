#!/usr/bin/env python3
"""Verify the saved audit and optionally compare a fresh regeneration.

Run from any directory. This checks static evidence only; it never runs MATLAB.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


REPO = Path(__file__).resolve().parents[2]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def verify(reports, source, regenerated):
    errors = []
    validation = json.loads((reports / 'validation.json').read_text(encoding='utf-8'))
    manifest = json.loads((reports / 'manifest.json').read_text(encoding='utf-8'))
    summary = json.loads((reports / 'summary.json').read_text(encoding='utf-8'))
    expected = validation['report_sha256']
    for name, checksum in expected.items():
        path = reports / name
        if not path.is_file() or sha256(path) != checksum:
            errors.append(f'Saved report hash mismatch: {name}')
    for path, checksum in [
        (REPO / 'audit/tools/audit_acycle.py', validation['auditor_sha256']),
        (REPO / 'audit/decisions.json', validation['decisions_sha256']),
    ]:
        if sha256(path) != checksum:
            errors.append(f'Audit provenance hash mismatch: {path.name}')
    pin = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if pin != validation['upstream_commit'] or pin != summary['commit']:
        errors.append('Upstream commit differs from the reviewed pin')
    status = subprocess.check_output(
        ['git', '-C', str(source), 'status', '--porcelain', '--untracked-files=no'], text=True)
    if status.strip():
        errors.append('Upstream has modified tracked files')
    tracked = set(subprocess.check_output(
        ['git', '-C', str(source), 'ls-files', '-z'], text=True).rstrip('\0').split('\0'))
    paths = [row['path'] for row in manifest]
    if set(paths) != tracked or len(paths) != len(tracked):
        errors.append('Manifest must cover every tracked file exactly once')
    for row in manifest:
        path = source / row['path']
        if not path.is_file() or sha256(path) != row['sha256']:
            errors.append(f'Upstream file hash mismatch: {row["path"]}')
    symbols = read_csv(reports / 'symbols.csv')
    identifiers = {row['id'] for row in symbols}
    edges = read_csv(reports / 'edges.csv')
    if len(identifiers) != len(symbols):
        errors.append('Duplicate graph symbols')
    if any(row['source'] not in identifiers or row['target'] not in identifiers for row in edges):
        errors.append('Graph edge has an absent endpoint')
    if regenerated is not None:
        generated_names = {path.name for path in regenerated.iterdir() if path.is_file()}
        if generated_names != set(expected):
            errors.append('Regenerated report set differs from the saved 15-report baseline')
        for name in expected:
            path = regenerated / name
            if not path.is_file() or path.read_bytes() != (reports / name).read_bytes():
                errors.append(f'Regeneration differs: {name}')
    result = dict(
        passed=not errors, upstream_commit=pin, source_files_checked=len(manifest),
        report_hashes_checked=len(expected), graph_symbols_checked=len(symbols),
        graph_edges_checked=len(edges), regeneration_checked=regenerated is not None,
        errors=errors, scope='Static audit only; no MATLAB, GUI, MEX or scientific parity execution.',
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=REPO / 'upstream/acycle')
    parser.add_argument('--reports', type=Path, default=REPO / 'audit/reports')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--regenerate', action='store_true', help='Generate into a temporary directory and compare bytes')
    mode.add_argument('--regenerated', type=Path, help='Compare a completed regeneration from this directory')
    args = parser.parse_args()
    if args.regenerate:
        with tempfile.TemporaryDirectory(prefix='acycle-audit-') as directory:
            output = Path(directory)
            subprocess.run([
                sys.executable, str(REPO / 'audit/tools/audit_acycle.py'),
                '--source', str(args.source.resolve()), '--output', str(output),
                '--config', str(REPO / 'audit/decisions.json'),
            ], check=True, stdout=subprocess.DEVNULL)
            return verify(args.reports, args.source, output)
    return verify(args.reports, args.source, args.regenerated)


if __name__ == '__main__':
    raise SystemExit(main())
