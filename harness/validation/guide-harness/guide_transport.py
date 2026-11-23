#!/usr/bin/env python3
"""Test transport for the three PUBLIC User Guide fixtures. No numerical fallback.

The only input published for high-level runs is a fixture digest and validated
parameters. A result must be a fresh artifact from the job for this request.
"""
import hashlib, json, os, re, sys, time
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

FILES = {
    'insolation': ('Example-Insol-t-0-2000ka-day-80-lat-65-meandaily-La04.txt','6397fd514c2efba370c59a28cb10224b96d3e498469aa0e80bb0eb3d1bc6933c'),
    'etp': ('Example-La2004-1E.5T-1P-0-2000.txt','9653ac0d10ea7e4bad40afd4b553bacc3901b9c38e88b3da598e12f23565354f'),
    'wayao': ('Example-WayaoCarnianGR0.txt','f39dcc29be09cd5a07ef1dcdd20c6fa30499213c204ce4897ac02d9f6f086c21')}
OPS={'analyze','coco','ecoco','tune','interpolate_pro','swa'}
ID=r'[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}'
def verify(e):
    if set(e)!={'case','run_id','operation','input_sha256','parameters'} or e['case'] not in FILES or e['operation'] not in OPS or not re.fullmatch(ID,e['run_id']): raise ValueError('Unexpected public fixture request')
    if e['input_sha256']!=FILES[e['case']][1]: raise ValueError('Input must be the unmodified public Chapter 6 fixture')
    from acycle_deepseek.tools import _validate_parameters
    _validate_parameters(e['operation'],e['parameters'])
    for v in e['parameters'].values():
        if isinstance(v,str) and not re.fullmatch(r'[\w./ −-]{1,48}',v): raise ValueError('Non-fixture parameter string')
    return e
def digest(f): return hashlib.sha256(f.read_bytes()).hexdigest()
def encode(case,output,request):
    r=json.loads(request.read_text()); src=Path(r['input_path']).resolve()
    if not src.is_relative_to(output.parent) or src.parent!=output.parent or Path(r['output_dir']).resolve()!=output: raise ValueError('Expected frozen run input')
    return verify({'case':case,'run_id':output.parent.name,'operation':r['operation'],'input_sha256':digest(src),'parameters':r['parameters']})
def receive(z,out,rid):
    with ZipFile(z) as archive:
        if sum(f.file_size for f in archive.infolist())>350_000_000: raise ValueError('Oversize artifact')
        for m in archive.infolist():
            name=PurePosixPath(m.filename)
            if name.is_absolute() or '..' in name.parts or (m.external_attr>>16)&0o170000==0o120000: raise ValueError('Unsafe archive member')
        meta=json.loads(archive.read('worker.json'))
        if meta['run_id']!=rid: raise ValueError('Wrong MATLAB result')
        archive.extractall(out)
    p=out/'response.json'; v=json.loads(p.read_text())
    if 'artifacts' in v:
        for k,path in v['artifacts'].items():
            relative=Path(path).relative_to(meta['output_dir']); local=out/relative
            if not local.resolve().is_relative_to(out) or not local.is_file(): raise ValueError('Missing artifact: '+k)
            v['artifacts'][k]=str(local)
        p.write_text(json.dumps(v,ensure_ascii=False))
def main():
    if 'DEEPSEEK_API_KEY' in os.environ: raise ValueError('Model credential in scientific process')
    if len(sys.argv)!=3 or sys.argv[1]!='-batch': raise ValueError('Expected MATLAB -batch')
    match=re.search(r"acycle_batch\('([^']+)','([^']+)'\);$",sys.argv[2])
    if not match: raise ValueError('This transport handles registered high-level tools; menu validation uses the installed-tools runner')
    r=Path(os.environ['ACYCLE_GUIDE_VALIDATION']); case=os.environ['ACYCLE_GUIDE_CASE']
    req,res=map(Path,match.groups()); out=res.parent.resolve(); rid=out.parent.name
    if req.parent.resolve()!=out or not out.is_relative_to(r/case/'workspace/.acycle/runs'):raise ValueError('Outside live study')
    spec=encode(case,out,req)
    queue=r/'queue'; temp=queue/(rid+'.tmp'); temp.write_text(json.dumps(spec,indent=2)+'\n'); temp.rename(queue/(rid+'.json'))
    (out/'matlab-started.json').write_text('{"transport":"public MATLAB worker; awaiting result"}')
    end=time.monotonic()+1750; z=queue/(rid+'.zip'); fail=queue/(rid+'.failed')
    while not z.is_file():
        if fail.is_file(): raise RuntimeError(fail.read_text()[:200])
        if time.monotonic()>end:raise TimeoutError('No fresh MATLAB artifact')
        time.sleep(1)
    receive(z,out,rid)
if __name__=='__main__': main()
