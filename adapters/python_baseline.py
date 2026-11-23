"""Independent NumPy/SciPy baselines. Reads only a prepared request directory."""
import argparse
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.interpolate import interp1d
from scipy.signal import detrend, find_peaks, lombscargle, periodogram
from scipy.stats import chi2
import classic_studies
import synthetic_models


def read(folder, name="data"):
    return np.loadtxt(folder / (name + ".csv"), delimiter=",", skiprows=1, ndmin=2)


def write(folder, filename, labels, values):
    np.savetxt(folder / filename, values, delimiter=",", header=",".join(labels), comments="", fmt="%.17g")


def numerical(req, folder):
    op, params = req["operation"], req["params"]
    data = read(folder)
    if op in synthetic_models.OPERATIONS:
        controls = read(folder, "controls") if op in {"segmented_clock", "weak_band"} else None
        return synthetic_models.evaluate(op, data, params, controls)
    x, y = data.T
    if op == "linear":
        n = int(np.floor((x[-1]-x[0])/params["step"] + 1e-10)) + 1
        g = x[0] + np.arange(n) * params["step"]
        return np.column_stack((g, np.interp(g, x, y)))
    if op == "tune":
        z, t = read(folder, "controls").T
        order = np.argsort(x)
        x, y = x[order], y[order]
        if not params["extrapolate"]:
            keep = (x >= z.min()) & (x <= z.max())
            x, y = x[keep], y[keep]
        return np.column_stack((interp1d(z, t, fill_value="extrapolate")(x), y))
    if op == "constant_rate":
        return np.column_stack((params["begin_ka"] + (x-x[0])/params["rate_m_per_ka"], y))
    if op == "integrate_rate":
        step = np.diff(x).min()
        z = x[0] + np.arange(round((x[-1]-x[0])/step)+1)*step
        inv = 100 / np.interp(z, x, y)
        return np.column_stack((z, np.r_[0, np.cumsum(np.diff(z)*(inv[1:]+inv[:-1])/2)]))
    if op == "periodogram":
        f, p = periodogram(y, fs=1/params["sample_interval"], detrend=False, nfft=params["nfft"])
        return np.column_stack((f,p))
    raise ValueError(f"No Python reproduction adapter for {op}")


def spectral_rate(x, y, periods, rates):
    order = np.argsort(x)
    x, y = x[order], y[order]
    dx = np.median(np.diff(np.unique(x)))
    grid = np.arange(x[0], x[-1], dx)
    f, power = periodogram(np.interp(grid, x, y), fs=1/dx, window="hann", detrend="linear",
                           nfft=4*len(grid))
    # Each astronomical component gets the same weight in log-power space.
    target = 100 / (np.asarray(periods)[:,None] * rates)
    logp = np.log(np.maximum(power, np.finfo(float).tiny))
    score = np.interp(target, f, logp, left=-np.inf, right=-np.inf).mean(axis=0)
    return float(rates[np.argmax(score)])


def calibrated_detection(y):
    # Fit AR(1), whiten, test the two prescribed frequencies with a Bonferroni correction.
    y = detrend(y)
    rho = np.dot(y[:-1],y[1:])/np.dot(y[:-1],y[:-1])
    v = y[1:] - rho*y[:-1]
    t = np.arange(len(v))
    power = lombscargle(t, v-v.mean(), 2*np.pi/np.array([23.,41.]))
    return int(np.min(chi2.sf(2*power/np.var(v), df=2))*2 < .05)


def science(req, folder, out):
    name, p = req["id"], req["params"]
    if name in classic_studies.TASK_IDS:
        return classic_studies.evaluate(name, folder, out, p)
    if name in ("cip1-case3","meishan-tuning") or name.startswith("odp846-oracle-"):
        queries=read(folder,"queries")
        if name.startswith("odp846-oracle-"):
            anchors=read(folder,"controls")
            times=np.empty(len(queries))
            for seg in np.unique(queries[:,0]):
                keep=queries[:,0]==seg
                local=anchors[anchors[:,0]==seg]
                times[keep]=np.interp(queries[keep,1],local[:,1],local[:,2])
        elif name=="meishan-tuning":
            anchors=read(folder,"anchors")
            times=np.interp(queries[:,1],anchors[:,0],anchors[:,1])
        else:
            x,y=read(folder).T
            # Plain constant-rate positive-control model using the dominant long wavelength.
            f,powr=periodogram(y,fs=1/np.median(np.diff(x)),window="hann",nfft=4*len(x))
            band=(f>=1/28)&(f<=1/12)
            times=queries[:,1]*405*f[band][np.argmax(powr[band])]
        write(out,"prediction.csv",["segment","coordinate_m","time_ka"],np.column_stack((queries,times)))
        return
    if name.startswith("laurin-"):
        window=read(folder,"windows")
        query=read(folder,"queries")[:,0]
        initial=np.interp(query,window[:,1],window[:,0]*p["assigned_period_ka"])
        return {f"interval_{i}_ka":value for i,value in enumerate(np.diff(initial),1)}
    if name.startswith("anticosti-"):
        x,y=read(folder).T
        periods=p["targetP_ka"] if p["template"]=="precession" else p["targetE_ka"]
        rate=spectral_rate(x,y,periods,np.linspace(20,60,201))
        return dict(rate_cm_per_ka=rate,duration_ka=np.ptp(x)*100/rate)
    if name == "cenogrid-modulation":
        result = {}
        for i, isotope in enumerate(("carbon","oxygen")):
            t,y = read(folder, isotope).T
            f,s = periodogram(y, fs=1/np.median(np.diff(t)), window="hann", nfft=5*len(t))
            for j,(lo,hi) in enumerate(p["bands_per_ka"][2*i:2*i+2],1):
                mask=(f>=lo)&(f<=hi)
                result[f"{isotope}_{j}_myr"]=.001/f[mask][np.argmax(s[mask])]
        return result
    if name == "synthetic-detection":
        data = read(folder)
        ids = np.unique(data[:,0])
        predictions = [calibrated_detection(data[data[:,0] == i,2]) for i in ids]
        write(out,"prediction.csv",["record_id","detected"],np.column_stack((ids,predictions)))
        return
    x,y = read(folder).T
    if name == "lr04-gaps":
        ages = read(folder,"queries")[:,0]
        write(out,"prediction.csv",["age_ka","benthic_d18O_permil"],np.column_stack((ages,np.interp(ages,x,y))))
        return
    if name == "synthetic-rate-step":
        results = {}
        for key, (lo,hi) in zip(("first_cm_per_ka","second_cm_per_ka"),read(folder,"windows")):
            mask=(x>=lo)&(x<=hi)
            results[key]=spectral_rate(x[mask],y[mask],p["target_periods_ka"],np.linspace(2,8,301))
        return results
    if name == "lavernock":
        f=np.linspace(1/.88,1/.74,321)
        power=lombscargle(x,y-y.mean(),2*np.pi*f)
        peaks=find_peaks(power)[0]
        if not len(peaks):
            return dict(wavelength_m=None,peak_power=None,fdr05_power=None)
        k=peaks[np.argmax(power[peaks])]
        return dict(wavelength_m=1/f[k],peak_power=power[k],fdr05_power=None)
    if name.startswith("bridge-"):
        z, age, sigma = read(folder,"dates").T
        design=np.column_stack((np.ones_like(z),z))
        cov=np.linalg.inv((design.T/sigma**2)@design)
        coef=cov@((design.T/sigma**2)@age)
        boundary=np.array([1.,p["ctb_position_m"]])
        est=boundary@coef
        hw=1.96*np.sqrt(boundary@cov@boundary)
        return dict(ctb_age_ma=est,ci95_ma=[est-hw,est+hw])
    if name in ("odp926b-timeopt","la-thure-coco","petm-published","petm-broad"):
        periods=p.get("orbital_periods_kyr",p.get("target_periods_ka",[95,125,23.62,22.32,19.07]))
        bounds=(1.3,5) if name=="odp926b-timeopt" else ((3,20) if name=="la-thure-coco" else (.13,30))
        estimate=spectral_rate(x,y,periods,np.linspace(*bounds,300))
        return dict(rate_cm_per_ka=estimate,global_p=None) if name.startswith("petm-") else dict(rate_cm_per_ka=estimate)
    raise ValueError(f"No Python baseline for {name}")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request",type=Path)
    parser.add_argument("submission",type=Path)
    a=parser.parse_args()
    req=json.loads((a.request/"request.json").read_text())
    a.submission.mkdir(parents=True,exist_ok=True)
    if req["track"]=="case":
        result=numerical(req,a.request)
        write(a.submission,"result.csv",req["output_columns"],result)
    else:
        result=science(req,a.request,a.submission)
        if result is not None:
            (a.submission/"result.json").write_text(json.dumps(result,allow_nan=False)+"\n")
    meta = {"method":"portable-baseline","version":f"NumPy {np.__version__}, SciPy {scipy.__version__}"}
    if req["id"] in classic_studies.TASK_IDS:
        meta["operation"] = classic_studies.METHOD_DETAILS.get(req["id"], classic_studies.JOINT_SCAN)
    (a.submission/"method.json").write_text(json.dumps(meta)+"\n")


if __name__=="__main__":
    main()
