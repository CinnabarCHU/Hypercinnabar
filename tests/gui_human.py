"""Ask the test host to exercise its native widget callbacks, outside the product protocol."""
import os
from pathlib import Path
import sys
import time

root = Path(os.environ["RUNNER_TEMP"])
request = root / "gui-human-request"
response = root / "gui-human-response"
tmp = request.with_suffix(".tmp")
tmp.write_text(sys.argv[1], encoding="utf-8")
tmp.replace(request)
until = time.monotonic() + 65
while not response.is_file() and time.monotonic() < until:
    time.sleep(.1)
if not response.is_file():
    raise TimeoutError("The MATLAB human-callback fixture did not finish.")
value = response.read_text(encoding="utf-8")
response.unlink()
if value != "ok":
    raise RuntimeError(value)
