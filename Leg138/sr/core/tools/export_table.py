"""Write named columns for one published electronic dataset or an edited print table."""
from pathlib import Path
import argparse
import csv
import gzip
import json
import sys

CORE=Path(__file__).resolve().parents[1]
def available():
    for filename in ('datasets.csv','print_datasets.csv'):
        with (CORE/filename).open() as stream:
            yield from csv.DictReader(stream)

def export(key,output,site=None):
    datasets={entry['dataset_id']:entry for entry in available()}
    if key not in datasets:
        raise SystemExit(f'Unknown dataset {key}. Use --list to display the published identifiers.')
    entry=datasets[key]
    writer=csv.writer(output)
    if 'file' in entry:
        with (CORE/entry['file']).open() as inp:
            rows=csv.DictReader(inp)
            writer.writerow(rows.fieldnames)
            for row in rows:
                if site is None or str(site)==row.get('site',entry['site']):
                    writer.writerow(row.values())
        return
    fields=json.loads(entry['fields_json'])
    writer.writerow(['source_file','source_line_first','source_line_last','source_record','sites','status','editorial_note',*fields])
    with gzip.open(CORE/'records.jsonl.gz','rt') as file:
        for line in file:
            row=json.loads(line)
            if row['d']!=key or (site is not None and site not in row['s']):
                continue
            values=row['v']
            writer.writerow([entry['source'],row['lo'],row['hi'],row['n'],'|'.join(map(str,row['s'])),
                'field_mapped' if values is not None else 'unresolved',row.get('note',''),*(values or ['']*len(fields))])
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('dataset',nargs='?');ap.add_argument('--list',action='store_true');ap.add_argument('--site',type=int);ap.add_argument('-o','--output',type=Path)
    args=ap.parse_args()
    if args.list:
        for x in available():print(x['dataset_id'],x['records'],x.get('sites',x.get('site','')),sep='\t')
    elif not args.dataset:
        ap.error('Choose a dataset or use --list.')
    elif args.output:
        with args.output.open('w',newline='',encoding='utf-8') as output:export(args.dataset,output,args.site)
    else:
        export(args.dataset,sys.stdout,args.site)
