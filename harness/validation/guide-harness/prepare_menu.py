"""Retrieve only checksummed outputs of public fixture workers, with read-only Actions access."""
import hashlib,json,os,re,sys,urllib.request
from pathlib import Path,PurePosixPath
from zipfile import ZipFile
from guide_transport import FILES, ID
from menu_transport import validate
repo=Path.cwd();root=Path(sys.argv[2]).resolve();root.mkdir(parents=True);out=root/'outputs';out.mkdir()
e=json.loads(Path(sys.argv[1]).read_text());validate(e);case=e['case'];p=e['settings'];assert 'DEEPSEEK_API_KEY' not in os.environ
api='https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY']+'/actions/'
class ScopedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,h,url):
        n=super().redirect_request(req,fp,code,msg,h,url)
        if n and n.host!=req.host:n.remove_header('Authorization')
        return n
def get(url):
    assert url.startswith(api)
    req=urllib.request.Request(url,headers={'Authorization':'Bearer '+os.environ['GH_READ_ACTIONS'],'User-Agent':'acycle-guide-validation'})
    return urllib.request.build_opener(ScopedRedirect()).open(req,timeout=80)
def materialize(s,is_journal):
    if s['kind']=='fixture':
        f=repo/'upstream/acycle/data/Examples'/FILES[case][0];assert hashlib.sha256(f.read_bytes()).hexdigest()==s['digest']==FILES[case][1];return str(f)
    assert re.fullmatch(r'\d+',s['workflow']) and re.fullmatch(r'[a-f0-9]{40}',s['sha']) and re.fullmatch(ID,s['run_id'])
    with get(api+'runs/'+s['workflow']) as r:run=json.load(r)
    assert run['head_sha']==s['sha'] and run['head_branch']=='acycle-guide-harness-jobs'
    assert run['path'] in ('.github/workflows/acycle-guide-harness-worker.yml','.github/workflows/acycle-guide-menu-worker.yml')
    with get(api+'runs/'+s['workflow']+'/artifacts') as r:a=json.load(r)['artifacts']
    item=next(t for t in a if t['name']=='scientific-result'); dest=root/s['run_id'];dest.mkdir(exist_ok=True);z=dest/'artifact.zip'
    if not z.exists():
        with get(api+'artifacts/'+str(item['id'])+'/zip') as f:
            b=f.read(200_000_001);assert len(b)<=200_000_000;z.write_bytes(b)
    n=PurePosixPath(s['member']);assert not n.is_absolute() and '..' not in n.parts
    if is_journal:assert n.parts[0]=='journals' and n.name=='events.jsonl'
    else:assert str(n) in ('processed.csv','prepared.csv','filtered.csv','cleaned.csv')
    with ZipFile(z) as a:
        m=json.loads(a.read('worker.json'));assert m['case']==case and m['run_id']==s['run_id'] and m['worker_sha']==s['sha']
        assert hashlib.sha256(a.read(str(n))).hexdigest()==s['digest']
        for info in a.infolist():
            path=PurePosixPath(info.filename)
            if path!=n and not (is_journal and path.parent==n.parent and path.name.startswith('events.jsonl.') and path.suffix=='.mat'):continue
            assert not path.is_absolute() and '..' not in path.parts and info.file_size<120_000_000
            f=dest/path; f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(a.read(info))
    return str(dest/n)
for k,s in e['sources'].items():
    if k=='file_input':
        assert s['mode']=='matrix' and re.fullmatch(r'[A-Za-z]\w{0,62}',s['field'])
        p[k]={'kind':'matrix','field':s['field'],'path':materialize(s['source'],False)}
    else:p[k]=materialize(s,True)
q=dict(operation='menu',acycle_root=str(repo),output_dir=str(out),menu=e['menu'],role=e['role'],payload=p)
(root/'request.json').write_text(json.dumps(q))
(out/'worker.json').write_text(json.dumps({'case':case,'run_id':e['run_id'],'worker_sha':os.environ['GITHUB_SHA'],'workflow_run':os.environ['GITHUB_RUN_ID'],'menu':e['menu'],'role':e['role'],'provider_credential_received':False},indent=2))
