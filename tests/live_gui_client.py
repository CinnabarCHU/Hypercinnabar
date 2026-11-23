"""Connect from outside a running MATLAB UI and verify it survives detach."""
import os
from pathlib import Path
import subprocess
import time

import matlab.engine

root = Path(os.environ["RUNNER_TEMP"])
for _ in range(1800):
    if (root / "gui-ready").is_file():
        break
    time.sleep(.1)
try:
    print("Named shared sessions", matlab.engine.find_matlab(), flush=True)
    eng = matlab.engine.connect_matlab("AcycleDesktopTest", background=True).result(timeout=35)
    print("Attached to MATLAB", flush=True)
    value = eng.feval("plus", 1.0, 2.0, background=True).result(timeout=35)
    assert value == 3
    eng.quit()
    print("Shared MATLAB Engine round trip passed", flush=True)
    runtime = root / "official-dsh"; src = root / "harness-src"
    subprocess.run(["node", str(src / "scripts/installed_plugin_smoke.mjs"), str(runtime),
                    str(root / "study"), str(runtime / "node_modules/dsh-acycle/index.mjs"),
                    "--gui-live"], check=True, timeout=320)
except BaseException:
    (root / "gui-done").write_text("failed")
    raise
(root / "gui-done").write_text("ok")
