"""Run the published program unmodified, using its interactive defaults."""
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
