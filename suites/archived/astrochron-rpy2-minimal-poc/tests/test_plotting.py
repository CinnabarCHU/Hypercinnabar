from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from astrochron_rpy2.plotting import plot_frame, r_file_device


class _FakeDevices:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []
        self.open_ids: set[int] = set()

    def png(self, *args, **kwargs) -> None:
        self.calls.append(("png", args, kwargs))
        self.open_ids.add(2)

    def pdf(self, *args, **kwargs) -> None:
        self.calls.append(("pdf", args, kwargs))
        self.open_ids.add(2)

    def dev_cur(self) -> list[int]:
        return [2]

    def dev_list(self) -> list[int]:
        return list(self.open_ids)

    def dev_off(self, *, which: int) -> None:
        self.calls.append(("dev_off", (), {"which": which}))
        self.open_ids.remove(which)


class _FakeAxis:
    def __init__(self) -> None:
        self.xlabel = None
        self.ylabel = None
        self.plotted = None

    def plot(self, x, y, **kwargs):
        self.plotted = (list(x), list(y), kwargs)
        return ["line"]

    def set_xlabel(self, value):
        self.xlabel = value

    def set_ylabel(self, value):
        self.ylabel = value


class PlottingTests(unittest.TestCase):
    def test_raster_device_uses_physical_size_and_dpi(self) -> None:
        devices = _FakeDevices()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plot.png"
            with patch("astrochron_rpy2.plotting._grdevices", return_value=devices):
                with r_file_device(path, width_in=9, height_in=4, dpi=600):
                    self.assertIn(2, devices.open_ids)
        name, args, kwargs = devices.calls[0]
        self.assertEqual(name, "png")
        self.assertEqual(args[0], str(path))
        self.assertEqual(kwargs["width"], 9)
        self.assertEqual(kwargs["height"], 4)
        self.assertEqual(kwargs["units"], "in")
        self.assertEqual(kwargs["res"], 600)
        self.assertEqual(devices.calls[-1], ("dev_off", (), {"which": 2}))

    def test_device_is_closed_after_body_error(self) -> None:
        devices = _FakeDevices()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plot.pdf"
            with patch("astrochron_rpy2.plotting._grdevices", return_value=devices):
                with self.assertRaisesRegex(RuntimeError, "boom"):
                    with r_file_device(path):
                        raise RuntimeError("boom")
        self.assertFalse(devices.open_ids)

    def test_plot_frame_uses_existing_axis(self) -> None:
        frame = pd.DataFrame({"time": [0, 1], "value": [4, 5]})
        axis = _FakeAxis()
        line = plot_frame(frame, axis, x="time", y="value", color="black")
        self.assertEqual(line, "line")
        self.assertEqual(axis.plotted, ([0, 1], [4, 5], {"color": "black"}))
        self.assertEqual(axis.xlabel, "time")
        self.assertEqual(axis.ylabel, "value")


if __name__ == "__main__":
    unittest.main()

