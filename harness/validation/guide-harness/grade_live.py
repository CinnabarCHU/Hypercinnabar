"""Read the SDK receipts and *fresh* worker artifacts after the run. Never grade prose as science."""
import argparse, hashlib, json
from pathlib import Path
from zipfile import ZipFile
import numpy as np

TARGETS={'insolation':[23.7,22.4,19.0],'etp':[405,125,95,41,23.7,22.4,19.0],'wayao':[33.9,10,7,2.6,1.8]}
def sha(data): return hashlib.sha256(data).hexdigest()
def matched_peaks(power,periods):
    f,y=power[:,0],power[:,1]; ix=np.where((y[1:-1]>y[:-2]) & (y[1:-1]>=y[2:]))[0]+1
    return [float(1/f[ix[np.argmin(abs(f[ix]-1/period))]]) for period in periods]
def grade(root,repo):
    output={}
    for case,targets in TARGETS.items():
        receipt=json.loads((root/case/'primary.json').read_text()); t=receipt['turns'][0]
        evidence={'model':receipt['runtime']['model'],'official_sdk':receipt['runtime']['sdk_client'],
                  'session':receipt.get('session_id'),'attachment_sha256':receipt['attachment']['sha256'],
                  'shell_tools_disabled':receipt['runtime']['shell_tools_disabled'],'sdk_status':receipt['status'],
                  'input_text':t['user_prompt'],'tools':[],'runs':[]}
        for call in t['tool_calls']:
            rid=call['callId']; m=next((x['message'] for x in t.get('tool_results',[]) if x.get('message',{}).get('toolCallId',x['message'].get('callId',x['message'].get('source',{}).get('callId')))==rid),None)
            step={'tool':call['name'],'outcome':('unreturned' if m is None else 'error' if m.get('isError') else 'ok')}
            if m and m.get('isError'):
                txt=' '.join(x.get('text','') for x in m.get('content',[]) if x.get('type')=='text')
                # Never publish transcript/private model reasoning, attachment paths or raw exception contexts.
                if 'Unknown MATLAB parameters' in txt:step['reason']='Unknown MATLAB parameter: method'
                elif 'Use a public exact catalog entrypoint' in txt:step['reason']='Native request did not specify a registered public entrypoint'
                else:step['reason']='Tool returned an error; raw output omitted'
            evidence['tools'].append(step)
        baseline=repo/'harness/validation/user-guide'/case
        ref=np.loadtxt(baseline/('mtm.csv' if case=='wayao' else 'mtm-5x-diagnostic.csv'),delimiter=',')
        prepared=np.loadtxt(baseline/'prepared-series.csv',delimiter=',')
        for z in sorted((root/'queue').glob('*.zip')):
            with ZipFile(z) as archive:
                w=json.loads(archive.read('worker.json'))
                if w['case']!=case:continue
                assert w['input_sha256']==evidence['attachment_sha256']
                local=root/case/'workspace/.acycle/runs'/w['run_id']/'result.json'
                saved=json.loads(local.read_text())
                if saved['status']!='completed': raise ValueError('Uncompleted local run: '+w['run_id'])
                v=json.loads(archive.read('response.json'))
                def csv(n): return np.loadtxt(archive.open(n),delimiter=',')
                p=csv('spectrum_robust.csv'); d=csv('processed.csv')
                assert p.shape[0]==len(ref) and d.shape[0]==len(prepared)
                guide_peaks=matched_peaks(ref,targets); actual=matched_peaks(p,targets)
                top=[e['period'] for e in v['summary']['peaks']]
                num={'rows':len(d),'processed_max_absolute_difference':float(np.max(abs(d[:,:2]-prepared))),
                     'nfft':v['parameters']['nfft'],'spectrum_bins':len(p),
                     'frequency_max_absolute_difference':float(np.max(abs(p[:,0]-ref[:,0]))),
                     'power_max_absolute_difference_over_reference_max':float(np.max(abs(p[:,1]-ref[:,1]))/np.max(ref[:,1])),
                     'check_periods':targets,'closest_local_peak_live':actual,'closest_local_peak_reference':guide_peaks,
                     'model_visible_top10_periods':top,'effective_smooth_fraction':v['parameters']['smooth_fraction'],
                     'evolution_step_actual':v['parameters'].get('evolution_step') if v['parameters'].get('evolution') else None}
                if case=='wayao' and 'filtered.csv' in archive.namelist():
                    ff=csv('filtered.csv'); original=np.loadtxt(baseline/'filtered.csv',delimiter=',')
                    num['gaussian_filter']={'curve_correlation':float(np.corrcoef(ff[:,1],original[:,1])[0,1]),
                           'max_absolute_difference':float(np.max(abs(ff[:,1]-original[:,1]))),'points':len(ff)}
                    ar=np.loadtxt(baseline/'robust-ar1.csv',delimiter=',')
                    common=p[(p[:,0]>=ar[0,0]-1e-12) & (p[:,0]<=ar[-1,0]+1e-12)]
                    if len(common)!=len(ar) or not np.allclose(common[:,0],ar[:,0],rtol=1e-10,atol=1e-12): raise ValueError('AR1 frequency grids differ')
                    num['robust95_shared_bins']=len(ar)
                    num['robust95_max_abs_diff_over_reference_max']=float(np.max(abs(common[:,4]-ar[:,4]))/np.max(ar[:,4]))
                artifacts={k:sha(archive.read(Path(path).name)) for k,path in v['artifacts'].items()}
                assert all(saved['artifact_sha256'][k]==h for k,h in artifacts.items())
                evidence['runs'].append({'id':w['run_id'],'parent':saved.get('parent_run_id'),'operation':w['request']['operation'],
                    'worker_sha':w['worker_sha'],'workflow_run':w['workflow_run'],'matlab':v['provenance']['matlab_release'],
                    'requested_parameters':w['request']['parameters'],'comparison':num,'artifact_sha256':artifacts})
        evidence['tool_calls']=len(evidence['tools'])
        evidence['returned_text']=bool(t.get('final_response')); evidence['final_response_sha256']=sha(t['final_response'].encode()) if t.get('final_response') else None
        output[case]=evidence
    return output
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('study',type=Path);p.add_argument('repo',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
    args.output.write_text(json.dumps(grade(args.study,args.repo),ensure_ascii=False,indent=2,allow_nan=False)+'\n')
