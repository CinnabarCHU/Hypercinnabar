"""Recompute a figure from the numerical inputs and open-source scientific code."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
REFS=json.loads((ROOT/'versions/acycle.json').read_text())
ALL=['F1','F2h','F2iso','F3','F4','F5','F6','F7','F8','S1','S2','S3','S4','S5','S6','S7']
ORBIT={'F1','F2h','F8','S6'}
COHERENCE={'F7','S7'}
CONFIG={
 'common':['F1','F2h','F7','F8','S6','S7'], 'common-negative':['F7','S7'],'common-bulk':['F8'],
 'april':['F2iso','F3','F4','F5','F6','S1','S2','S3','S4','S5'],
 'april-caption':['F5','S4'],'april-archiveband':['F2iso','F4','S3'],
 'v2701':['F3','S2'],'v27':['F3','S2'],'v270':['F3','S2'],'jan':['F3','S2'],
 'v28':['F2iso','F3','F4','F5','S2','S3','S4'],'v28-caption':['F5','S4'],
 'v302':['F2iso','F3','F4','F5','S2','S3','S4'],'v302-caption':['F5','S4'],
 'v303':['F2iso','F3','F4','F5','S2','S3','S4'],'v303-caption':['F5','S4'],
 'aug12':['F2iso','F3','F4','F5','S2','S3','S4'],'aug12-caption':['F5','S4'],'aug12-native':['F5','S4'],
 'current':['F2iso','F3','F4','F5','S2','S3','S4'],'current-caption':['F5','S4'],'current-native':['F5','S4']}
def checkout(ref,folder,subset):
    if not folder.exists():
        folder.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['git','clone','--filter=blob:none','--no-checkout','https://github.com/mingsongli/acycle.git',str(folder)],check=True)
        subprocess.run(['git','-C',str(folder),'sparse-checkout','set',subset],check=True)
        subprocess.run(['git','-C',str(folder),'checkout','--detach',ref],check=True)
    actual=subprocess.check_output(['git','-C',str(folder),'rev-parse','HEAD'],text=True).strip()
    if actual!=ref:raise ValueError(f'{folder} is at {actual}, expected {ref}')
    return folder

def ml(value):
    return "'"+str(value).replace("'","''")+"'"

def prepare_orbits(field_dir):
    field_dir.mkdir(parents=True,exist_ok=True)
    subprocess.run([sys.executable,str(ROOT/'python/orbits.py'),'--bundle',str(ROOT/'data/orbital_inputs.npz.xz'),'--output',str(field_dir/'orbits.mat')],check=True)

def render_calls(jobs,base):
    code=[]
    for profile,ids in jobs.items():
        for fig in ids:
            dest=base/profile/fig
            dest.mkdir(parents=True,exist_ok=True)
            code.append('render_figure('+','.join(map(ml,[fig,profile,ROOT,dest]))+');')
    return code

def run():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('figure',choices=ALL)
    p.add_argument('--version',choices=CONFIG)
    p.add_argument('--cached',action='store_true',help='Use the distributed, MATLAB-calculated numerical fields.')
    p.add_argument('--matlab',default='matlab')
    p.add_argument('--output',type=Path,help='Target directory for the FIG and SVG pair')
    a=p.parse_args();fid=a.figure
    profile=a.version or ('common' if fid in ORBIT|COHERENCE else 'april')
    if fid not in CONFIG[profile]:p.error(f'{fid} is unavailable for {profile}; see versions/figures.json')
    fields=ROOT/'fields'; base=profile.split('-')[0]
    out=(a.output or ROOT/'figures'/profile/fid).resolve();out.mkdir(parents=True,exist_ok=True)
    commands=["addpath("+ml(ROOT/'matlab')+");"]
    if fid in ORBIT:
        if not a.cached or not (fields/'orbits.mat').exists():prepare_orbits(fields)
    elif not a.cached:
        code_ref=REFS['april' if fid in COHERENCE else base]
        core=checkout(code_ref,ROOT/'.sources'/code_ref,'code')
        ref=checkout(REFS['current'],ROOT/'.sources'/'reference','data')
        if fid in COHERENCE:
            # Each pair gets a separate temporary directory for the original MC cache.
            import tempfile,os
            for k in range(1,6):
                with tempfile.TemporaryDirectory() as tmp:
                    expr=commands[0]+f'compute_wtc({k},{ml(core)},{ml(ref)},{ml(fields/"wtc")});'
                    env=dict(os.environ,TMPDIR=tmp,TEMP=tmp,TMP=tmp)
                    subprocess.run([a.matlab,'-batch',expr],check=True,env=env)
        else:
            commands.append('compute_fields('+','.join(map(ml,['v27' if base=='v2701' else base,core,ref,fields/base]))+');')
            if profile.endswith('archiveband'):commands.append('pda_alternate('+','.join(map(ml,[core,ref,ROOT]))+');')
    commands.append('render_figure('+','.join(map(ml,[fid,profile,ROOT,out]))+');')
    subprocess.run([a.matlab,'-batch',' '.join(commands)],check=True)
    from python.size_svg import set_paper_size
    set_paper_size(out/'plot.svg',fid)

if __name__=='__main__':run()
