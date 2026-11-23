"""Connect from outside a running MATLAB UI and verify it survives detach."""
import os
from pathlib import Path
import subprocess
import time

root = Path(os.environ["RUNNER_TEMP"])
for _ in range(1800):
    if (root / "gui-ready").is_file():
        break
    time.sleep(.1)
try:
    session = (root / "gui-ready").read_text(encoding="utf-8")
    assert (Path(session) / "session.json").is_file()
    os.environ["ACYCLE_GUI_SESSION"] = session
    runtime = root / "official-dsh"; src = root / "harness-src"
    subprocess.run(["node", str(src / "scripts/installed_plugin_smoke.mjs"), str(runtime),
                    str(root / "study"), str(runtime / "node_modules/dsh-acycle/index.mjs"),
                    "--gui-live"], check=True, timeout=800 if os.environ.get("ACYCLE_PROVIDER_FIXTURE") else 320)
except BaseException:
    (root / "gui-done").write_text("failed")
    raise
(root / "gui-done").write_text("ok")
