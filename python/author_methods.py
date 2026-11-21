"""Numerical routines from eccentricity_final.py and wavelet_pipeline.py in the supplied code archive."""
import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks
DTI=5.0
WIN_MA=(38.0,67.0)
W0=6.0
S0_FAC=8
DS=.0625
NS=50
FF=4*np.pi/(6+np.sqrt(38))
CO=FF/np.sqrt(2)
ARC_LO,ARC_HI=62.0,85.0
ARC_RATIO=1.38
SMOOTH_TIME=120


def bandpass(x, dt, tlo, thi):
    """FFT 矩形带通，保留周期 tlo~thi，零均值输出。"""
    n = len(x)
    X = np.fft.rfft(x - x.mean())
    f = np.fft.rfftfreq(n, d=dt)
    g = np.zeros_like(f)
    g[(f >= 1.0 / thi) & (f <= 1.0 / tlo)] = 1.0
    return np.fft.irfft(X * g, n=n)

def prepare_cwt(t, h):
    ti = np.arange(t[0], t[-1] + DTI, DTI)
    hi = np.interp(ti, t, h)
    m = (ti >= WIN_MA[0] * 1e3) & (ti <= WIN_MA[1] * 1e3)
    tw, y = ti[m], hi[m]
    dt = tw[1] - tw[0]
    y = (y - y.mean()) / y.std()
    y = y - y.mean()

    s0 = S0_FAC * dt
    scales = s0 * 2 ** (DS * np.arange(NS))
    N = len(y)
    Xf = np.fft.fft(y)
    omega = 2 * np.pi * np.fft.fftfreq(N, dt)
    norm = np.sqrt(2) * np.pi ** 0.25
    cfs = np.zeros((NS, N), dtype=complex)
    for i, s in enumerate(scales):
        psi = norm * np.exp(-(s * omega - W0) ** 2 / 2)
        psi[omega < 0] = 0
        cfs[i] = dt * np.fft.ifft(Xf * np.conj(psi))

    # COI
    half_up = np.arange(1, (N + 1) // 2)
    half_dn = np.arange(1, N // 2)
    coi_seq = np.concatenate([[1e-5], half_up, half_dn[::-1], [1e-5]])[:N]
    coi = CO * dt * coi_seq
    periods = FF * scales
    return tw, scales, cfs, periods, coi

def black_arc(tw, periods, cfs):
    """
    返回分段弧列表，每段为 (age 数组, period 数组)。
    每段弧的两个端点落在相邻两个红色斑点中心（波腹），弧顶在中间波节。
    波腹由平滑带内总功率 find_peaks 数值定位；弧顶周期取波节处峰值；
    弧振幅随弧长（波腹间距）变化：ARC_RATIO × 弧长；用余弦弧连接。
    """
    power = np.abs(cfs) ** 2
    logp = np.log2(periods)
    band = (periods >= ARC_LO) & (periods <= ARC_HI)
    bidx = np.where(band)[0]
    pw_s = uniform_filter1d(power[bidx, :], size=SMOOTH_TIME, axis=1)

    tot = pw_s.sum(axis=0)
    peaks, _ = find_peaks(tot, distance=200, prominence=tot.std() * 0.3)

    def sub_peak(n):
        sub = pw_s[:, n]
        jg = bidx[sub.argmax()]
        return periods[jg]

    age = tw * 1e-3
    segments = []
    for i in range(len(peaks) - 1):
        pL, pR = peaks[i], peaks[i + 1]
        node = (pL + pR) // 2                 # 波节
        ptop = sub_peak(node)                 # 弧顶（小周期）
        aL, aR = age[pL], age[pR]
        amp = ARC_RATIO * (aR - aL)           # 振幅随弧长
        pend = ptop + amp                     # 端点（大周期）
        aa = np.linspace(aL, aR, 80)
        u = np.clip((aa - age[node]) / max(age[node] - aL, aR - age[node]), -1, 1)
        pp = ptop + (pend - ptop) * (1 - np.cos(np.pi * u)) / 2
        segments.append((aa, pp))
    return segments
