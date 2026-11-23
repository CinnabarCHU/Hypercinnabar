"""Fixture-only relay for follow-up agent calls; no array/journal is committed.

Inputs beyond the public chapter fixtures must refer to exact members of fresh
science artifacts from this validation run. All MATLAB values remain unchanged.
"""
import hashlib, json, os, re, shutil, sys, time
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
from guide_transport import FILES, ID
MENUS={'menu_waveletGUI','menu_ecoco','menu_period','menu_agebuild','menu_age','menu_filter','menu_interp','menu_prewhiten','menu_sort','menu_power','menu_samplerate'}
R=re.compile(ID)
def digest(f): return hashlib.sha256(f.read_bytes()).hexdigest()
def plain(o):
    if isinstance(o,(float,int,bool)) or o is None:return
    if isinstance(o,list):
        if len(o)>160: raise ValueError('Use artifact references for long arrays')
        for x in o:plain(x)
    elif isinstance(o,dict):
        for k,v in o.items():
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,61}',k):raise ValueError('Bad field')
            plain(v)
    elif not isinstance(o,str) or len(o)>100 or not re.fullmatch(r'[\w ,()./+%−:-]*',o) or any(t in o for t in ('/','..',':','\\')):raise ValueError('Only bounded scientific settings may be relayed')
def validate(e):
    if e['case'] not in FILES or not R.fullmatch(e['run_id']) or e['menu'] not in MENUS or e['role'] not in ('helper','analyzer','plotter','replay'):raise ValueError('Not a Chapter 6 role')
    allowed={'input','override','params','plt','dat','res','target_kind'}
    if set(e['settings'])-allowed: raise ValueError('Unsupported fixture payload')
    plain(e['settings'])
    if set(e['sources'])-{'file_input','helper_journal','analyzer_journal','replay_journal'}:raise ValueError('Unknown role input')
def identify(archive,member,case):
    with ZipFile(archive) as z:
        meta=json.loads(z.read('worker.json')); assert meta['case']==case and member in z.namelist()
        return {'kind':'artifact','workflow':str(meta['workflow_run']),'sha':meta['worker_sha'],'run_id':meta['run_id'],'member':member,'digest':hashlib.sha256(z.read(member)).hexdigest()}
def client(args):
    if 'DEEPSEEK_API_KEY' in os.environ:raise RuntimeError('Unexpected provider credential')
    root=Path(os.environ['ACYCLE_GUIDE_VALIDATION'])
    session=os.environ['ACYCLE_GUIDE_CASE']; case={'etp-wavelet':'etp','wayao-next':'wayao'}[session]
    match=re.search(r"acycle_harness_menu\('([^']+)','([^']+)'\);$",args[2])
    if not match:raise ValueError('This follow-up validates the registered menu interface')
    req,res=map(Path,match.groups());out=res.parent.resolve(); rid=out.parent.name
    if req.parent.resolve()!=out or not out.is_relative_to(root/session/'workspace/.acycle/runs'):raise ValueError('Outside study')
    q=json.loads(req.read_text()); p=dict(q['payload']); sources={}; qdir=root/'menu-queue';qdir.mkdir(exist_ok=True)
    if 'file_input' in p:
        f=p.pop('file_input'); src=Path(f['path']).resolve()
        if not src.is_relative_to(out.parent):raise ValueError('Expected frozen helper input')
        h=digest(src)
        if h==FILES[case][1]: spec={'kind':'fixture','digest':h}
        else:
            spec=None
            for z in sorted((root/'queue').glob('*.zip')):
                with ZipFile(z) as ar:
                    if json.loads(ar.read('worker.json'))['case']!=case:continue
                    for member in ('processed.csv','filtered.csv','prepared.csv','cleaned.csv'):
                        if member in ar.namelist() and hashlib.sha256(ar.read(member)).hexdigest()==h:spec=identify(z,member,case); break
                if spec: break
            if spec is None:raise ValueError('Only this live study’s actual public output may be passed')
        sources['file_input']={'mode':f['kind'],'field':f['field'],'source':spec}
    for k in ('helper_journal','analyzer_journal','replay_journal'):
        if k not in p:continue
        jf=Path(p.pop(k)).resolve();parts=jf.relative_to(root/session/'workspace/.acycle/runs').parts
        if parts[1:3]!=('outputs','journals') or parts[-1]!='events.jsonl':raise ValueError('Expected journal of this conversation')
        spec=identify(qdir/(parts[0]+'.zip'),'/'.join(parts[2:]),case)
        if spec['digest']!=digest(jf):raise ValueError('Local journal changed')
        sources[k]=spec
    e=dict(case=case,run_id=rid,role=q['role'],menu=q['menu'],settings=p,sources=sources);validate(e)
    tmp=qdir/(rid+'.tmp'); tmp.write_text(json.dumps(e,indent=2)+'\n');tmp.rename(qdir/(rid+'.json'))
    (out/'matlab-started.json').write_text('{"transport":"public R2024b worker"}')
    z=qdir/(rid+'.zip');end=time.monotonic()+1650
    while not z.is_file():
        if time.monotonic()>end:raise TimeoutError('No fresh scientific response')
        time.sleep(1)
    with ZipFile(z) as ar:
        if sum(m.file_size for m in ar.infolist())>220_000_000:raise ValueError('Oversized archive')
        for m in ar.infolist():
            n=PurePosixPath(m.filename)
            if n.is_absolute() or '..' in n.parts or ((m.external_attr>>16)&0o170000)==0o120000:raise ValueError('Invalid member')
        md=json.loads(ar.read('worker.json'));assert md['run_id']==rid
        ar.extractall(out)
if __name__=='__main__':client(sys.argv)
