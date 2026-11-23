"""Run a prepared feature case through one of the original Python interfaces."""
import argparse
import json
from pathlib import Path

import pandas as pd


def thin(operation, params, data, controls):
    from astrochron_rpy2 import __version__, astrochron, call_frame, package_version

    flags = {"genplot": False, "verbose": False}
    if operation == "tune":
        out = call_frame(astrochron.tune, data, controls, extrapolate=params["extrapolate"], **flags)
    elif operation == "constant_rate":
        out = call_frame(astrochron.constantSedrate, data, params["rate_m_per_ka"], begin=params["begin_ka"], **flags)
    elif operation == "integrate_rate":
        out = call_frame(astrochron.sedrate2time, data, **flags)
    elif operation == "linear":
        out = call_frame(astrochron.linterp, data, dt=params["step"], **flags)
    elif operation == "ar1":
        from rpy2 import robjects

        ar1 = astrochron.ar1
        robjects.r["RNGkind"]("Mersenne-Twister", "Inversion", "Rejection")
        robjects.globalenv[".Random.seed"] = robjects.IntVector(params["rng_state"])
        out = call_frame(ar1, npts=params["npts"], rho=params["rho"], **flags)
    else:
        raise ValueError(f"Unsupported raw interface operation: {operation}")
    return out, {"method": "astrochron-rpy2", "version": __version__, "astrochron": package_version()}


def warp(operation, params, data, controls):
    from astrochron_warp import AstrochronWarp, __version__

    client = AstrochronWarp()
    if operation == "tune":
        result = client.tune(data, controls, extrapolate=params["extrapolate"])
    elif operation == "constant_rate":
        result = client.constant_sedrate(data, params["rate_m_per_ka"], begin=params["begin_ka"])
    elif operation == "integrate_rate":
        result = client.sedrate_to_time(data)
    else:
        raise ValueError(f"Unsupported domain interface operation: {operation}")
    return result.data, {"method": "astrochron-warp", "version": __version__, "astrochron": result.astrochron_version}


def read_input(folder, stem):
    path = folder / f"{stem}.csv"
    if path.exists():
        return pd.read_csv(path, dtype=float, float_precision="round_trip")
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("backend", choices=["rpy2", "warp"])
    parser.add_argument("request", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    request = json.loads((args.request / "request.json").read_text())
    run = thin if args.backend == "rpy2" else warp
    out, method = run(request["operation"], request["params"], read_input(args.request, "data"),
                      read_input(args.request, "controls"))
    out.columns = request["output_columns"]
    args.output.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output / "result.csv", index=False, float_format="%.17g")
    (args.output / "method.json").write_text(json.dumps(method, indent=2) + "\n")


if __name__ == "__main__":
    main()
