"""Compare two published distributions only when the complete sample key has a unique counterpart."""
from pathlib import Path
from collections import defaultdict,Counter
from decimal import Decimal,InvalidOperation
import csv,gzip,re,argparse
def samplekey_ir(r):
    label=r['sample_label'].strip()
    m=re.search(r'(\d+)([A-Z]+)-(\d+|CC)\s*[, ]+\s*(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)$', label)
    if not m or not r['reported_hole']:return None
    return (r['site'],r['reported_hole'][-1],str(int(m[1])),m[2],m[3],Decimal(m[4]),Decimal(m[5]))
def samplekey_disc(r):
    try:return (r['site'],r['hole'],str(int(r['core'])),r['core_type'],r['section'],Decimal(r['top_cm']),Decimal(r['bottom_cm']))
    except (ValueError,InvalidOperation):return None
def num(s):
    if not s:return None
    return Decimal(re.sub(r'^[ab]\s*','',s.strip()))
def main(root,out):
    ir=list(csv.DictReader((root/'ir/core/tables/carbons.csv').open()))
    disc=list(csv.DictReader(gzip.open(root/'disc/core/carbon.csv.gz','rt')))
    old=defaultdict(list);new=defaultdict(list)
    for r in ir:old[samplekey_ir(r)].append(r)
    for r in disc:new[samplekey_disc(r)].append(r)
    output=[]
    for r in ir:
        key=samplekey_ir(r); matches=new.get(key,[]) if key else []
        other=matches[0] if len(matches)==1 and len(old.get(key,[]))==1 else {}
        a,b=r['organic_c_pct'],other.get('organic_carbon_pct','')
        state='unmatched_or_nonunique' if not other else ('both_blank' if not (a or b) else 'same_numeric_value' if num(a)==num(b) else 'numeric_or_presence_difference')
        output.append(dict(site=r['site'],ir_hole=r['reported_hole'],ir_sample=r['sample_label'],ir_path=r['source_path'],ir_line=r['source_line'],ir_published_value=a,disc_path=other.get('source_path',''),disc_line=other.get('source_line',''),disc_published_value=b,comparison=state))
    with (out/'carbon_distribution_comparison.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=output[0]);w.writeheader();w.writerows(output)
    print(Counter(r['comparison'] for r in output))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('out',type=Path);a=p.parse_args();main(a.root,a.out)
