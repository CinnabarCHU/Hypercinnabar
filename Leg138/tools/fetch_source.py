"""Fetch one exact source path using the public Leg 138 source registry."""
import argparse
from pathlib import Path

if __package__:
    from .fetch_sources import INVENTORY, ROOT, process, read_manifest
else:
    from fetch_sources import INVENTORY, ROOT, process, read_manifest


def fetch(root, key):
    row = next((item for item in read_manifest(INVENTORY) if item['local_path'] == key), None)
    if row is None:
        raise ValueError('No source registered with that exact path')
    root = Path(root).resolve()
    result = process(row, root, offline=False, attempts=3, timeout=60)
    if result['status'] not in {'verified', 'fetched'}:
        raise ValueError(f"{result['status']}: {result['detail']}")
    return root / key


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('local_path')
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    print(fetch(args.root, args.local_path))
