"""Independent candidate implementations for deterministic forward models."""
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import hilbert, lfilter

OPERATIONS = {"cip_accumulation", "segmented_clock", "rate_step_proxy", "weak_band",
              "hilbert_envelope", "imbrie_continuous", "imbrie_euler"}


def evaluate(op, data, p, controls=None):
    if op == "cip_accumulation":
        time = data[:, 0]
        rate = p["mean_cm_per_ka"] + p["amplitude_cm_per_ka"] * np.sin(2*np.pi*time / p["period_ka"])
        height = p["initial_height_m"] + np.r_[0., np.cumsum(np.diff(time)*rate[1:]/100)]
        return np.column_stack((time, height, rate))
    if op == "segmented_clock":
        segment, depth = data.T
        age = np.empty_like(depth)
        for number in np.unique(segment):
            selected = segment == number
            nodes = controls[controls[:, 0] == number]
            age[selected] = np.interp(depth[selected], nodes[:, 1], nodes[:, 2])
        return np.column_stack((segment, depth, age))
    if op == "rate_step_proxy":
        depth, innovations = data.T
        offset = np.maximum(depth-p["break_m"], 0.)
        first, second = p["rates_cm_per_ka"]
        age = (depth-offset)*100/first + offset*100/second
        clean = sum(amplitude*np.sin(2*np.pi*age/period + phase)
                    for period, amplitude, phase in p["harmonics"])
        rho = p["ar1_rho"]
        excitation = innovations*np.sqrt(1-rho**2)
        excitation[0] = innovations[0]
        noise = lfilter([1.], [1., -rho], excitation)
        return np.column_stack((depth, age, clean, clean+p["noise_scale"]*noise))
    if op == "weak_band":
        depth = data[:, 0]
        cycle = interp1d(*controls.T, bounds_error=False, fill_value="extrapolate")(depth)
        distance = (cycle-p["cycle_center"])/p["envelope_sigma_cycles"]
        amplitude = 1-p["attenuation"]*np.exp(-.5*distance**2)
        return np.column_stack((depth, amplitude*np.cos(2*np.pi*cycle)))
    if op == "hilbert_envelope":
        return np.column_stack((data[:, 0], np.abs(hilbert(data[:, 1]))))
    if op in ("imbrie_continuous", "imbrie_euler"):
        age, insolation = data.T
        order = np.argsort(-age)
        target = insolation.mean()-insolation[order]
        ice = np.empty(len(age))
        ice[0] = p["initial"]
        for i, dt in enumerate(-np.diff(age[order])):
            gap = target[i]-ice[i]
            rate = (1-p["b"] if gap > 0 else 1+p["b"])/p["tm_ka"]
            fraction = -np.expm1(-dt*rate) if op == "imbrie_continuous" else dt*rate
            ice[i+1] = ice[i]+fraction*gap
        return np.column_stack((age, ice[np.argsort(order)]))
    raise ValueError(f"Unknown forward model {op}")
