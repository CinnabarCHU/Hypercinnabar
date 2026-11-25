"""Exercise the distributed user commands against the MATLAB-owned desktop."""
import json
from pathlib import Path
import subprocess
import sys
import time

root=Path(sys.argv[1]).resolve()
connection=root/'generated/connection.json'
until=time.monotonic()+240
while not connection.is_file() and time.monotonic()<until:
    time.sleep(.15)
result={'status':'failed'}
try:
    if not connection.is_file():
        raise TimeoutError('The packaged MATLAB launcher did not create a connection.')
    for action in ('config','check','filter','image','events'):
        subprocess.run([sys.executable,str(root/'local_test.py'),action],check=True,cwd=root,timeout=120)
    filtered=json.loads((root/'generated/local-filter.json').read_text())['receipts'][-1]['result']
    assert filtered['params']['flow']==.035 and filtered['params']['fhigh']==.055
    assert filtered['frequency_unit']=='cycles/m' and filtered['result_size']==[256,3]
    result={'status':'passed','tested_commands':['config','check','filter','image','events']}
finally:
    (root/'generated/local-tests-done.json').write_text(json.dumps(result)+'\n',encoding='utf-8')
