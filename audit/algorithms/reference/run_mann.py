"""Run the original numerical code with a declaration-syntax fix for gfortran."""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.request import urlopen

base = "https://www.meteo.psu.edu/holocene/public_html/Mann/tools/MTM-RED/"
sources = ["mtm.f", "spec.f", "findpeaks.f", "recon.f", "display.f", "miscsubs.f"]
tables = ["chisquare.dat", "ftest.dat"]
out = Path("reference-evidence")
out.mkdir(exist_ok=True)
with open("benchmarks/fixtures/records/lavernock.csv", newline="") as handle:
    data = sorted((float(row[0]), float(row[1])) for row in list(csv.reader(handle))[1:])
with tempfile.TemporaryDirectory() as tmp:
    work = Path(tmp)
    hashes = {}
    for name in sources+tables:
        with urlopen(base+name, timeout=20) as response:
            content = response.read()
        (work/name).write_bytes(content)
        hashes[name] = hashlib.sha256(content).hexdigest()
    (out/"mann-source-sha256.json").write_text(json.dumps(hashes, indent=2)+"\n")
    expected = json.loads(Path(__file__).with_name("mann-original-sha256.json").read_text())
    if hashes != expected:
        raise ValueError("Published source or reference tables differ from the pinned archive.")
    # One historical spelling puts the complex width after the function name.
    # Reorder only this declaration; fail if the archive ever changes.
    src = work/"miscsubs.f"
    old = b"COMPLEX FUNCTION ZDOTC*16("
    original = src.read_bytes()
    if original.count(old) != 1:
        raise ValueError("Unexpected original ZDOTC declaration.")
    src.write_bytes(original.replace(old,b"COMPLEX*16 FUNCTION ZDOTC("))
    # Fixed-form FORTRAN 77 relied on implicit static storage.
    subprocess.run(["gfortran", "-std=legacy", "-O0", "-fno-automatic",
                    *sources, "-o", "mtm"], cwd=work, check=True)
    with (work/"series.dat").open("w") as handle:
        handle.write(f"Lavernock magnetic susceptibility\n{len(data)} 0.03\n(F20.12)\n")
        for _, value in data:
            handle.write(f"{value:20.12f}\n")
    run = subprocess.run(["./mtm"], cwd=work, input="series.dat\n0\n7\n", text=True,
                         capture_output=True, timeout=90)
    (out/"mann-program.txt").write_text(run.stdout+run.stderr)
    run.check_returncode()
    for file in work.glob("*.out"):
        shutil.copyfile(file, out/("mann-"+file.name))
    info = work/"mtm-spec.inf"
    shutil.copyfile(info, out/"mann-noise.txt")
    if "robust determination:" not in info.read_text().lower():
        raise RuntimeError("The original program did not emit its robust fitted rho.")
