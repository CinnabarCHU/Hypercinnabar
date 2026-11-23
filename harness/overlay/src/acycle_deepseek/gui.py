"""Typed Harness requests for an existing named MATLAB desktop."""
from io import StringIO
import json
import os
from pathlib import Path
import re

PREFIX = "acycle_gui_"
NUMERIC_FILES = {".txt", ".csv", ".dat", ".tsv", ".mat"}
IMAGE_FILES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".gif"}


def run(workspace, action, args):
    name = os.environ.get("ACYCLE_GUI_ENGINE", "")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,62}", name):
        raise ValueError("Configure guiEngine with the name displayed by the Acycle desktop.")
    q = dict(args)
    if action == "open":
        file = (workspace / Path(q["input_path"])).resolve()
        allowed = NUMERIC_FILES if q["feature"] == "filter" else IMAGE_FILES
        if not file.is_relative_to(workspace) or not file.is_file() or file.suffix.lower() not in allowed:
            raise ValueError("Choose a supported input file inside the active Harness workspace.")
        q["input_path"] = str(file)
    try:
        import matlab.engine as matlab_engine
    except ImportError as err:
        raise RuntimeError("Install the MATLAB Engine for Python matching your desktop release.") from err
    # Naming is deliberate. An unspecified name may start a different MATLAB.
    engine = matlab_engine.connect_matlab(name)
    try:
        value = engine.feval("acgui.live", action, json.dumps(q, allow_nan=False), nargout=1,
                             stdout=StringIO(), stderr=StringIO())
        return json.loads(value)
    finally:
        engine.quit()  # Detach this client from the user-owned shared session.


def schemas():
    if not os.environ.get("ACYCLE_GUI_ENGINE"):
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
