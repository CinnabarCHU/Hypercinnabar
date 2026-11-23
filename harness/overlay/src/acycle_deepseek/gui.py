"""Typed requests to the local session folder opened by the user's desktop."""
import json
import os
from pathlib import Path
import time
import uuid

PREFIX = "acycle_gui_"
NUMERIC_FILES = {".txt", ".csv", ".dat", ".tsv", ".mat"}
IMAGE_FILES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".gif"}


def run(workspace, action, args):
    session = Path(os.environ.get("ACYCLE_GUI_SESSION", ""))
    marker = session / "session.json"
    if not session.is_absolute() or not marker.is_file():
        raise ValueError("Open Connect to Acycle Harness and set guiSession to its local folder.")
    if json.loads(marker.read_text(encoding="utf-8")).get("protocol") != 1:
        raise ValueError("Unsupported Acycle desktop protocol.")
    q = dict(args)
    if action == "open":
        file = (workspace / Path(q["input_path"])).resolve()
        allowed = NUMERIC_FILES if q["feature"] == "filter" else IMAGE_FILES
        if not file.is_relative_to(workspace) or not file.is_file() or file.suffix.lower() not in allowed:
            raise ValueError("Choose a supported input file inside the active Harness workspace.")
        q["input_path"] = str(file)
    token = uuid.uuid4().hex
    temporary = session / (token + ".tmp")
    request = session / (token + ".request.json")
    response = session / (token + ".reply.json")
    timeout = 90
    try:
        temporary.write_text(json.dumps({"action": action, "arguments": q, "deadline": time.time() + timeout},
                                        allow_nan=False), encoding="utf-8")
        temporary.replace(request)
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if response.is_file():
                result = json.loads(response.read_text(encoding="utf-8"))
                if not result["ok"]:
                    raise RuntimeError(result["identifier"] + " " + result["message"])
                return json.loads(result["json"])
            if not marker.is_file():
                raise RuntimeError("The shared Acycle desktop closed.")
            time.sleep(.075)
        raise TimeoutError("The desktop did not reply in time. Inspect the window before retrying.")
    finally:
        for file in (temporary, request, response):
            file.unlink(missing_ok=True)


def schemas():
    if not os.environ.get("ACYCLE_GUI_SESSION"):
        return []
    text = {"type": "string"}
    revision = {"type": "integer", "minimum": 1}
    def patch(names):
        return {"type": "object", "additionalProperties": False, "minProperties": 1,
                "properties": {key: {"type": "number"} for key in names}}
    specs = [
        ("inspect", "List the live Acycle windows or inspect one window's committed parameters, units, revision and scientific record IDs.",
         {"window_id": text}, []),
        ("open", "Open the filter or nonblocking image-profile picker on the user's visible MATLAB desktop using a workspace file. Filter accepts a legacy bandpass MAT exchange. Rebinding the open filter requires its current window_id and expected_revision.",
         {"feature": {"type": "string", "enum": ["filter", "image_profile"]}, "input_path": text,
          "window_id": text, "expected_revision": revision}, ["feature", "input_path"]),
        ("update", "Apply one compound edit to the visible filter. Frequencies are in cycles per coordinate unit. Display-only edits reuse the original analyzer. On conflict, inspect the new state before acting.",
         {"window_id": text, "expected_revision": revision, "params": patch(["flow", "fhigh"]),
          "plt": patch(["x_1", "x_2", "y_1", "y_2"])}, ["window_id", "expected_revision"]),
        ("events", "Read committed changes, completed human-picked image coordinates or cancellation since a desktop event cursor. The call returns immediately. If resync is true, inspect the windows again.",
         {"window_id": text, "after": {"type": "integer", "minimum": 0}}, []),
    ]
    return [{"type": "function", "function": {"name": PREFIX + name, "description": desc,
             "parameters": {"type": "object", "properties": fields, "required": required,
                            "additionalProperties": False}}} for name, desc, fields, required in specs]
