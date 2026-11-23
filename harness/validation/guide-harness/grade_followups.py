"""Export only public tool and numerical evidence. Omit hidden model messages, raw paths and logs."""
import json,hashlib,sys
from pathlib import Path
from zipfile import ZipFile

def grade(root):
    spec=json.loads((root/'followup.json').read_text());by_case={}
    for entry in spec['cases']:
        key=entry['id']; receipt=json.loads((root/key/'primary.json').read_text()); turn=receipt['turns'][0]
        result={'session_id':receipt.get('session_id'),'session_status':receipt['status'],'model':receipt['runtime']['model'],
                 'input_text':turn['user_prompt'],'attachment_sha256':receipt['attachment']['sha256'],'derived_from':entry['derived_from'],
                 'tool_calls':len(turn['tool_calls']),'scientific_calls':[c['name'] for c in turn['tool_calls'] if c['name'] in ('acycle_native','acycle_analyze') or c['name'] in ['acycle_menu_'+role for role in ('helper','analyzer','plotter','replay')]],'requests':[]}
        case=key.split('-')[0]
        for request in sorted((root/'menu-queue').glob('*.json')):
            e=json.loads(request.read_text())
            if e['case']!=case: continue
            rid=e['run_id']; row={'id':rid,'menu':e['menu'],'role':e['role'],'settings':e['settings'],'sources':e['sources']}
            z=request.with_suffix('.zip')
            if z.exists():
                with ZipFile(z) as f:
                    w=json.loads(f.read('worker.json'));res=json.loads(f.read('response.json'));row.update(workflow=w['workflow_run'],worker_commit=w['worker_sha'],matlab_status=res['status'],completion=res['completion'])
                    if 'error' in res:row['error']=res['error']
                    if res['status']=='ok':
                        summary=res['summary'];row['returned_fields']=summary.get('fields',[]); row['figures']=res.get('files',[])
                        row['return_shapes']={k:v['size'] for k,v in summary.get('preview',{}).items() if 'size' in v}
                    if e['role']=='helper' and res['status']=='ok':
                        branch=res['summary'].get('preview',{}).get('params',{}).get('preview',{})
                        row['prepared_data']={k:{a:v[a] for a in ('class','size') if a in v} for k,v in branch.items() if k in ('data','datax','datay')}
                        row['prepared_settings']={k:v.get('value') for k,v in branch.items() if k in ('operation','period','pkstrough','mother','dss','param','pad','data_standardize','method_sel','pt1','pt2')}
                    if res.get('journal'):
                        lines=[json.loads(l) for l in f.read(res['journal']).splitlines()];row['logged_status']=lines[-1].get('info',{}).get('status')
            result['requests'].append(row)
        outcome=turn.get('scientific_outcome',{})
        result['completed_run_ids']=[r['run_id'] for r in outcome.get('completed_runs',[])] if outcome else None
        result['returned_tool_errors_count']=sum(bool(k.get('message',{}).get('isError')) for k in turn.get('tool_results',[]))
        result['tool_budget_exceeded']=any('budget' in str(v).lower() or 'exceeded' in str(v).lower() for v in receipt.get('errors',[]))
        result['returned_final_text']=bool(turn.get('final_response'))
        helpers={r['id']:r for r in result['requests'] if r['role']=='helper' and r.get('completion')=='done'}
        def matches(h):
            data=h.get('prepared_data',{}).get('data',{});params=h.get('prepared_settings',{})
            if data.get('class')!='double' or not data.get('size') or data['size'][1]<2:return False
            if case=='etp':
                return data['size'][0]==2001 and all(params.get(k)==v for k,v in {'operation':'WaveletSpectrum_legacy','method_sel':3,'dss':.1,'mother':'MORLET','param':6,'pad':1,'pt2':700}.items())
            return data['size'][0]==534 and params.get('operation')=='BuildAgeModel_legacy' and params.get('period')==405 and params.get('pkstrough')==1
        eligible={i for i,h in helpers.items() if matches(h)}
        computed={r['id'] for r in result['requests'] if r['role']=='analyzer' and r.get('completion')=='done' and r['sources'].get('helper_journal',{}).get('run_id') in eligible}
        plotted=[r['id'] for r in result['requests'] if r['role']=='plotter' and r.get('completion')=='done' and r['sources'].get('analyzer_journal',{}).get('run_id') in computed and r.get('figures')]
        result['guide_wavelet_or_agebuild']={'matching_helper_runs':sorted(eligible),'matching_analyzer_runs':sorted(computed),'matching_plotter_runs':plotted}
        by_case[key]=result
    return by_case
if __name__=='__main__':Path(sys.argv[2]).write_text(json.dumps(grade(Path(sys.argv[1])),ensure_ascii=False,indent=2)+'\n')
