"""Summarize downloaded guide artifacts without recomputing scientific results."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('results', type=Path)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
reports = []
for path in sorted(args.results.glob('*/report.json')):
    report = json.loads(path.read_text())
    reports.append({
        'case_id': report['case_id'],
        'execution_ok': report['execution_ok'],
        'criteria_ok': report['criteria_ok'],
        'steps': len(report['steps']),
        'checks': len(report['checks']),
        'passed_checks': sum(c['passed'] for c in report['checks']),
        'failed_steps': [s for s in report['steps'] if s['status'] != 'ok' or s['completion'] != 'done'],
        'failed_checks': [c for c in report['checks'] if not c['passed']],
        'fatal': report['fatal'],
        'peaks': report.get('peaks'),
        'coco': report.get('coco'),
        'ecoco': report.get('ecoco'),
        'age_model_edge': report.get('age_model_edge'),
    })
result = {'cases': reports}
text = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
if args.output:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)
else:
    print(text, end='')
