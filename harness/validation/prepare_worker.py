"""Materialize only an allowlisted, checksummed MATLAB validation request."""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys


def prepare(envelope_path, root, repository):
    envelope = json.loads(Path(envelope_path).read_text())
    if not envelope.get("provider_credential_absent") or "DEEPSEEK_API_KEY" in os.environ:
        raise ValueError("Validation worker must not receive the provider credential")
    run_id = envelope["run_id"]
    if not re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{12}", run_id):
        raise ValueError("Invalid run id")
    root = Path(root).resolve()
    workspace = root / "workspace"
    original = envelope["workspace"]
    request = envelope["request"]
    if request["operation"] != "menu" or request["menu"] not in {"menu_rgb2gray", "menu_interp"}:
        raise ValueError("Unknown validation operation")
    if request["role"] not in {"helper", "analyzer", "plotter", "replay"}:
        raise ValueError("Unknown validation role")
    if len(envelope["files"]) > 30:
        raise ValueError("Too many input files")
    for name, spec in envelope["files"].items():
        parts = PurePosixPath(name)
        dest = workspace.joinpath(*parts.parts)
        if parts.is_absolute() or ".." in parts.parts or not parts.parts or parts.parts[0] != ".acycle":
            raise ValueError("Unsafe input path")
        if not dest.resolve().is_relative_to(workspace):
            raise ValueError("Input path escape")
        if len(spec["base64"]) > 14_000_000:
            raise ValueError("Oversized input")
        data = base64.b64decode(spec["base64"], validate=True)
        if hashlib.sha256(data).hexdigest() != spec["sha256"]:
            raise ValueError("Input checksum mismatch")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)

    def relocate(value):
        if isinstance(value, str) and value.startswith(original + "/"):
            candidate = workspace / value[len(original) + 1:]
            if not candidate.resolve().is_relative_to(workspace):
                raise ValueError("Request path escape")
            return str(candidate)
        if isinstance(value, dict):
            return {key: relocate(item) for key, item in value.items()}
        if isinstance(value, list):
            return [relocate(item) for item in value]
        return value

    request = relocate(request)
    request["acycle_root"] = str(Path(repository).resolve())
    output = workspace / ".acycle/runs" / run_id / "outputs"
    if request["output_dir"] != str(output):
        raise ValueError("Mismatched output directory")
    output.mkdir(parents=True)
    (root / "request.json").write_text(json.dumps(request) + "\n")
    (output / "validation-provenance.json").write_text(json.dumps({
        "schema": 1, "run_id": run_id, "execution": "real MATLAB on GitHub Actions",
        "provider_credential_received": False, "model_runs_elsewhere": True,
        "commit": os.environ.get("GITHUB_SHA"), "workflow_run": os.environ.get("GITHUB_RUN_ID"),
        "original_input_checksums": {key: spec["sha256"] for key, spec in envelope["files"].items()},
    }, indent=2) + "\n")
    return output


if __name__ == "__main__":
    output = prepare(*sys.argv[1:])
    with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
        stream.write(f"output={output}\n")
