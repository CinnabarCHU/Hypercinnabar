"""Check public tool calls, their returned IDs and native Acycle journals in the CI ZIPs."""
import argparse,hashlib,json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

def grade(zpath, baseline):
    with ZipFile(zpath) as z:
        r=json.loads(z.read('graded/report.json'));case=r['case_id'];expected=json.loads((baseline/case/'report.json').read_text())
        seen=set();trace=[]
        for s in r['steps']:
            ordinal=PurePosixPath(s['folder']).name; prefix='graded/'+ordinal+'/'; rid=s['harness_run_id']
            call=json.loads(z.read(prefix+'public-call.json')); record=json.loads(z.read(prefix+'public-result.json'))
            assert call['name']=='acycle_menu_'+s['role'] and record['run_id']==rid and rid not in seen
            assert record['menu']==s['menu'] and record['status']=='completed' and record['completion']==s['completion']=='done'
            assert all(parent in seen for parent in record.get('source_runs',[]))
            home='ws/.acycle/runs/'+rid+'/'; jf=home+record['journal']; journal=z.read(jf); log=[json.loads(l) for l in journal.splitlines()]
            assert log[0]['attr']=='init' and log[-1]['attr']=='fin' and log[-1]['info']['status']=='done'
            for val in (log[0]['info']['params'],log[-1]['info']['retval']):
                if val:
                    assert z.getinfo(str(PurePosixPath(jf).parent/val)).file_size>0
            figures=[n for n in record.get('artifacts',{}) if n.startswith('figure_')]
            for f in figures: assert z.read(prefix+f+'.png').startswith(b'\x89PNG\r\n\x1a\n')
            trace.append({'step':s['label'],'tool':call['name'],'selector':record['selector'],'run_id':rid,'source_runs':record.get('source_runs',[]),'figures':len(figures),'journal_sha256':hashlib.sha256(journal).hexdigest()})
            seen.add(rid)
        def checks(report):return [(v['name'],bool(v['passed'])) for v in report['checks']]
        def logical(report):
            table={}
            for name,ok in checks(report):
                if name in table and table[name]!=ok: raise ValueError('Conflicting duplicate check: '+name)
                table[name]=ok
            return table
        assert [s['label'] for s in r['steps']]==[s['label'] for s in expected['steps']]
        return {'case':case,'calls':len(trace),'execution_ok':r['execution_ok'],'checks_passed':sum(x[1] for x in checks(r)),'checks_total':len(r['checks']),
                'check_outcomes_match_bridge':logical(r)==logical(expected),'bridge_raw_check_rows':len(checks(expected)),'science':{k:r[k] for k in ('sampling','coco','evolution','wavelet','age_model_edge') if k in r},'failed_checks':[n for n,ok in checks(r) if not ok],'trace':trace}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('artifact_dir',type=Path);p.add_argument('reference',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    out=[grade(a.artifact_dir/(c+'.zip'),a.reference) for c in ('insolation','etp','wayao')]
    a.output.write_text(json.dumps(out,indent=2)+'\n')
