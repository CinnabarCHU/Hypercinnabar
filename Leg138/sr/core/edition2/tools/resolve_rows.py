"""Keep source observations immutable and add an independently evidenced field-placement layer."""
import csv, gzip, json, re, hashlib
from pathlib import Path
from decimal import Decimal
E=Path(__file__).resolve().parents[1];C=E.parent
def table(name):
    with (C/name).open() as f:return list(csv.DictReader(f))
def witness(n):
    text=gzip.decompress((E/'witnesses'/f'PANGAEA.{n}.txt.gz').read_bytes()).decode()
    lines=text.splitlines();i=next(i for i,v in enumerate(lines) if v.strip()=='*/')+1
    heads=lines[i].split('\t')
    return [(k,dict(zip(heads,v.split('\t')))) for k,v in enumerate(lines[i+1:],i+2)]
def write_csv(name,rows):
    with (E/'data'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run():
    unresolved=table('unresolved_records.csv')
    ds={x['dataset_id']:x for x in table('datasets.csv')}
    ids={}
    with gzip.open(C/'records.jsonl.gz','rt') as f:
        for line in f:
            row=json.loads(line)
            if row['v'] is None:ids[(row['d'],row['lo'])]=row['n']
    check=[];results=[];links=[]
    moore=dict(zip(range(844,849),['808116','808118','808119','808121','808122']))
    paper={x['item_id']:x for x in table('items.csv')}
    names={132:'B Theocalyptra davisiana',139:'B Lamprocyrtis neoheteroporos',141:'T Phormostichoartus doliolum',145:'B Pterocanium prismatium',164:'B Diartus petterssoni'}
    for r in unresolved:
        key=r['dataset_id'];lo=int(r['first_line']);hi=int(r['last_line']);raw=r['original_text']
        fields=json.loads(ds[key]['fields_json']);proposal={};orphans=[];ambiguities=[];outside=[];status=''
        if key=='SR.C23.TABLE3':
            parts=raw.replace('\n','\t').split('\t');datum=parts[0]
            assert len(parts)==12
            vals=[v.strip() for v in parts[2:]]
            proposal['datum']=datum;orphans=[parts[1]];status='field_alignment_supported_leading_token_unassigned'
            for i,site in enumerate(moore):
                t,o=vals[i*2:i*2+2];proposal[f'site{site}_t_mcd']=t;proposal[f'site{site}_o_mcd']=o
                published_table=paper[f'SR.C11.TABLE{site-842}']
                obs=[(n,q) for n,q in witness(moore[site]) if q['Ageprof dat des']==names[lo]]
                wt=wo='';wline=''
                if obs:
                    wline,q=obs[0];wt=q['Depth comp top [mcd]'];wo=q['Depth comp bot [mcd]']
                    match='exact' if Decimal(t)==Decimal(wt) and Decimal(o)==Decimal(wo) else 'same_field_position_different_published_value'
                else:
                    assert t==o=='n.a'
                    match='no_matching_event_in_site_table'
                edition23=next(((n,q) for n,q in witness('806678') if q['Event']==f'138-{site}' and q['Ageprof dat des'].lower().startswith(datum[0]+' ') and q['Ageprof dat des'].lower().endswith(datum.split()[-1].lower())),None)
                rep_vals=(edition23[1]['Depth top [m]'],edition23[1]['Depth bot [m]']) if edition23 else ('','')
                check.append(dict(table=key,source_line=lo,source_event=datum,site=site,cd_t=t,cd_o=o,unassigned_leading_token=parts[1],ch11_witness=moore[site],witness_line=wline,witness_event=names[lo],witness_t=wt,witness_o=wo,comparison=match,ch11_source=published_table['source'],ch11_pdf_page=published_table['pdf_page'],ch23_repository_edition='806678',ch23_repository_line=edition23[0] if edition23 else '',ch23_repository_t=rep_vals[0],ch23_repository_o=rep_vals[1]))
            outside=['808116','808118','808119','808121','808122','806678']
            ambiguities=['Leading token has no reliable station or field identity. Preserve it verbatim. Sparse or differing values in the independent author study are not substituted into the CD values.']
        elif key=='SR.C35.APPENDIXB':
            x=raw.split()
            when,expected=(('847B','44.84') if lo==950 else ('850B','378.56'))
            matches=[(n,q) for n,q in witness('806757') if q['H']=='138-'+when and q['Depth sed [m]']==expected]
            assert len(matches)==1
            wline,q=matches[0]
            if lo==950:
                v=x[:7]+['']+x[7:9]+['']+x[9:]
                assert q['Terr [%]']==q['Acc rate terr [g/cm**2/ka]']==''
                assert [q['CaCO3 [%]'],q['bSiO2 [%]']]==['?78.01','?26.11']
                assert [q['Acc rate CaCO3 [g/cm**2/ka]'],q['Acc rate opal [g/cm**2/ka]']]==v[8:10]
                status='field_alignment_verified_two_empty_source_cells'
            else:
                v=x[:6]+[x[6]+x[7]]+x[8:]
                assert v[6]==q['bSiO2 [%]']=='18.86'
                assert abs(sum(Decimal(y) for y in v[5:8])-Decimal(100))<=Decimal('0.015')
                status='split_number_verified'
            assert len(v)==len(fields)
            proposal=dict(zip(fields,v));outside=['806757']
            links.append(dict(dataset_id=key,source_line=lo,witness='806757',witness_line=wline,comment='Same hole, composite depth and chronology; preserves printed suspect flags rather than translating their encoding.'))
        else:
            assert key=='SR.C15.TABLE9' and lo==873
            tok=raw.split()
            assert tok[0]=='677B-' and tok[4]=='5.4'
            proposal=dict(zip(['sample_label_as_printed','coarse_pct','depth_mbsf','depth_offset_m','depth_mcd','benthic_d18o','benthic_d13c','planktonic_d18o'],tok[1:]))
            ambiguities=['Hole label 677B- on the same line also introduces subsequent Hole B rows. At 81.60 mbsf the isotope pair resembles Hole A in the earlier study. No complete sample label or final planktonic d13C is legible on the CD line. Do not impute a measurement.']
            orphans=['677B-'];status='partial_fields_identifiable_hole_and_final_isotope_unresolved';outside=['701308','701312']
            for n in outside:
                for line,q in witness(n):
                    if q['Depth sed [m]']=='81.60':
                        links.append(dict(dataset_id=key,source_line=lo,witness=n,witness_line=line,comment=q['Event']+' at 81.60 mbsf; comparison only. Independent publication or adjusted values are not an exact duplicate record.'))
        results.append(dict(dataset_id=key,ordinal=ids[(key,lo)],source=r['source'],source_sha256=ds[key]['sha256'],source_first_line=lo,source_last_line=hi,original_text=raw,status=status,proposed_field_values=proposal,unassigned_tokens=orphans,notes=ambiguities,witness_dois=outside))
    with (E/'data/row_apparatus.jsonl').open('w') as f:
        for item in results:f.write(json.dumps(item,ensure_ascii=False)+'\n')
    write_csv('ch23_depth_crosschecks.csv',check);write_csv('row_witness_lines.csv',links)
    print(len(results),len(check),len(links))
if __name__=='__main__':run()
