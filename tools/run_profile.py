"""Exercise the public request/response route with one backend and save per-ID receipts."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def entries(name):
    return json.loads((ROOT/"catalog"/(name+".json")).read_text())

def run(args):
    cases,tasks=entries("cases"),entries("tasks")
    ops={"python":{"linear","integrate_rate","tune","constant_rate","periodogram","cip_accumulation",
                   "segmented_clock","rate_step_proxy","weak_band","hilbert_envelope","imbrie_continuous","imbrie_euler"},
         "r":{"linear","integrate_rate","tune","constant_rate","ar1","segmented_clock","hilbert_envelope","imbrie_euler"},
         "rpy2":{"linear","integrate_rate","tune","constant_rate","ar1"},
         "warp":{"integrate_rate","tune","constant_rate"},
         "matlab":{"linear","periodogram","swa","gaussian","segmented_clock","hilbert_envelope"}}
    ids=[name for name,case in cases.items() if case["operation"] in ops[args.backend]]
    if args.backend=="matlab":
        ids=[name for name in ids if not name.startswith("cenogrid-") or f"-{args.profile}-" in name]
    if args.backend=="python":
        ids += list(tasks)
    if args.backend=="r":
        ids.extend(["odp926b-timeopt","xiamaling-precession","walvis1262-precession"])
    if args.ids:
        if set(args.ids)-set(ids):
            raise SystemExit("Unsupported IDs for this profile: "+str(sorted(set(args.ids)-set(ids))))
        ids=args.ids
    args.output.mkdir(parents=True,exist_ok=True)
    if any(args.output.iterdir()):
        raise SystemExit("Use a new or empty result directory")
    checked=[]
    for name in ids:
        # Each independent candidate gets only the request folder. The scorer owns the reference.
        dest=args.output/name
        req,sub=dest/"request",dest/"submission"
        subprocess.run([sys.executable,ROOT/"bench.py","prepare",name,req],check=True)
        if args.backend=="matlab":
            if not args.acycle:
                raise SystemExit("--acycle must locate the selected Acycle checkout")
            env=dict(os.environ,CYCLO_REQUEST=str(req.resolve()),CYCLO_OUTPUT=str(sub.resolve()),
                     CYCLO_ACYCLE=str(args.acycle.resolve()),CYCLO_ADAPTER=str(ROOT/"adapters"))
            call="addpath(getenv('CYCLO_ADAPTER')); acycle_candidate(getenv('CYCLO_REQUEST'),getenv('CYCLO_OUTPUT'),getenv('CYCLO_ACYCLE'))"
            subprocess.run(["matlab","-batch",call],env=env,check=True)
        else:
            if args.backend in ("rpy2", "warp"):
                prefix=[sys.executable,ROOT/"adapters/astrochron_bridge.py",args.backend]
            elif args.backend=="r":
                prefix=["Rscript","--vanilla",ROOT/"adapters/astrochron.R"]
            else:
                prefix=[sys.executable,ROOT/"adapters/python_baseline.py"]
            subprocess.run([*prefix,req,sub],check=True)
        result=subprocess.run([sys.executable,ROOT/"bench.py","score",name,sub],text=True,capture_output=True)
        if result.returncode not in (0,1):
            raise RuntimeError(f"{name}: {result.stderr}")
        receipt=json.loads(result.stdout)
        (dest/"score.json").write_text(result.stdout)
        checked.append(receipt)
        print(f"{name}: {receipt['status']}", flush=True)
    (args.output/"summary.json").write_text(json.dumps(checked,indent=2,allow_nan=False)+"\n")
    # Geological disagreement is a result. Numerical regressions are build failures.
    return int(any(row["status"]=="mismatch" for row in checked))

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("backend",choices=["python","r","rpy2","warp","matlab"])
    parser.add_argument("output",type=Path)
    parser.add_argument("ids",nargs="*")
    parser.add_argument("--profile",choices=["v28","current"],default="current")
    parser.add_argument("--acycle",type=Path)
    sys.exit(run(parser.parse_args()))
