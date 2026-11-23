"""Run pinned original test suites alongside the portable cases."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT/"catalog/suites.json").read_text())


def checkout(name, folder):
    entry=REGISTRY[name]
    location=folder/(entry["repository"].split("/")[-1]+"-"+entry["commit"][:12])
    if not location.is_dir():
        folder.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=folder) as stage:
            repo=Path(stage)/"checkout"
            subprocess.run(["git","init","--quiet",repo],check=True)
            subprocess.run(["git","-C",repo,"remote","add","origin","https://github.com/"+entry["repository"]+".git"],check=True)
            subprocess.run(["git","-C",repo,"fetch","--quiet","--depth=1","origin",entry["commit"]],check=True)
            subprocess.run(["git","-C",repo,"checkout","--quiet","--detach","FETCH_HEAD"],check=True)
            repo.rename(location)
    actual=subprocess.check_output(["git","-C",location,"rev-parse","HEAD"],text=True).strip()
    if actual != entry["commit"]:
        raise ValueError(f"Checkout at {location} has unexpected revision {actual}")
    if entry.get("submodules"):
        subprocess.run(["git","-C",location,"submodule","update","--init","--recursive"],check=True)
    return location


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=["list","fetch","run"])
    parser.add_argument("suite",nargs="?",choices=sorted(REGISTRY))
    parser.add_argument("--vendor",type=Path,default=ROOT/".vendor")
    parser.add_argument("--output",type=Path,default=ROOT/".results"/"suites")
    parser.add_argument("--input-root",type=Path,help="Original publication validation input directory")
    parser.add_argument("--case",action="append",default=[],help="Original Harness case ID, repeatable")
    parser.add_argument("--figure",default="F3",help="CENOGRID manuscript figure")
    parser.add_argument("--cached",action="store_true",help="Use archived numerical fields for the CENOGRID figure")
    args=parser.parse_args()
    if args.action=="list":
        for key,s in REGISTRY.items():
            print(f"{key:23} {s['scope']}")
        return
    if args.suite is None:
        parser.error("choose a suite to fetch or run")
    key=args.suite
    repo=checkout(key,args.vendor.resolve())
    if args.action=="fetch":
        print(repo);return
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,CYCLO_SUITE_OUT=str(out))
    def run(cmd): subprocess.run(cmd,cwd=repo,env=env,check=True)
    if key=="guide-master":
        for script in [["migration/check.py","--figures"],["migration/master/compare.py"],
                       ["migration/menu/build.py"],["audit/tools/build_module_inventory.py"]]:
            run([sys.executable,*script])
        methods=REGISTRY[key]["matlab_tests"]
        run(["matlab","-batch","addpath('tests','audit/tests'); "+"; ".join(methods)])
    elif key in ("harness-cases","harness-parity"):
        acycle=checkout("upstream-bispectrum",args.vendor.resolve())
        env.update(ACYCLE_ROOT=str(acycle),ACYCLE_BACKEND="local",ACYCLE_VALIDATION_DIR=str(out))
        env["PYTHONPATH"]=os.pathsep.join([str(repo/"src"),env.get("PYTHONPATH","")])
        if key=="harness-parity":
            run(["matlab","-batch","addpath('matlab'); run_validation(getenv('ACYCLE_ROOT'),getenv('CYCLO_SUITE_OUT'))"])
        else:
            requested={c["id"] for c in json.loads((repo/"benchmarks/manifest.json").read_text())["cases"]}
            if set(args.case)-requested:parser.error("unknown Harness case")
            options=[x for case in args.case for x in ("--case",case)]
            run([sys.executable,"benchmarks/run.py","--workspace",out,*options])
    elif key=="upstream-bispectrum":
        run(["matlab","-batch","addpath('code/package/bispectral'); r=bispectralSelfTest(); assert(r.Passed)"])
    elif key in ("upstream-coco","upstream-bispectral-examples"):
        if not args.input_root or not args.input_root.is_dir():
            parser.error("supply the original records with --input-root (see docs/sources.md)")
        env["CYCLO_INPUT"]=str(args.input_root.resolve())
        call=("runCocoPublicationValidation(getenv('CYCLO_SUITE_OUT'),'InputRoot',getenv('CYCLO_INPUT')); "
              "validateCocoPublicationValidation(getenv('CYCLO_SUITE_OUT'))" if key=="upstream-coco" else
              "r=bispectralValidateExamples(getenv('CYCLO_SUITE_OUT'),'DataDirectory',getenv('CYCLO_INPUT')); assert(r.Passed)")
        run(["matlab","-batch","addpath(genpath('code')); "+call])
    elif key=="cenogrid-figures":
        run([sys.executable,"main.py",args.figure,"--version","manuscript","--output",out]+(["--cached"] if args.cached else []))
    else:
        parser.error("this group bundles independent workflows; run the pinned commands listed in docs/sources.md")


if __name__=="__main__":
    main()
