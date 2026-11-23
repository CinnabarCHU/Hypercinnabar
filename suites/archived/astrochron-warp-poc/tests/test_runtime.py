from __future__ import annotations

import unittest

from astrochron_warp import AstrochronWarp, RuntimeStatus, SubprocessBackend, runtime_status


class RuntimeTests(unittest.TestCase):
    def test_domain_client_is_process_isolated_by_default(self) -> None:
        self.assertIsInstance(AstrochronWarp().backend, SubprocessBackend)

    def test_probe_never_raises_for_an_optional_runtime(self) -> None:
        status = runtime_status()
        self.assertIsInstance(status, RuntimeStatus)
        if status.available:
            self.assertIsNotNone(status.astrochron_version)
        else:
            self.assertTrue(status.error)


if __name__ == "__main__":
    unittest.main()

