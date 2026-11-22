"""Measure the two exported MATLAB role trees. With --candidates print matching bodies as TSV."""

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median


MATLAB = Path(__file__).resolve().parents[2] / 'matlab'
ROLES = {'helper', 'analyzer', 'plotter'}
SECTION = re.compile(r'%% Copied from (\S+) (.+):L(\d+)-L(\d+)')
EXECUTE = re.compile(r'^function\b.*\bexecute\(')


def survey(namespace):
    lengths = {}
    bodies = {}
    packages = defaultdict(set)
    copied_lines = defaultdict(set)
    public_calls = set()
    call = re.compile(r'\b' + namespace + r'\.(\w+)\.(helper|analyzer|plotter)\s*\(')
    for file in sorted((MATLAB / ('+' + namespace)).glob('+*/*.m')):
        if file.stem not in ROLES:
            continue
        package, role = file.parent.name[1:], file.stem
        key = (package, role)
        packages[package].add(role)
        lines = file.read_text(encoding='utf-8').splitlines()
        lengths[key] = len(lines)
        first = next(i for i, line in enumerate(lines) if EXECUTE.match(line))
        bodies[key] = [line for line in lines[first:]
                       if not line.startswith('%% Copied from ') and line != '%% End copied source']
        for line in lines:
            marker = SECTION.fullmatch(line)
            if marker:
                repo_pin, source, lo, hi = marker.groups()
                for number in range(int(lo), int(hi) + 1):
                    copied_lines[repo_pin, source, number].add(key)
            if not line.lstrip().startswith('%'):
                public_calls.update((key, match.groups()) for match in call.finditer(line))
    stats = {
        'packages': len(packages),
        'roles': len(lengths),
        'roles per package': dict(sorted(Counter(map(len, packages.values())).items())),
        'analyzer only': sum(roles == {'analyzer'} for roles in packages.values()),
        'median file lines': median(lengths.values()),
        'files <= 30 lines': sum(n <= 30 for n in lengths.values()),
        'files > 100 lines': sum(n > 100 for n in lengths.values()),
        'source lines in two or more distinct role files': sum(len(users) >= 2 for users in copied_lines.values()),
        'distinct literal calls to public roles': len(public_calls),
    }
    return stats, bodies


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidates', action='store_true')
    options = parser.parse_args()
    guide_stats, guide = survey('acmethods')
    master_stats, master = survey('acmaster')
    common = sorted(guide.keys() & master.keys())
    matches = [key for key in common if guide[key] == master[key]]
    if options.candidates:
        print('package\trole')
        for package, role in matches:
            print(package, role, sep='\t')
    else:
        print('metric', 'GUIDE', '3.1.1', sep='\t')
        for metric in guide_stats:
            print(metric, guide_stats[metric], master_stats[metric], sep='\t')
        print(f'{len(common)} matching package/role names; {len(matches)} matching execute bodies.')
