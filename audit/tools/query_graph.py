#!/usr/bin/env python3
"""Inspect reviewed file relationships without MATLAB. Paths are case sensitive."""
import argparse
import csv
from collections import defaultdict, deque
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('path', help='Upstream-relative MATLAB path')
parser.add_argument('--direction', choices=('callees','callers'), default='callees')
parser.add_argument('--transitive', action='store_true')
parser.add_argument('--reports', type=Path, default=Path('audit/reports'))
args=parser.parse_args()
inventory={r['path']:r for r in csv.DictReader((args.reports/'migration_inventory.csv').open())}
if args.path not in inventory:
    parser.error('Path is not present in the pinned inventory')
graph=defaultdict(set)
for row in csv.DictReader((args.reports/'file_edges.csv').open()):
    s,t=row['source'],row['target']
    if args.direction=='callers': s,t=t,s
    graph[s].add(t)
seen,queue={args.path},deque([(args.path,0)])
print('Static possible dependencies; dynamic dispatch and external callers remain unresolved.')
while queue:
    source,depth=queue.popleft()
    for target in sorted(graph[source]):
        if target in seen: continue
        seen.add(target)
        print(f'{depth+1}\t{source}\t{target}\t{inventory[target]["category"]}')
        if args.transitive: queue.append((target,depth+1))
