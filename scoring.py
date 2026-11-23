"""Unit-aware scores for external implementations. All inputs are public."""
from __future__ import annotations

import csv
import json
import math

import numpy as np

from fixtures import case_tables, detection_panel, lr04_data
from records import ROOT


def read_json(path):
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"Duplicate JSON field {key}")
            obj[key] = value
        return obj

    def invalid(value):
        raise ValueError(f"Non-finite JSON token {value}")
    obj = json.loads(path.read_text(), object_pairs_hook=unique, parse_constant=invalid)
    if not isinstance(obj, dict):
        raise ValueError(f"{path.name} must be a JSON object")
    return obj


def number(value, field):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{field} requires a finite number")
    return float(value)


def read_table(path, headers):
    with path.open(newline="") as stream:
        reader = csv.reader(stream)
        if next(reader, None) != headers:
            raise ValueError(f"{path.name} requires the ordered header {','.join(headers)}")
        rows = list(reader)
    if not rows or any(len(row) != len(headers) for row in rows):
        raise ValueError(f"{path.name} is empty or has an incorrect row width")
    arr = np.array(rows, dtype=float)
    if not np.isfinite(arr).all():
        raise ValueError(f"{path.name} contains a non-finite number")
    return arr


def score_case(case, submission):
    got = read_table(submission / "result.csv", case["output_columns"])
    _, ref = case_tables(case)
    if got.shape != ref.shape:
        raise ValueError(f"Expected array {ref.shape}, received {got.shape}")
    metrics = {}
    for col, name in enumerate(case["output_columns"]):
        delta = np.abs(got[:, col] - ref[:, col])
        rtol = case["rtol"] if col else min(case["rtol"], 1e-11)
        atol = case["atol"] if col else min(case["atol"], 1e-12)
        override = case.get("column_tolerances", {}).get(name)
        if override:
            rtol, atol = override["rtol"], override["atol"]
        within = delta <= atol + rtol * np.abs(ref[:, col])
        metrics[name] = dict(max_abs_error=float(delta.max()), failures=int((~within).sum()),
                             max_error_row=int(delta.argmax()) + 1, atol=atol, rtol=rtol)
    match = all(m["failures"] == 0 for m in metrics.values())
    return {"status": "match" if match else "mismatch", "rows": len(got), "columns": metrics}


def score_predictions(kind, submission):
    if kind == "reconstruction":
        pred = read_table(submission / "prediction.csv", ["age_ka", "benthic_d18O_permil"])
        _, ref, block = lr04_data()
        if pred.shape != ref.shape or not np.array_equal(pred[:, 0], ref[:, 0]):
            raise ValueError("Predictions must cover every withheld age exactly once, in query order")
        err = pred[:, 1] - ref[:, 1]
        out = {}
        for label, group in [("isolated", ~block), ("block", block), ("all", np.ones_like(block))]:
            out[label] = dict(n=int(group.sum()), rmse_permil=float(np.sqrt(np.mean(err[group]**2))),
                              bias_permil=float(err[group].mean()))
        return {"status": "scored", "metrics": out}
    pred = read_table(submission / "prediction.csv", ["record_id", "detected"])
    _, truth = detection_panel()
    if (pred.shape != (len(truth), 2) or not np.array_equal(pred[:, 0], np.arange(len(truth))) or
            not np.isin(pred[:, 1], [0, 1]).all()):
        raise ValueError("Supply all record IDs in order with one binary decision each")
    positive = pred[:, 1].astype(bool)
    tp = int(positive[truth == 1].sum())
    fp = int(positive[truth == 0].sum())
    n1, n0 = int(truth.sum()), int((truth == 0).sum())
    return {"status": "scored", "metrics": dict(true_positive=tp, false_positive=fp,
            n_signal=n1, n_null=n0, sensitivity=tp/n1, false_positive_rate=fp/n0,
            balanced_accuracy=(tp/n1 + 1-fp/n0)/2)}


def clock_ensemble(path, reference):
    with path.open(newline="") as stream:
        header = next(csv.reader(stream), [])
    count = len(header)-2
    if count < 2:
        raise ValueError("An ensemble requires at least two complete age curves")
    expected = ["segment","coordinate_m"] + [f"draw_{i+1}" for i in range(count)]
    sample = read_table(path, expected)
    if (sample.shape[0] != len(reference) or not np.array_equal(sample[:,0],reference[:,0])
            or not np.allclose(sample[:,1],reference[:,1],rtol=0,atol=1e-8)):
        raise ValueError("Ensemble coordinates must match the query grid")
    draws = sample[:,2:]
    if np.any(np.diff(draws, axis=0) < 0):
        raise ValueError("Each ensemble member must be a complete monotone chronology")
    # Half the mean of all pairwise absolute differences via sorted order statistics.
    weights = (2*np.arange(1,count+1)-count-1) / count**2
    spread = np.sort(draws-draws[:,:1],axis=1) @ weights
    crps = np.abs(draws-reference[:,2,None]).mean(axis=1)-spread
    lo,hi = np.quantile(draws,[.05,.95],axis=1)
    return dict(draws=count,mean_crps_ka=float(crps.mean()),mean_90pct_width_ka=float((hi-lo).mean()),
                reference_in_90pct_fraction=float(np.mean((lo<=reference[:,2])&(reference[:,2]<=hi))))


def score_task(task, submission):
    metrics = task["metrics"]
    if metrics[0]["kind"] == "clock":
        cols = ["segment", "coordinate_m", "time_ka"]
        candidate = read_table(submission / "prediction.csv", cols)
        ref = read_table(ROOT / task["reference_file"], cols)
        if (candidate.shape != ref.shape or not np.array_equal(candidate[:,0], ref[:,0])
                or not np.allclose(candidate[:,1], ref[:,1], atol=1e-8, rtol=0)):
            raise ValueError("Return all requested segments and coordinates in query order")
        if np.any(np.diff(candidate[:,2]) < 0):
            raise ValueError("Time must increase monotonically through the section, including across gaps")
        delta = candidate[:,2] - ref[:,2]
        stats = dict(rmse_ka=float(np.sqrt(np.mean(delta**2))), max_abs_ka=float(np.max(np.abs(delta))),
                     mae_ka=float(np.mean(np.abs(delta))),
                     end_minus_start_error_ka=float(delta[-1]-delta[0]), rows=len(ref))
        if "reference_record" in task:
            stats["endpoint_errors_ka"] = delta[[0,-1]].tolist()
            stats["interior_rmse_ka"] = float(np.sqrt(np.mean(delta[1:-1]**2)))
            stats["interior_rows"] = len(ref)-2
        if (submission / "ensemble.csv").is_file():
            stats["ensemble"] = clock_ensemble(submission / "ensemble.csv", ref)
        if task.get("params", {}).get("target_ka") == 405:
            segment = (ref[:,1] >= 269.85) & (ref[:,1] <= 343.95)
            stats["disputed_interval_duration_error_ka"] = float(np.ptp(candidate[segment,2]) - np.ptp(ref[segment,2]))
        return {"status":"scored", "metrics":stats}
    if metrics[0]["kind"] in ("reconstruction", "detection"):
        return score_predictions(metrics[0]["kind"], submission)
    values = read_json(submission / "result.json")
    required = set(task["output_fields"])
    if set(values) != required:
        raise ValueError(f"result.json requires exactly {sorted(required)}")
    if "peak_power" in values:
        # A threshold is meaningful only when it applies to a selected peak.
        if (values["peak_power"] is None) != (values["wavelength_m"] is None):
            raise ValueError("Supply peak power and wavelength together")
        if values["wavelength_m"] is None and values["fdr05_power"] is not None:
            raise ValueError("A threshold without a selected peak cannot be scored")
        for field in ("peak_power", "fdr05_power"):
            if values[field] is not None and number(values[field], field) < 0:
                raise ValueError(f"{field} must be nonnegative")
    results = []
    for metric in metrics:
        key, kind = metric["field"], metric["kind"]
        if kind == "period_ratio":
            numerator = number(values[metric["numerator"]], metric["numerator"])
            denominator = number(values[metric["denominator"]], metric["denominator"])
            if numerator <= 0 or denominator <= 0:
                raise ValueError("Periods used in the frequency ratio test must be positive")
            value = numerator / denominator
        else:
            value = values[key]
        out = {"field": key, "quantity": kind, "value": value}
        if "comparison" in metric:
            out["comparison"] = metric["comparison"]
        results.append(out)
        if kind == "p_value":
            if value is not None and not 0 <= number(value, key) <= 1:
                raise ValueError(f"{key} must be null or in [0,1]")
            continue
        if kind == "fdr":
            out["available"] = value is not None
            out["met"] = value is not None and values["peak_power"] > value
            continue
        if kind == "interval":
            out["unit"] = metric["unit"]
            if value is not None:
                if not isinstance(value, list) or len(value) != 2:
                    raise ValueError(f"{key} must contain two ordered numbers")
                lo, hi = [number(v, key) for v in value]
                if lo > hi:
                    raise ValueError(f"{key} endpoints must be ordered")
                if "center_field" in metric and not lo <= values[metric["center_field"]] <= hi:
                    raise ValueError("Declared interval must contain the reported median")
                rlo, rhi = metric["reference_bounds"]
                out.update(width=hi-lo, lower_difference=lo-rlo, upper_difference=hi-rhi)
            continue
        out["unit"] = metric["unit"]
        if metric.get("optional") and value is None:
            out["available"] = False
            out["reference"] = metric["reference"]
            continue
        if key == "wavelength_m" and value is None:
            out["met"] = False
            continue
        x = number(value, key)
        if x <= 0:
            raise ValueError(f"{key} must be positive")
        if "reference" in metric:
            out["reference"] = metric["reference"]
            out["absolute_difference"] = abs(x - metric["reference"])
        if kind == "range":
            lo, hi = metric["bounds"]
            out.update(bounds=[lo,hi], distance_to_range=max(lo-x, 0., x-hi), met=lo <= x <= hi)
    gates = [item["met"] for item in results if "met" in item]
    status = ("criterion_met" if all(gates) else "criterion_unmet") if gates else "scored"
    return {"status": status, "metrics": results}
