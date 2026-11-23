"""Verify the edition catalogue, references and representative scientific queries offline."""
import argparse
import csv
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path
from serve import endpoint

def verify(root):
    with sqlite3.connect(root/'Leg138.sqlite') as db:
        db.row_factory=sqlite3.Row
        value=lambda sql:db.execute(sql).fetchone()[0]
        assert value('PRAGMA integrity_check')=='ok'
        assert not list(db.execute('PRAGMA foreign_key_check'))
        counts={name:value('SELECT count(*) FROM '+name) for name in ('documents','pages','plate_pages','sites','plans','items','evidence','assets','datasets','dataset_items','native_ir','sr_rows')}
        for name,n in [('documents',76),('pages',1922),('plate_pages',620),('plans',12),('sites',11),('assets',5425),('native_ir',17835),('sr_rows',124288)]:assert counts[name]==n,(name,counts[name],n)
        for r in db.execute('select distinct local_path from datasets'):
            assert (root/r[0]).is_file(),r[0]
        assert value("SELECT count(*) FROM evidence e LEFT JOIN items i USING(item_id) WHERE e.item_id IS NOT NULL AND i.item_id IS NULL")==0
        assert value("SELECT count(*) FROM dataset_items m LEFT JOIN items i USING(item_id) WHERE i.item_id IS NULL")==0
        assert value("SELECT count(*) FROM documents d LEFT JOIN assets a ON a.local_path=d.local_source WHERE a.local_path IS NULL")==0
        assert value("SELECT count(*) FROM documents d WHERE d.pdf_pages!=(SELECT count(*) FROM pages p WHERE p.doc_id=d.doc_id)")==0
        assert value("SELECT count(*) FROM documents WHERE series='IR' AND chapter!='' AND doi=''")==0
        for d in db.execute("SELECT d.*,count(s.record_no) AS actual FROM datasets d LEFT JOIN sr_rows s USING(dataset_id) WHERE d.storage='sr_rows' GROUP BY d.dataset_id"):
            assert d['records']==d['actual'],d['dataset_id']
        get=lambda name,**q:endpoint(db,root,name,dict(limit='1000',**q))
        assert len(get('sites'))==11 and len(get('plans'))==12
        assert not get('sites',site='850')[0]['proposed_site']
        assert len(get('rows',dataset='IR.ORGANIC_C'))==666 and not get('rows',dataset='IR.ORGANIC_C',site='854')
        assert len(get('rows',dataset='IR.CARBON',site='854'))==63
        assert len(get('rows',dataset='SR.C39.TABLE2.CORRECTED',site='846'))==266
        assert len(get('rows',dataset='IR11.T11.pilot',site='846'))==62
        assert len(get('rows',dataset='IR.carbonate_repeat_runs'))==645
        replica=get('rows',dataset='IR.carbonate_repeat_samples',site='853')
        case=next(r for r in replica if r['source_row']=='22')
        assert (case['run_1_carbonate_pct'],case['run_2_carbonate_pct'],case['published_absolute_difference_pct'])==('87.90','87.07','0.17')
        assert len(get('rows',dataset='PLATES.OPTICAL'))==22
        assert len(get('rows',dataset='PR.RATE_INTERVAL'))==230
        assert get('search',q='organic carbon',site='846')
        assert get('search',q='ooze',site='845',series='PLATES')
        assert get('page',doc='IR.C17',page='1')
        assert get('items',series='IR',site='852',kind='table')
        assert get('sources',series='SR',site='846')
        assert len(get('rows',dataset='CD.GRAPE_SOURCE_ROWS',site='844'))==1000
        assert get('datasets',item='IR11.T11')
        copies=Counter(r['comparison'] for r in csv.DictReader((root/'data/carbon_distribution_comparison.csv').open()))
        assert copies['same_numeric_value']==664 and sum(copies.values())==2296
        collations=list(csv.DictReader((root/'data/pr_ir_field_comparison.csv').open()))
        assert len(collations)==252 and sum(r['status']=='same_numeric_value' for r in collations)==249
        raw=list(csv.DictReader((root/'disc/core/replay/splice_membership.csv').open()))
        assert sum(int(r['paired_mcd_density_equal']) for r in raw)==121065
        assert int(raw[0]['fin_selected_rows'])-int(raw[0]['released_mcd_rows'])==157
        digest=json.loads((root/'data/source_package_checks.json').read_text())
        assert sum(v['payload_entries'] for v in digest['archives'].values())==counts['assets']
        result=dict(counts=counts,checks='passed',carbon_witness_checks=dict(copies),hole_version_pairs=len(collations),mcd_rows_traceable_to_hole_fin=121065,source_payloads=counts['assets'])
        sums=root/'SHA256SUMS'
        if sums.exists():
            for ln in sums.read_text().splitlines():
                sha,rel=ln.split('  ',1);assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==sha,rel
        return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',nargs='?',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--write',type=Path)
    args=p.parse_args();result=verify(args.root);t=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.write:args.write.write_text(t)
    print(t)
