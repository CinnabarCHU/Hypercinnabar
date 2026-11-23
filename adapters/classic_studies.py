"""Reference candidates using only the observations, forcing and endpoint ages in each request."""
import numpy as np
from scipy.signal import find_peaks, periodogram

TASK_IDS = {"hays76-simplex", "rossello-precession", "odp846-published-clock",
            "newark-long-eccentricity", "xiamaling-precession", "walvis1262-precession"}
METHOD_DETAILS = {
    "hays76-simplex": "Mean at repeated depths; SIMPLEX age interpolation; linear detrend, Hann spectrum and 16x padding.",
    "rossello-precession": "Ordered La2004 summer-insolation maxima with the published 3 kyr lag and fixed terminal ages; minimize squared fractional deviations from endpoint-derived interval durations.",
    "odp846-published-clock": "Linear interpolation between the two terminal ages; the isotope measurements and forcing are unused in this comparator.",
    "newark-long-eccentricity": "Linear detrend and Hann depth-rank periodogram, 4x padding; ratio of long and carrier wavelengths scaled to 404 ka.",
}
JOINT_SCAN = ("101 sedimentation rates by 121 axial precession frequencies; equal log-power "
              "weights within each band family, fixed present-day g frequencies, sidereal "
              "length of day from the alodfromk conversion; point estimates only.")


def load(folder, stem):
    return np.loadtxt(folder / (stem + ".csv"), delimiter=",", skiprows=1, ndmin=2)


def mean_at_coordinates(x, y):
    unique, index = np.unique(x, return_inverse=True)
    return unique, np.bincount(index, weights=y)/np.bincount(index)


def band_wavelength(f, power, bounds):
    peaks = find_peaks(power)[0]
    select = peaks[(f[peaks] >= 1/bounds[1]) & (f[peaks] <= 1/bounds[0])]
    if not len(select):
        raise ValueError(f"No local spectral peak at wavelengths in {bounds}")
    return 1/f[select[np.argmax(power[select])]]


def hays_simplex(folder, p):
    out = {}
    for core in ("rc11", "e49"):
        depth, values = mean_at_coordinates(*load(folder, core).T)
        anchors = np.asarray(p["ties_depth_m_age_ka"][core])
        slope = np.diff(anchors[:, 1])[0]/np.diff(anchors[:, 0])[0]
        age = anchors[0, 1] + slope*(depth-anchors[0, 0])
        start, step, count = p["time_grid"][core]
        grid = start + step*np.arange(count)
        values = np.interp(grid, age, values)
        f, power = periodogram(values, fs=1/step, window="hann", detrend="linear", nfft=16*count)
        for name, bounds in p["period_search_ka"].items():
            out[f"{core}_{name}_ka"] = band_wavelength(f, power, bounds)
    return out


def rossello_ages(folder, levels, anchors, lag_ka):
    time, insolation = load(folder, "insolation").T
    peaks = time[find_peaks(insolation, distance=10)[0]] - lag_ka
    young, old = anchors[:, 1]
    pool = np.r_[young, peaks[(peaks>young) & (peaks<old)], old]
    if len(pool) < len(levels):
        raise ValueError("Too few insolation maxima for ordered horizon assignment")
    # Match ordered levels to orbit extrema. Missing sedimentary cycles may skip peaks.
    # Weight each interval by its constant-rate predicted duration.
    expected = np.diff(levels)*(old-young)/(levels[-1]-levels[0])
    elapsed = pool[None, :] - pool[:, None]
    previous = np.full(len(pool), np.inf)
    previous[0] = 0.
    back = np.empty((len(levels)-1, len(pool)), dtype=int)
    for i, duration in enumerate(expected):
        cost = previous[:, None] + ((elapsed-duration)/duration)**2
        cost[elapsed <= 0] = np.inf
        back[i] = cost.argmin(axis=0)
        previous = cost.min(axis=0)
    if not np.isfinite(previous[-1]):
        raise ValueError("No monotone orbital assignment through the supplied anchors")
    indices = [len(pool)-1]
    for row in back[::-1]:
        indices.append(row[indices[-1]])
    return pool[indices[::-1]]


def terrestrial_estimates(folder, p):
    depth, signal = mean_at_coordinates(*load(folder, "data").T)
    step = p["interpolation_step_m"]
    grid = depth[0] + step*np.arange(int((depth[-1]-depth[0])/step)+1)
    f, power = periodogram(np.interp(grid, depth, signal), fs=1/step, window="hann",
                           detrend="linear", nfft=4*len(grid))
    # A simple fixed-g spectral scan. The priors in TimeOptB differ from this approximation.
    g1, g2, g3, g4, g5 = (5.59, 7.456, 17.368, 17.916, 4.257)
    eccentricity = np.array([g2-g5, g4-g5, g3-g5, g4-g2, g3-g2])
    rates = np.linspace(*p["rate_search_cm_per_ka"], 101)
    precession = np.linspace(*p["precession_search_arcsec_yr"], 121)
    # One revolution equals 1,296,000 arcseconds. Frequencies below are in cycles/m.
    scale = 100/(1296*rates)
    log_power = np.log(np.maximum(power, np.finfo(float).tiny))
    ecc = np.interp(eccentricity[:, None]*scale, f, log_power).mean(axis=0)
    pre_freq = precession[:, None] + np.array([g2, g5, g3, g4])
    pre = np.interp(pre_freq[:, :, None]*scale, f, log_power).mean(axis=1)
    ki, ri = np.unravel_index(np.argmax(pre + ecc), pre.shape)
    k = precession[ki]
    # The dimensionless lunar-distance fit and spin conversion used by astrochron::alodfromk.
    a = np.polyval([.00621404, -.00060922, -.217194, 1.], np.log(k/50.475838))
    sidereal_today = 2*np.pi/(7.292115e-5*3600)
    return dict(rate_cm_per_ka=rates[ri], precession_arcsec_yr=k,
                lod_h=sidereal_today/(1+4.81*(1-np.sqrt(a))), rate_ci95=None, precession_ci95=None)


def evaluate(name, folder, output, p):
    if name == "hays76-simplex":
        return hays_simplex(folder, p)
    if name in ("xiamaling-precession", "walvis1262-precession"):
        return terrestrial_estimates(folder, p)
    if name == "newark-long-eccentricity":
        x, y = load(folder, "data").T
        spacing = np.median(np.diff(x))
        f, power = periodogram(y, fs=1/spacing, window="hann", detrend="linear", nfft=4*len(x))
        anchor = band_wavelength(f, power, p["anchor_wavelength_native"])
        long_band = anchor*np.asarray(p["modulation_ratio_search"])
        long_wave = band_wavelength(f, power, long_band)
        return {"modulation_ka": p["calibration_ka"]*long_wave/anchor}
    if name in ("rossello-precession", "odp846-published-clock"):
        queries = load(folder, "queries")
        anchors = load(folder, "anchors")
        if name == "rossello-precession":
            times = rossello_ages(folder, queries[:, 1], anchors, p["reported_lag_ka"])
        else:
            times = np.interp(queries[:, 1], anchors[:, 0], anchors[:, 1])
        np.savetxt(output / "prediction.csv", np.column_stack((queries, times)), delimiter=",",
                   header="segment,coordinate_m,time_ka", comments="", fmt="%.17g")
        return None
    raise ValueError(f"No classical study candidate for {name}")
