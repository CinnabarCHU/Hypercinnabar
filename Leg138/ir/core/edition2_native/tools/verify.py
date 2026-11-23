"""Verify per-line token completeness and reconstruct all 92 original byte streams."""
import csv,gzip,hashlib,json
from collections import Counter,defaultdict
from selection import HERE,PRIMARY,CORE,TARGET,readcsv
# These columns carry selectors and extra editorial or inherited context rather than new source lexemes.
NON_LITERAL=set('item_id site source_path source_line verification_flags raw_source_line reported_hole row_kind previous_body_line event_group_first_line event_display_joined context_line reported_core_prefix reflector_group_context reflector_group_source_line'.split())

def verify():
    directory=readcsv(HERE/'datasets.csv');coverage={r['item_id']:r for r in readcsv(HERE/'coverage.csv')}
    assert len(directory)==len(coverage)==92 and set(coverage)==set(TARGET)
    witness=defaultdict(bytearray);datalines={}
    with gzip.open(HERE/'source_lines.csv.gz','rt',encoding='utf8',newline='') as f:
        for r in csv.DictReader(f):
            k=(r['item_id'],int(r['source_line']));assert k not in datalines
            datalines[k]=r;witness[k[0]]+=r['raw_text'].encode('latin1')+{'CRLF':b'\r\n','LF':b'\n','CR':b'\r','none':b''}[r['line_ending']]
    checked=0;field_values=0
    for e in directory:
        id=e['source_items'];b=witness[id];meta=coverage[id];assert hashlib.sha256(b).hexdigest()==meta['source_sha256'];assert b==(PRIMARY/meta['source_path']).read_bytes()
        rows=readcsv(CORE/e['data_path']);assert int(e['row_count'])==len(rows)==int(meta['named_rows']);seen=set()
        for r in rows:
            n=int(r['source_line']);assert n not in seen;seen.add(n)
            s=datalines[id,n];assert s['role']=='data' and r['raw_source_line']==s['raw_text']
            literal=[v for k,v in r.items() if k not in NON_LITERAL and v]
            assert Counter(s['raw_text'].split())==Counter(' '.join(literal).split()),(id,n)
            checked+=1;field_values+=len(literal)
        expected={ln for (key,ln),v in datalines.items() if key==id and v['role']=='data'};assert seen==expected
    s=json.loads((HERE/'verification.json').read_text());assert checked==s['named_rows'];s.update({'source_byte_roundtrips_verified':len(witness),'source_lines_reassembled':len(datalines),'data_rows_verified_for_exact_literal_token_multisets':checked,'populated_literal_fields_including_unresolved_fragments':field_values});(HERE/'verification.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s))
if __name__=='__main__':verify()
