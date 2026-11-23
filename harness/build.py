"""Assemble the installable Acycle Harness source from the fixed public upstream and this overlay."""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "harness"
HARNESS = "eefe06cf83dea1799e91fe5475e6b774d2e3f077"
MASTER = "dcba4279168745b563e0535b954297023dd62fc7"


def build(output):
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"Choose a new output directory: {output}")
    source = ROOT / "upstream/harness"
    for folder, pin in ((source, HARNESS), (ROOT / "upstream/master", MASTER)):
        if (
            not folder.is_dir()
            or subprocess.check_output(
                ["git", "-C", str(folder), "rev-parse", "HEAD"], text=True
            ).strip()
            != pin
        ):
            raise ValueError(
                f"Initialize the pinned submodule {folder} with git submodule update --init --recursive"
            )
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        stage = Path(temporary) / "project"
        shutil.copytree(
            source, stage, ignore=shutil.ignore_patterns(".git", "__pycache__", "node_modules")
        )
        shutil.copytree(
            HERE / "overlay", stage, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__")
        )
        shutil.copyfile(ROOT / "code/interface/catalogue.json", stage / "matlab/menu_catalog.json")
        subprocess.run(
            [
                sys.executable,
                str(stage / "scripts/build_native_catalog.py"),
                str(ROOT / "upstream/master"),
                "--output",
                str(stage / "matlab/native_catalog.json"),
            ],
            check=True,
        )
        stage.rename(output)
    return output


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("output", type=Path)
    print(build(p.parse_args().output))
