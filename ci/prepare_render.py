import argparse,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import ROOT,CONFIG,ORBIT,REFS,prepare_orbits,ml

def prepare(group):
    calls=["addpath("+ml(ROOT/'matlab')+");"]
    groups={
        'common':['common','common-negative','common-bulk','common-records'],
        'baseline':['april','april-caption'], 'frequency':['april-archiveband'],
        'older':['v27','v270','v2701','jan','v28','v28-caption'],
        'july':['v302','v302-caption'],
        'august':['v303','v303-caption'],
        'pretag':['aug12','aug12-caption','aug12-native'],
        'current':['current','current-caption','current-native']}
    if group=='common':prepare_orbits(ROOT/'fields')
    if group=='frequency':calls.append('pda_alternate('+','.join(map(ml,[ROOT/'upstream',ROOT/'reference',ROOT]))+');')
    if group=='older':calls.append('compute_fields('+','.join(map(ml,['v27',ROOT/'oldcore',ROOT/'reference',ROOT/'fields/v2701']))+');')
    wrap="""from pathlib import Path
import subprocess
import sys
folder=Path(__file__).resolve().parent
root=folder.parents[2]
subprocess.run([sys.executable,str(root/'main.py'),folder.name,'--version',folder.parent.name,*sys.argv[1:]],check=True)
"""
    for version in groups[group]:
        for fig in CONFIG[version]:
            out=ROOT/'figures'/version/fig;out.mkdir(parents=True,exist_ok=True)
            (out/'main.py').write_text(wrap)
            calls.append('render_figure('+','.join(map(ml,[fig,version,ROOT,out]))+');')
    (ROOT/'group_profiles.txt').write_text('\n'.join(groups[group])+'\n')
    (ROOT/'batch_render.m').write_text('\n'.join(calls)+'\n')
if __name__=='__main__':prepare(sys.argv[1])
