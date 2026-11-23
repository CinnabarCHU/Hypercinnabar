from __future__ import annotations

import unittest
from unittest.mock import patch

from astrochron_rpy2 import astrochron
from astrochron_rpy2.raw import get_function


class _FakePackage:
    tune = object()


class RawProxyTests(unittest.TestCase):
    def test_repr_does_not_load_r(self) -> None:
        with patch("astrochron_rpy2.raw.get_astrochron") as loader:
            self.assertIn("lazy rpy2 proxy", repr(astrochron))
            loader.assert_not_called()

    def test_proxy_forwards_attributes_without_wrapping_function(self) -> None:
        package = _FakePackage()
        with patch("astrochron_rpy2.raw.get_astrochron", return_value=package):
            self.assertIs(astrochron.tune, package.tune)

    def test_get_function_forwards_name(self) -> None:
        package = _FakePackage()
        with patch("astrochron_rpy2.raw.get_astrochron", return_value=package):
            self.assertIs(get_function("tune"), package.tune)

    def test_get_function_rejects_empty_name(self) -> None:
        with self.assertRaises(ValueError):
            get_function("")


if __name__ == "__main__":
    unittest.main()

