"""Call the actual packaged interpreters and Acycle tools against a live R2024a GUI."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root=Path(sys.argv[1]).resolve()
work=root/'Workspace'
resources=root/'Acycle Harness.app/Contents/Resources'
connection=work/'generated/connection.json'
until=time.monotonic()+300
while not connection.is_file() and time.monotonic()<until:
    time.sleep(.2)
result={'status':'failed'}
try:
    c=json.loads(connection.read_text())
    config={'id':'acycle-native','name':'dsh-acycle','config':{
        'python':str(resources/'python/bin/python3'), 'workspace':c['workspace'], 'guiSession':c['guiSession']}}
    config_file=work/'generated/harness-plugin.json'
    config_file.write_text(json.dumps(config)+'\n')
    env=dict(os.environ,ACYCLE_HARNESS_RUNTIME=str(resources/'runtime'),PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1')
    for action in ('check','filter','image','events'):
        subprocess.run([str(resources/'node/bin/node'),str(work/'check_harness.mjs'),str(config_file),action],
            check=True,cwd=work,env=env,timeout=120)
    result={'status':'passed','actions':['check','filter','image','events'],'packaged_interpreters':True}
finally:
    (work/'generated/local-tests-done.json').write_text(json.dumps(result)+'\n')
