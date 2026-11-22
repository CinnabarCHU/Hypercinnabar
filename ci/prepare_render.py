"""Write one MATLAB job for a collection of figure/version combinations."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import CONFIG, ROOT, ml

GROUPS = {
    'common': ['common', 'common-negative', 'common-bulk', 'common-records'],
    'baseline': ['april', 'april-caption'],
    'frequency': ['april-archiveband'],
    'gaussian': ['april-demean'],
    'older': ['v27', 'v270', 'v2701', 'jan', 'v28', 'v28-caption'],
    'july': ['v302', 'v302-caption'],
    'august': ['v303', 'v303-caption'],
    'pretag': ['aug12', 'aug12-caption', 'aug12-native'],
    'current': ['current', 'current-caption', 'current-native'],
}

def prepare(group, output):
    calls = ["addpath(" + ml(ROOT / 'matlab') + ");"]
    for version in GROUPS[group]:
        for figure in CONFIG[version]:
            folder = output / version / figure
            folder.mkdir(parents=True, exist_ok=True)
            args = ','.join(map(ml, (figure, version, ROOT, folder)))
            calls.append(f"render_figure({args});")
    (ROOT / 'batch_render.m').write_text('\n'.join(calls) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('group', choices=GROUPS)
    parser.add_argument('--output', type=Path, default=ROOT / 'figures')
    args = parser.parse_args()
    prepare(args.group, args.output.resolve())
