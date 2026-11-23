from __future__ import annotations

import unittest

import pandas as pd

from astrochron_warp import AstrochronWarp


class FakeBackend:
    astrochron_version = "1.8-test"

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def call(self, function: str, /, **kwargs: object) -> pd.DataFrame:
        self.calls.append((function, kwargs))
        if function == "sedrate2time":
            return pd.DataFrame([[0.0, 0.0], [1.0, 50.0]])
        return pd.DataFrame([[100.0, 1.0], [110.0, 2.0]])


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.backend = FakeBackend()
        self.client = AstrochronWarp(self.backend)

    def test_tune_sorts_inputs_and_disables_r_plots(self) -> None:
        result = self.client.tune(
            [[2, 2], [0, 1]],
            [[2, 120], [0, 100]],
            extrapolate=True,
        )

        function, kwargs = self.backend.calls[-1]
        self.assertEqual(function, "tune")
        self.assertEqual(list(kwargs["dat"]["depth"]), [0.0, 2.0])
        self.assertEqual(list(kwargs["controlPts"]["time"]), [100.0, 120.0])
        self.assertFalse(kwargs["genplot"])
        self.assertFalse(kwargs["verbose"])
        self.assertEqual(list(result.data.columns), ["time", "value"])
        self.assertEqual(result.astrochron_version, "1.8-test")

    def test_tune_rejects_folded_control_map(self) -> None:
        with self.assertRaisesRegex(ValueError, "strictly monotonic"):
            self.client.tune(
                [[0, 1], [1, 2], [2, 3]],
                [[0, 100], [1, 90], [2, 110]],
            )

    def test_tune_accepts_decreasing_time(self) -> None:
        self.client.tune(
            [[0, 1], [1, 2], [2, 3]],
            [[0, 120], [1, 110], [2, 100]],
        )
        _, kwargs = self.backend.calls[-1]
        self.assertEqual(list(kwargs["controlPts"]["time"]), [120.0, 110.0, 100.0])

    def test_constant_sedrate_rejects_nonpositive_rate(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            self.client.constant_sedrate([[0, 1], [1, 2]], 0)

    def test_sedrate_to_time_uses_documented_units(self) -> None:
        result = self.client.sedrate_to_time([[1, 2], [0, 2]])
        function, kwargs = self.backend.calls[-1]
        self.assertEqual(function, "sedrate2time")
        self.assertEqual(list(kwargs["sedrates"].columns), ["depth_m", "rate_cm_per_ka"])
        self.assertEqual(list(result.data.columns), ["depth_m", "time_ka"])


if __name__ == "__main__":
    unittest.main()


