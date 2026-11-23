from __future__ import annotations

import os
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from astrochron_warp import AstrochronWarp


@unittest.skipUnless(
    os.environ.get("ASTROCHRON_WARP_RUN_R_TESTS") == "1",
    "set ASTROCHRON_WARP_RUN_R_TESTS=1 after installing R, rpy2, and Astrochron",
)
class RIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = AstrochronWarp()

    def test_piecewise_linear_tune_matches_known_map(self) -> None:
        result = self.client.tune(
            [[0, 10], [1, 20], [2, 30], [3, 40]],
            [[0, 100], [1, 110], [3, 150]],
            extrapolate=True,
        )
        expected = pd.DataFrame(
            {"time": [100.0, 110.0, 130.0, 150.0], "value": [10.0, 20.0, 30.0, 40.0]}
        )
        assert_frame_equal(result.data, expected, check_dtype=False)

    def test_constant_sedrate_matches_known_map(self) -> None:
        result = self.client.constant_sedrate(
            [[0.0, 1], [0.1, 2], [0.2, 3]],
            0.01,
            begin=5,
        )
        expected = pd.DataFrame(
            {"time": [5.0, 15.0, 25.0], "value": [1.0, 2.0, 3.0]}
        )
        assert_frame_equal(result.data, expected, check_dtype=False)

    def test_sedrate_curve_integrates_to_time(self) -> None:
        result = self.client.sedrate_to_time([[0, 2], [1, 2], [2, 2]])
        expected = pd.DataFrame(
            {"depth_m": [0.0, 1.0, 2.0], "time_ka": [0.0, 50.0, 100.0]}
        )
        assert_frame_equal(result.data, expected, check_dtype=False)


if __name__ == "__main__":
    unittest.main()


