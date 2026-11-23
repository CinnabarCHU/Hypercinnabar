#!/usr/bin/env python3
"""Test-only transport for a real MATLAB worker; never supplies numerical results.

The operator publishes queue requests on the validation branch, then returns the
GitHub artifact as queue/<run_id>.zip. No model credential is sent to that worker.
"""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import time
from zipfile import ZipFile


def main():
    if "DEEPSEEK_API_KEY" in os.environ:
        raise RuntimeError("Provider credential incorrectly inherited by numerical worker")
    if len(sys.argv) != 3 or sys.argv[1] != "-batch":
        raise ValueError("Expected a MATLAB batch invocation")
    match = re.search(r"acycle_harness_menu\('([^']+)','([^']+)'\);$", sys.argv[2])
    if not match:
        raise ValueError("Validation transport accepts only the fixed menu dispatcher")
    root = Path(os.environ["ACYCLE_VALIDATION_ROOT"]).resolve()
    workspace = root / "workspace"
    request_path, response_path = map(Path, match.groups())
    output = response_path.parent.resolve()
    if request_path.resolve().parent != output or not output.is_relative_to(workspace / ".acycle/runs"):
        raise ValueError("Request must belong to this validation workspace")
    request = json.loads(request_path.read_text())
    if request["operation"] != "menu" or request["menu"] not in {"menu_rgb2gray", "menu_interp"}:
        raise ValueError("Menu is outside the fixed validation scope")
    if request["role"] not in {"helper", "analyzer", "plotter", "replay"}:
        raise ValueError("Unknown menu role")
    run_id = output.parent.name
    if not re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{12}", run_id):
        raise ValueError("Invalid run id")
    files = {}

    def add(path):
        path = Path(path)
        resolved = path.resolve()
        if path.is_symlink() or not resolved.is_relative_to(workspace / ".acycle"):
            raise ValueError("Input lies outside the analysis workspace")
        data = path.read_bytes()
        if len(data) > 10_000_000:
            raise ValueError("Validation input too large")
        files[resolved.relative_to(workspace).as_posix()] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "base64": base64.b64encode(data).decode("ascii"),
        }

    payload = request["payload"]
    if "file_input" in payload:
        add(payload["file_input"]["path"])
    for key in ("helper_journal", "analyzer_journal", "replay_journal"):
        if key in payload:
            journal = Path(payload[key])
            add(journal)
            for sidecar in journal.parent.glob(journal.name + ".*.mat"):
                add(sidecar)
    envelope = {"schema": 1, "run_id": run_id, "workspace": str(workspace),
                "request": request, "files": files, "provider_credential_absent": True}
    queue = root / "queue"
    queue.mkdir(exist_ok=True)
    temporary = queue / (run_id + ".tmp")
    temporary.write_text(json.dumps(envelope, indent=2) + "\n")
    temporary.rename(queue / (run_id + ".json"))
    print(json.dumps({"validation_request": run_id, "role": request["role"]}), flush=True)
    deadline = time.monotonic() + 1400
    archive = queue / (run_id + ".zip")
    while not archive.is_file():
        if time.monotonic() > deadline:
            raise TimeoutError("No MATLAB worker artifact within validation time limit")
        time.sleep(1)
    with ZipFile(archive) as zipped:
        if sum(member.file_size for member in zipped.infolist()) > 50_000_000:
            raise ValueError("Oversized worker artifact")
        for member in zipped.infolist():
            name = PurePosixPath(member.filename)
            dest = output.joinpath(*name.parts)
            if name.is_absolute() or ".." in name.parts or not dest.resolve().is_relative_to(output):
                raise ValueError("Unsafe worker artifact path")
            if (member.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("Worker artifact contains a symlink")
            if member.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(zipped.read(member))
    if not response_path.is_file():
        raise RuntimeError("MATLAB worker artifact lacks its actual response")
    print(json.dumps({"validation_response": run_id}), flush=True)


if __name__ == "__main__":
    main()
