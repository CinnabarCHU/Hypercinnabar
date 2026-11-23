"""Numerical fixtures and the open synthetic controls."""
from __future__ import annotations

import numpy as np
from scipy.io import loadmat

from records import ROOT, record_array


def case_tables(case):
    fixture = case["fixture"]
    if "table" in fixture:
        table = np.loadtxt(ROOT / fixture["table"], delimiter=",", skiprows=1, ndmin=2)
        return table[:, fixture["input_indices"]], table[:, fixture["output_indices"]]
    if "mat" not in fixture:
        return np.asarray(fixture["data"]), np.asarray(fixture["expected"])
    data = loadmat(ROOT / fixture["mat"], variable_names=["raw", "dat", "y", "t", "sp", "g"])
    op = case["operation"]
    if op == "linear":
        return data["raw"], data["dat"]
    inputs = np.column_stack((data["t"], data["y"]))
    if op == "gaussian":
        return inputs, np.column_stack((data["t"], data["g"]))
    return inputs, data["sp"]


def lr04_data():
    series = record_array("lr04")
    age = series[:, 0]
    block = ((age >= 1760) & (age <= 1780)) | ((age >= 2090) & (age <= 2120))
    isolated = np.arange(len(age)) % 13 == 5
    # Leave a measured sample on each side of a block and in front of both endpoints.
    isolated &= ((age < 1754) | (age > 1786)) & ((age < 2084) | (age > 2126))
    isolated[[0, -1]] = False
    hidden = isolated | block
    return series[~hidden], series[hidden], block[hidden]


def rate_section():
    rng = np.random.Generator(np.random.PCG64(9017))
    depth = .05 * np.arange(2000)
    time = np.minimum(depth, 40.) / .04 + np.maximum(depth - 40., 0.) / .06
    value = sum(a * np.sin(2 * np.pi * time / p + phi)
                for p, a, phi in [(23, .8, .4), (41, .9, 1.1), (100, .65, -.7)])
    value += ar_noise(rng, len(time), .65) * .42
    return np.column_stack((depth, value))


def ar_noise(rng, n, rho):
    noise = rng.standard_normal(n)
    scale = np.sqrt(1 - rho * rho)
    for j in range(1, n):
        noise[j] = rho * noise[j-1] + scale * noise[j]
    return noise


def detection_panel():
    rng = np.random.Generator(np.random.PCG64(39417))
    labels = rng.permutation(np.repeat([0, 1], 20))
    time = np.arange(256)
    series = []
    for index, label in enumerate(labels):
        noise = ar_noise(rng, len(time), .62)
        phase = rng.uniform(0, 2*np.pi, size=2)
        waves = .95*np.sin(2*np.pi*time/23 + phase[0]) + .65*np.cos(2*np.pi*time/41 + phase[1])
        series.append(np.column_stack((np.full_like(time, index), time, noise+label*waves)))
    return np.vstack(series), labels
