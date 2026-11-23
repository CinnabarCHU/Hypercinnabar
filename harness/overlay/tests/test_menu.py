from zipfile import ZipFile

import pytest

from acycle_deepseek import menu, tools


def test_catalogue_matches_actual_menus_and_preserves_versions(tmp_path):
    rows = tools.dispatch("acycle_menu_catalog", {"limit": 136}, tmp_path)
    assert rows["total"] == len(rows["items"]) == 136
    assert menu.capabilities()["entries"] == 118
    assert sum(len(m["choices"].split()) for m in menu._catalog()[0].values()) == 758
    for m in menu._catalog()[0].values():
        for op in m["choices"].split():
            detail = menu.discover({"menu": m["tag"], "operation": op})
            assert detail["revision"] == ("guide" if op.endswith("_legacy") else "master")
            assert "helper" in detail["wrapper_roles"]
    found = menu.discover({"query": "RGB to Grayscale", "limit": 1})
    assert found["items"][0]["menu"] == "menu_rgb2gray"
    assert menu.discover({"menu": "menu_timeOpt"})["default"] == "TimeOpt_legacy"
    assert menu.discover({"menu": "menu_imshow", "operation": "Desktop"})["desktop_required_to_execute"]


@pytest.mark.parametrize(
    "role,args,match",
    [
        ("analyzer", {}, "complete params"),
        ("analyzer", {"params": {}}, "Unknown operation"),
        ("analyzer", {"params": {"operation": "RGBToGray"}, "override": {}}, "unknown"),
        ("plotter", {"plt": {"operation": "Desktop"}}, "interactive"),
        ("helper", {"override": {"dat": {}}}, "override"),
        ("helper", {"input": {"operation": "madeUp"}}, "Unknown operation"),
        ("helper", {"input_kind": "image"}, "input_path"),
        ("helper", {"input": {"outputFile": "../result.xlsx"}}, "relative product"),
        ("helper", {"input": {"dataPath": "/tmp/other"}}, "input_path"),
    ],
)
def test_reject_unusable_calls_before_science(tmp_path, role, args, match):
    with pytest.raises(ValueError, match=match):
        tools.dispatch("acycle_menu_" + role, {"menu": "menu_rgb2gray", **args}, tmp_path)
    assert not (tmp_path / ".acycle").exists()


def test_workspace_refs_and_journal_archive(tmp_path):
    old = "20261123T120000Z-001122334455"
    directory = tools._run_path(tmp_path, old)
    journals = directory / "outputs/journals/call"
    journals.mkdir(parents=True)
    event = journals / "events.jsonl"
    event.write_text("journal fixture")
    (journals / "retval.mat").write_bytes(b"transport fixture")
    (journals / "outside").symlink_to(tmp_path / "elsewhere")
    record = {
        "run_id": old,
        "status": "completed",
        "completion": "incomplete",
        "operation": "menu",
        "role": "helper",
        "selector": "RGBToGray_legacy",
        "menu": "menu_rgb2gray",
        "revision_pin": menu.REVISION,
        "artifacts": {},
    }
    menu._save_journal(directory, directory / "outputs", record, "journals/call/events.jsonl")
    tools._write(directory / "result.json", record)
    with ZipFile(record["artifacts"]["journal_zip"]) as z:
        assert set(z.namelist()) == {"events.jsonl", "retval.mat"}
    tag, op, role, request, refs, _ = menu._request(
        tmp_path, "analyzer", {"menu": "menu_rgb2gray", "helper_run_id": old}
    )
    assert (tag, op, role, refs) == ("menu_rgb2gray", "RGBToGray_legacy", "analyzer", [old])
    assert request == {"helper_journal": str(event)}
    for action, args, match in [
        ("analyzer", {"menu": "menu_sound", "helper_run_id": old}, "different menu"),
        ("analyzer", {"menu": "menu_rgb2gray", "helper_run_id": old, "params": {}}, "either"),
        (
            "plotter",
            {"menu": "menu_rgb2gray", "helper_run_id": old, "plt": {"operation": "RGBToGray"}},
            "agree",
        ),
    ]:
        with pytest.raises(ValueError, match=match):
            menu._request(tmp_path, action, args)
    record["completion"] = "cancelled"
    tools._write(directory / "result.json", record)
    with pytest.raises(ValueError, match="completed menu run"):
        menu._request(tmp_path, "replay", {"run_id": old})


def test_menu_files_and_backend_preflight(tmp_path, monkeypatch):
    runtime = tmp_path / "checkout/code/interface"
    runtime.mkdir(parents=True)
    (runtime / "catalogue.json").write_bytes((tools._matlab_dir() / "menu_catalog.json").read_bytes())
    monkeypatch.setenv("ACYCLE_MENU_ROOT", str(tmp_path / "checkout"))
    monkeypatch.setenv("ACYCLE_BACKEND", "github")
    with pytest.raises(ValueError, match="local MATLAB"):
        tools.dispatch("acycle_menu_helper", {"menu": "menu_rgb2gray"}, tmp_path)
    with pytest.raises(ValueError, match="inside the Harness workspace"):
        menu._input(tmp_path, {"input_path": "../not-a-file.csv"}, {})
    path = tmp_path / "series.csv"
    path.write_text("0,0\n1,2\n")
    assert menu._input(tmp_path, {"input_path": "series.csv"}, {}) == (path, "matrix", "data")
    (runtime / "catalogue.json").write_text("{}")
    with pytest.raises(ValueError, match="matching"):
        tools.dispatch("acycle_menu_helper", {"menu": "menu_rgb2gray"}, tmp_path)
