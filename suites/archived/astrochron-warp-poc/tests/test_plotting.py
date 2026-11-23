from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from astrochron_warp import WarpResult, draw_age_model, draw_warp, export_warp_plot

try:
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
except Exception:  # pragma: no cover - optional dependency
    Figure = None


@unittest.skipIf(Figure is None, "install the plotting extra to run plot tests")
class PlottingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = pd.DataFrame({"depth": [0.0, 1.0, 2.0], "value": [1.0, 0.0, 1.0]})
        self.result = WarpResult(
            data=pd.DataFrame({"time": [100.0, 110.0, 125.0], "value": [1.0, 0.0, 1.0]}),
            function="astrochron::tune",
            astrochron_version="1.8-test",
        )
        self.controls = pd.DataFrame({"depth": [0.0, 2.0], "time": [100.0, 125.0]})

    def test_drawers_use_caller_owned_axes(self) -> None:
        figure = Figure(figsize=(8, 3))
        FigureCanvasAgg(figure)
        axes = figure.subplots(1, 3)
        graphics = draw_warp(axes[:2], self.source, self.result)
        model = draw_age_model(axes[2], self.controls)
        self.assertIs(graphics["source_axes"], axes[0])
        self.assertIs(graphics["warped_axes"], axes[1])
        self.assertIs(model["axes"], axes[2])

    def test_export_controls_size_resolution_and_format(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "warp.png"
            exported = export_warp_plot(
                self.source,
                self.result,
                output,
                control_points=self.controls,
                width_in=7.5,
                height_in=3.25,
                dpi=180,
            )
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 1000)
            self.assertEqual(exported.width_in, 7.5)
            self.assertEqual(exported.height_in, 3.25)
            self.assertEqual(exported.dpi, 180.0)
            self.assertEqual(exported.format, "png")


if __name__ == "__main__":
    unittest.main()
