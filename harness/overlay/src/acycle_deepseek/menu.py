"""Discover pinned menu roles and transport typed Acycle journals between MATLAB calls."""

from __future__ import annotations
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import shutil
from uuid import uuid4
from zipfile import ZipFile, ZIP_DEFLATED
from . import tools

REVISION = "74082d52da4b2800068577bd1e66a5a026d470c1"
DESKTOP = {"Desktop", "Robot"}
ROLES = ("helper", "analyzer", "plotter")
PREFIX = "acycle_menu_"


@lru_cache(maxsize=1)
def _catalog():
    raw = (tools._matlab_dir() / "menu_catalog.json").read_bytes()
    data = json.loads(raw)
    return (
        {m["tag"]: m for m in data["menus"]},
        {e["operation"]: e for e in data["engines"]},
        hashlib.sha256(raw).hexdigest(),
    )


def capabilities():
    menus, _, _ = _catalog()
    return {
        "catalog": PREFIX + "catalog",
        "roles": list(ROLES),
        "replay": PREFIX + "replay",
        "revision": REVISION,
        "entries": sum(bool(m["entry"]) for m in menus.values()),
        "backend": "local MATLAB",
        "runtime_configured": bool(os.environ.get("ACYCLE_MENU_ROOT")),
    }


def _menu(tag):
    menus, _, _ = _catalog()
    if not isinstance(tag, str) or tag not in menus:
        raise ValueError("Unknown menu tag. Search acycle_menu_catalog first.")
    return menus[tag]


def _engine(menu, operation, role):
    if not isinstance(operation, str) or operation not in menu["choices"].split():
        raise ValueError(f'Unknown operation for {menu["tag"]}: {operation!r}')
    spec = _catalog()[1][operation]
    if role not in menu["roles"].split() or (role != "helper" and role not in spec["roles"].split()):
        raise ValueError(f"{operation} has no {role} in the selected snapshot")
    if role == "plotter" and spec["package"] in DESKTOP:
        raise ValueError(f"{operation} requires an interactive Acycle desktop")
    return spec


def discover(args):
    menus, engines, _ = _catalog()
    if "menu" in args:
        m = _menu(args["menu"])
        if args.get("operation") is not None:
            op = args["operation"]
            if op not in m["choices"].split():
                raise ValueError(f'{op} is not registered under {m["tag"]}')
            e = engines[op]
            return {
                "menu": m["tag"],
                **e,
                "wrapper_roles": ["helper", *[k for k in e["roles"].split() if k != "helper"]],
                "desktop_required_to_execute": e["package"] in DESKTOP,
                "revision_pin": REVISION,
            }
        return {
            "menu": m["tag"],
            "master": m["master"],
            "guide": m["guide"],
            "default": m["default"],
            "roles": m["roles"].split(),
            "operations": m["choices"].split(),
            "revision_pin": REVISION,
        }
    if "operation" in args:
        raise ValueError("Supply menu with an exact operation lookup")
    query = args.get("query", "")
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    term = query.casefold()
    limit, offset = args.get("limit", 25), args.get("offset", 0)
    if type(limit) is not int or not 1 <= limit <= 136 or type(offset) is not int or offset < 0:
        raise ValueError("Invalid catalogue offset or limit")
    rows = [
        {
            "menu": m["tag"],
            "path": m["master"] or m["guide"],
            "default": m["default"],
            "roles": m["roles"].split(),
            "master_visibility": m["masterVisibility"],
        }
        for m in menus.values()
        if term in " ".join((m["tag"], m["master"], m["guide"], m["choices"])).casefold()
    ]
    return {
        "total": len(rows),
        "offset": offset,
        "items": rows[offset : offset + limit],
        "revision_pin": REVISION,
    }


def _object(value, name):
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")
    return value


def _parent(root, run_id, role=None, menu=None):
    record = tools._get(root, run_id)
    if (
        record.get("operation") != "menu"
        or record.get("status") != "completed"
        or record.get("completion") not in ("done", "incomplete")
        or record.get("revision_pin") != REVISION
    ):
        raise ValueError("Expected a completed menu run from this catalogue revision")
    if role and record["role"] != role or menu and record["menu"] != menu:
        raise ValueError("Source run belongs to a different menu or role")
    base = tools._run_path(root, run_id)
    path = (base / record["journal"]).resolve()
    if not path.is_relative_to(base / "outputs" / "journals") or not path.is_file():
        raise ValueError("Saved Acycle journal unavailable inside its run")
    return record, path


def _input(root, args, payload):
    if "input_path" not in args:
        if "input_kind" in args or "input_field" in args:
            raise ValueError("input_kind/input_field requires input_path")
        return None
    kind = args.get("input_kind", "matrix")
    field = args.get(
        "input_field", {"matrix": "data", "image": "im_name", "path": "inputfile"}.get(kind, "")
    )
    if (
        kind not in ("matrix", "image", "path")
        or not isinstance(field, str)
        or not re.fullmatch(r"[A-Za-z]\w{0,62}", field)
        or field == "operation"
    ):
        raise ValueError("Invalid input kind or MATLAB field")
    if field in payload.get("input", {}):
        raise ValueError(f"Input {field} supplied twice")
    source = (root / args["input_path"]).resolve()
    if not source.is_relative_to(root) or not source.is_file():
        raise ValueError("Menu input files must exist inside the Harness workspace")
    suffixes = {
        "matrix": {".txt", ".dat", ".csv", ".tsv"},
        "image": {".jpg", ".jpeg", ".tif", ".tiff", ".png", ".bmp"},
    }
    if kind in suffixes and source.suffix.lower() not in suffixes[kind]:
        raise ValueError(f"Unsupported {kind} file type")
    return source, kind, field


def _check_paths(root, node):
    """Keep explicit method destinations relative to the new run's working directory."""
    if isinstance(node, list):
        for item in node:
            _check_paths(root, item)
    if not isinstance(node, dict):
        return
    for key, value in node.items():
        field = key.lower()
        if isinstance(value, str) and value:
            if field in {
                "outputfile",
                "outputroot",
                "outputparent",
                "outputdirectory",
                "writedir",
                "basename",
            }:
                path = PureWindowsPath(value)
                if path.anchor or ".." in path.parts or (field == "basename" and len(path.parts) != 1):
                    raise ValueError(f"{key} must be a relative product name inside this run")
            if field in {"inputfile", "datapath"}:
                raise ValueError(
                    f"Supply {key} using helper input_path with input_kind=path and input_field={key}"
                )
            if field == "inputroot":
                path = (root / value).resolve()
                if not path.is_relative_to(root) or not path.is_dir():
                    raise ValueError("InputRoot must identify a directory inside the workspace")
                node[key] = str(path)
        else:
            _check_paths(root, value)


def _request(root, role, args):
    if role == "replay":
        previous, journal = _parent(root, args["run_id"])
        return (
            previous["menu"],
            previous["selector"],
            previous["role"],
            {"replay_journal": str(journal)},
            [args["run_id"]],
            None,
        )
    m = _menu(args["menu"])
    payload = {}
    refs = []
    for key in ("input", "override", "params", "plt", "dat"):
        if key in args:
            payload[key] = _object(args[key], key)
    if "res" in args:
        payload["res"] = args["res"]
    _check_paths(root, payload)
    source = None
    if role == "helper":
        override = payload.get("override", {})
        if set(override) - {"params", "plt"}:
            raise ValueError("Only override.params and override.plt are accepted")
        for name, val in override.items():
            _object(val, "override." + name)
        selector = override.get("params", {}).get(
            "operation", payload.get("input", {}).get("operation", m["default"])
        )
        source = _input(root, args, payload)
    else:
        helper = None
        if "helper_run_id" in args:
            helper, path = _parent(root, args["helper_run_id"], "helper", m["tag"])
            payload["helper_journal"] = str(path)
            refs.append(args["helper_run_id"])
        params = payload.get("params", {})
        if role == "analyzer":
            if ("params" in args) == (helper is not None):
                raise ValueError("Supply either complete params or helper_run_id")
            selector = helper["selector"] if helper else params.get("operation")
        else:
            analyzer = None
            if "analyzer_run_id" in args:
                if "res" in args:
                    raise ValueError("Supply res or analyzer_run_id once")
                analyzer, path = _parent(root, args["analyzer_run_id"], "analyzer", m["tag"])
                payload["analyzer_journal"] = str(path)
                refs.append(args["analyzer_run_id"])
            prepared = helper.get("plot_selector", helper["selector"]) if helper else None
            selector = (
                payload.get("plt", {}).get("operation")
                or params.get("operation")
                or prepared
                or (analyzer and analyzer["selector"])
            )
            if helper and prepared != selector or analyzer and analyzer["selector"] != selector:
                raise ValueError("The source runs and plot selector must agree")
            if not helper and "plt" not in args and "params" not in args:
                raise ValueError("Supply plot settings in plt or a helper_run_id")
            payload["target_kind"] = args.get("target", "original")
            if payload["target_kind"] not in ("original", "figure", "axes"):
                raise ValueError("target must be original, figure or axes")
    _engine(m, selector, role)
    return m["tag"], selector, role, payload, refs, source


def _journal(output, relative):
    journal = (output / relative).resolve()
    if not journal.is_relative_to(output / "journals") or not journal.is_file():
        raise ValueError("MATLAB did not return its Acycle journal")
    return journal


def _save_journal(directory, output, record, relative):
    journal = _journal(output, relative)
    record["journal"] = str(journal.relative_to(directory))
    exchange = output / "acycle-journal.zip"
    with ZipFile(exchange, "w", ZIP_DEFLATED) as archive:
        for sidecar in sorted(journal.parent.iterdir()):
            if sidecar.is_file() and not sidecar.is_symlink():
                archive.write(sidecar, sidecar.name)
    record["artifacts"]["journal_zip"] = str(exchange)


def run(root, role, args):
    menu, selector, effective, payload, refs, source = _request(root, role, args)
    runtime = Path(os.environ.get("ACYCLE_MENU_ROOT", "")).expanduser().resolve()
    api = runtime / "code/interface/catalogue.json"
    if (
        not os.environ.get("ACYCLE_MENU_ROOT")
        or not api.is_file()
        or hashlib.sha256(api.read_bytes()).hexdigest() != _catalog()[2]
    ):
        raise ValueError("Set ACYCLE_MENU_ROOT to the matching initialized Acycle menu checkout")
    if os.environ.get("ACYCLE_BACKEND", "local") != "local":
        raise ValueError("Menu journals require the local MATLAB backend")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid4().hex[:12]
    directory = tools._run_path(root, run_id)
    output = directory / "outputs"
    output.mkdir(parents=True)
    record = {
        "run_id": run_id,
        "operation": "menu",
        "role": effective,
        "action": role,
        "menu": menu,
        "selector": selector,
        "revision_pin": REVISION,
        "status": "running",
        "source_runs": refs,
        "parent_run_id": refs[0] if refs else None,
        "output_dir": str(output),
        "artifacts": {},
    }
    tools._write(directory / "result.json", record)
    try:
        if source:
            path, kind, field = source
            staging = directory / "inputs"
            staging.mkdir()
            frozen = staging / path.name
            shutil.copyfile(path, frozen)
            record["input_sha256"] = hashlib.sha256(frozen.read_bytes()).hexdigest()
            payload["file_input"] = {"path": str(frozen), "kind": kind, "field": field}
        response = tools._execute(
            {
                "operation": "menu",
                "acycle_root": str(runtime),
                "menu": menu,
                "role": role,
                "payload": payload,
                "output_dir": str(output),
            }
        )
        _save_journal(directory, output, record, response["journal"])
        if response["completion"] not in ("done", "incomplete", "cancelled"):
            raise ValueError("Invalid Acycle completion status")
        record.update(
            status="completed",
            completion=response["completion"],
            summary=response["summary"],
            plot_selector=response.get("plot_selector", selector),
        )
        for name in response.get("files", []):
            if Path(name).name != name or not (output / name).is_file():
                raise ValueError("Invalid figure artifact")
            record["artifacts"][Path(name).stem] = str(output / name)
        products = output / "products"
        for product in sorted(products.rglob("*")):
            if (
                product.is_file()
                and not product.is_symlink()
                and product.resolve().is_relative_to(products)
            ):
                record["artifacts"]["product:" + product.relative_to(products).as_posix()] = str(product)
    except Exception as error:
        record.update(status="failed", error=str(error))
        details = output / "response.json"
        if details.is_file():
            try:
                failure = json.loads(details.read_text())
                record["diagnostics"] = failure.get("error", {})
                if failure.get("journal"):
                    _save_journal(directory, output, record, failure["journal"])
                    if failure.get("completion") in ("cancelled", "incomplete", "done"):
                        record["completion"] = failure["completion"]
            except (OSError, ValueError, TypeError) as diagnostics_error:
                record["journal_error"] = str(diagnostics_error)
        tools._write(directory / "result.json", record)
        raise tools.RunError(record) from error
    tools._write(directory / "result.json", record)
    return record


def schemas():
    string = {"type": "string"}
    obj = {"type": "object", "additionalProperties": True}

    def spec(name, description, fields, required=()):
        return {
            "type": "function",
            "function": {
                "name": PREFIX + name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": fields,
                    "required": list(required),
                    "additionalProperties": False,
                },
            },
        }

    return [
        spec(
            "catalog",
            "Find a GUI menu by query. With menu, list version choices. With menu and operation, inspect required fields and roles. GUIDE choices end in _legacy.",
            {
                "query": string,
                "menu": string,
                "operation": string,
                "limit": {"type": "integer", "minimum": 1, "maximum": 136},
                "offset": {"type": "integer", "minimum": 0},
            },
        ),
        spec(
            "helper",
            "Resolve a menu input into params, plt and dat. Select a version in input.operation or override.params.operation. Only helper accepts override. Its run_id retains full typed values.",
            {
                "menu": string,
                "input": obj,
                "override": obj,
                "input_path": string,
                "input_field": string,
                "input_kind": {"enum": ["matrix", "image", "path"], "type": "string"},
            },
            ["menu"],
        ),
        spec(
            "analyzer",
            "Compute with complete params OR a helper_run_id for the same menu. No defaults or overrides. Results remain available by run_id.",
            {"menu": string, "params": obj, "helper_run_id": string},
            ["menu"],
        ),
        spec(
            "plotter",
            "Render saved MATLAB results. Supply a helper_run_id or full plt, plus analyzer_run_id or res when needed. Explicit branches replace the corresponding full branch. For multi-panel axes use plt.panel.",
            {
                "menu": string,
                "helper_run_id": string,
                "analyzer_run_id": string,
                "params": obj,
                "plt": obj,
                "dat": obj,
                "res": {},
                "target": {"type": "string", "enum": ["original", "figure", "axes"]},
            },
            ["menu"],
        ),
        spec(
            "replay",
            "Replay one saved menu invocation in a fresh run using its Acycle journal and initial RNG state.",
            {"run_id": string},
            ["run_id"],
        ),
    ]
