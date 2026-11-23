from __future__ import annotations

import unittest
from unittest.mock import patch

import pandas as pd

from astrochron_rpy2.pandas_bridge import (
    as_pandas_frame,
    call_frame,
    call_with_pandas,
)


class _Context:
    def __init__(self, owner) -> None:
        self.owner = owner

    def __enter__(self):
        self.owner.entered += 1

    def __exit__(self, exc_type, exc, traceback):
        self.owner.exited += 1


class _Converter:
    def __init__(self) -> None:
        self.entered = 0
        self.exited = 0

    def context(self):
        return _Context(self)


class PandasBridgeTests(unittest.TestCase):
    def test_call_with_pandas_scopes_converter(self) -> None:
        converter = _Converter()
        function = lambda value: value + 1
        with patch(
            "astrochron_rpy2.pandas_bridge._conversion_runtime",
            return_value=(object(), converter),
        ):
            self.assertEqual(call_with_pandas(function, 4), 5)
        self.assertEqual((converter.entered, converter.exited), (1, 1))

    def test_call_frame_does_not_round_trip_existing_dataframe(self) -> None:
        converter = _Converter()
        original = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        with patch(
            "astrochron_rpy2.pandas_bridge._conversion_runtime",
            return_value=(object(), converter),
        ):
            result = call_frame(lambda: original, columns=("x", "y"))
        self.assertEqual(list(result.columns), ["x", "y"])
        self.assertEqual(list(original.columns), ["a", "b"])

    def test_as_pandas_frame_accepts_dataframe_without_rpy2(self) -> None:
        original = pd.DataFrame({"a": [1], "b": [2]}, index=[10])
        result = as_pandas_frame(original, columns=("x", "y"))
        self.assertEqual(list(result.columns), ["x", "y"])
        self.assertEqual(list(result.index), [0])
        self.assertEqual(list(original.columns), ["a", "b"])


if __name__ == "__main__":
    unittest.main()

