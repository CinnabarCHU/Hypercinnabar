"""Prepare or score all current or v2.8 MATLAB requests in a single batch."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("action",choices=["prepare","score"])
parser.add_argument("profile",choices=["current","v28"])
parser.add_argument("folder",type=Path)
args=parser.parse_args()
cases=json.loads((root/"catalog/cases.json").read_text())
ids=[k for k,c in cases.items() if c["operation"] in {"linear","gaussian","swa","periodogram","segmented_clock","hilbert_envelope"} and
     (not k.startswith("cenogrid-") or f"-{args.profile}-" in k)]
scores=[]
for name in ids:
    sub=args.folder/name/("request" if args.action=="prepare" else "submission")
    cmd=[sys.executable,root/"bench.py",args.action,name,sub]
    if args.action=="prepare":
        subprocess.run(cmd,check=True)
    else:
        result=subprocess.run(cmd,capture_output=True,text=True)
        if result.returncode not in (0,1):
            raise RuntimeError(f"{name}: {result.stderr}")
        scores.append(json.loads(result.stdout))
        (sub.parent/"score.json").write_text(result.stdout)
if args.action=="prepare":
    (args.folder/"cases.json").write_text(json.dumps(ids))
else:
    (args.folder/"summary.json").write_text(json.dumps(scores,indent=2)+"\n")
    for s in scores:
        print(s["id"],s["status"])
    sys.exit(int(any(s["status"]!="match" for s in scores)))
