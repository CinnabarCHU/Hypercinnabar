from __future__ import annotations

import os
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from astrochron_rpy2 import astrochron, call_frame, package_version


@unittest.skipUnless(
    os.environ.get("ASTROCHRON_RPY2_RUN_R_TESTS") == "1",
    "set ASTROCHRON_RPY2_RUN_R_TESTS=1 after installing R, rpy2, and Astrochron",
)
class RIntegrationTests(unittest.TestCase):
    def test_raw_tune_with_pandas_bridge(self) -> None:
        result = call_frame(
            astrochron.tune,
            pd.DataFrame({"depth": [0, 1, 2, 3], "value": [10, 20, 30, 40]}),
            controlPts=pd.DataFrame({"depth": [0, 1, 3], "time": [100, 110, 150]}),
            extrapolate=True,
            genplot=False,
            check=True,
            verbose=False,
            columns=("time", "value"),
        )
        expected = pd.DataFrame(
            {"time": [100.0, 110.0, 130.0, 150.0], "value": [10, 20, 30, 40]}
        )
        assert_frame_equal(result, expected, check_dtype=False)
        self.assertTrue(package_version())


if __name__ == "__main__":
    unittest.main()

