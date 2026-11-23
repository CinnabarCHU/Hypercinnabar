"""Build a request for the real packaged MATLAB dispatcher from a public test packet."""
import json, os, sys
from pathlib import Path
from guide_transport import FILES, verify, digest
def main():
    if 'DEEPSEEK_API_KEY' in os.environ: raise ValueError('Unexpected credential')
    repo=Path.cwd().resolve(); env=verify(json.loads(Path(sys.argv[1]).read_text())); out=Path(sys.argv[2]).resolve();out.mkdir(parents=True)
    src=repo/'upstream/acycle/data/Examples'/FILES[env['case']][0]
    if digest(src)!=env['input_sha256']: raise ValueError('Incorrect fixture')
    request={'input_path':str(src),'output_dir':str(out),'acycle_root':str(repo/'upstream/master'),'operation':env['operation'],'parameters':env['parameters']}
    (out.parent/'request.json').write_text(json.dumps(request))
    (out/'worker.json').write_text(json.dumps({'case':env['case'],'run_id':env['run_id'],'input_sha256':env['input_sha256'],'output_dir':str(out),'worker_sha':os.environ['GITHUB_SHA'],'workflow_run':os.environ['GITHUB_RUN_ID'],'provider_credential_received':False,'request':env},indent=2))
if __name__=='__main__': main()
