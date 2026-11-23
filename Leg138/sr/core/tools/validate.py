"""Verify source fingerprints, catalogue identities, complete source-line accounting and extraction shapes."""
from collections import Counter, defaultdict
from pathlib import Path
import csv, gzip, hashlib, json

CORE=Path(__file__).resolve().parents[1]
ORIGINAL=CORE.parent/'primary'
def table(name):
    with (CORE/name).open() as file:return list(csv.DictReader(file))
def validate():
    sources=table('source_manifest.csv');by_src={r['source']:r for r in sources}
    for r in sources:
        source=ORIGINAL/r['source']
        assert source.stat().st_size==int(r['bytes']),r
        assert hashlib.sha256(source.read_bytes()).hexdigest()==r['sha256'],r
    tree=table('distribution_tree.csv')
    assert all(r['manifest_source'] in by_src for r in tree if r['entry_type']=='file')
    tables=table('datasets.csv');ds={r['dataset_id']:r for r in tables}
    ids={x['item_id'] for x in table('items.csv')};assert all(x['item_id'] in ids for x in tables)
    rows=Counter();unresolved=Counter();sites=Counter();physical=defaultdict(set)
    extra=defaultdict(set)
    for x in table('nonrecord_lines.csv'):
        extra[x['dataset_id']].add(int(x['source_line']))
    with gzip.open(CORE/'records.jsonl.gz','rt') as file:
        for line in file:
            record=json.loads(line);key=record['d'];rows[key]+=1
            assert record['n']==rows[key]
            assert record['lo']<=record['hi']
            for i in range(record['lo'],record['hi']+1):
                assert i not in physical[key]
                physical[key].add(i)
            if record['v'] is None:unresolved[key]+=1
            else:assert len(record['v'])==len(json.loads(ds[key]['fields_json']))
            for s in record['s']:sites[(key,int(s))]+=1
    for key,row in ds.items():
        assert rows[key]==int(row['records'])
        assert unresolved[key]==int(row['unresolved_records'])
        assert rows[key]-unresolved[key]==int(row['field_mapped_records'])
        readable=(ORIGINAL/row['source']).read_bytes().decode('latin-1').splitlines()
        nonempty={i for i,line in enumerate(readable,1) if line.strip()}
        assert not physical[key]&extra[key]
        assert not nonempty-(physical[key]|extra[key]),key
    for x in table('dataset_site_evidence.csv'):
        assert sites[(x['dataset_id'],int(x['site']))]==int(x['records_including_site'])
    edited=table('print_datasets.csv')
    for e in edited:
        assert e['item_id'] in ids
        assert e['source'] in by_src
        assert len(table(e['file']))==int(e['records'])
    pages=Counter()
    with gzip.open(CORE/'pages.jsonl.gz','rt') as f:
        for line in f:
            p=json.loads(line);pages[p['source']]+=1
            assert pages[p['source']]==p['pdf_page']
    items=table('items.csv');chapters=table('chapters.csv')
    result=dict(source_files=len(sources),official_files=sum(r['channel']=='ODP' for r in sources),
        directories=sum(r['entry_type']=='directory' for r in tree),directory_files=sum(r['entry_type']=='file' for r in tree),
        volume_chapters=len(chapters),chapter_leaves=sum(int(r['pdf_pages']) for r in chapters),all_indexed_leaves=sum(pages.values()),
        located_items=len(items),item_kinds=dict(Counter(i['kind'] for i in items)),anchors=len(table('caption_anchors.csv')),
        text_site_evidence=len(table('site_evidence.csv')),table_site_evidence=len(table('dataset_site_evidence.csv')),
        electronic_editions=len(tables),electronic_records=sum(rows.values()),field_mapped=sum(rows.values())-sum(unresolved.values()),
        unresolved=sum(unresolved.values()),accounted_nonrecord_nonempty_source_lines=sum(len(s) for s in extra.values()),
        transcribed_print_datasets=len(edited),transcribed_print_records=sum(int(r['records']) for r in edited),
        revised_ch39_table2={'cd_rows':rows['SR.C39.TABLE2.CD'],'replacement_rows':rows['SR.C39.TABLE2.CORRECTED']},
        sr6_fig11={'published_panels':list(range(844,854)),'additional_distributed_site':854},
        unresolved_by_table={k:v for k,v in unresolved.items() if v})
    (CORE/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':validate()
