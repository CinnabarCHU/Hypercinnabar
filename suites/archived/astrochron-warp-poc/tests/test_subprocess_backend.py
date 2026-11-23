from __future__ import annotations

import sys
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from astrochron_warp import (
    AstrochronCancelledError,
    AstrochronTimeoutError,
    SubprocessBackend,
    WarpExecutor,
)


class SubprocessBackendTests(unittest.TestCase):
    def make_backend(self, *, timeout: float | None = 2.0) -> SubprocessBackend:
        worker = Path(__file__).with_name("fake_worker.py")
        return SubprocessBackend(
            timeout=timeout,
            worker_command=(sys.executable, worker),
        )

    def test_probe_does_not_load_r_in_parent(self) -> None:
        backend = self.make_backend()
        status = backend.probe()
        self.assertTrue(status.available)
        self.assertEqual(status.astrochron_version, "1.8-fake")
        self.assertEqual(backend.rpy2_version, "3.6-fake")

    def test_dataframe_round_trip(self) -> None:
        backend = self.make_backend()
        source = pd.DataFrame({"depth": [0.0, 1.0], "value": [2.0, 3.0]})
        output = backend.call("tune", dat=source, genplot=False)
        self.assertEqual(list(output.columns), ["depth", "value"])
        self.assertEqual(list(output["depth"]), [100.0, 101.0])
        self.assertEqual(backend.astrochron_version, "1.8-fake")

    def test_timeout_kills_worker(self) -> None:
        backend = self.make_backend(timeout=0.05)
        with self.assertRaises(AstrochronTimeoutError):
            backend.call("slow", dat=pd.DataFrame([[0.0, 1.0], [1.0, 2.0]]))
        self.assertFalse(backend.has_active_process)

    def test_cancel_terminates_running_worker(self) -> None:
        backend = self.make_backend(timeout=None)
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                backend.call,
                "slow",
                dat=pd.DataFrame([[0.0, 1.0], [1.0, 2.0]]),
            )
            deadline = time.monotonic() + 2
            while not backend.has_active_process and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(backend.cancel_current())
            with self.assertRaises(AstrochronCancelledError):
                future.result(timeout=2)
        self.assertFalse(backend.has_active_process)

    def test_executor_returns_immediately_and_preserves_domain_api(self) -> None:
        backend = self.make_backend()
        executor = WarpExecutor(backend=backend)
        self.addCleanup(executor.close)
        start = time.monotonic()
        job = executor.submit_tune(
            [[0.0, 1.0], [1.0, 2.0]],
            [[0.0, 100.0], [1.0, 110.0]],
        )
        submit_elapsed = time.monotonic() - start
        self.assertLess(submit_elapsed, 0.1)
        self.assertFalse(job.done())
        result = job.result(timeout=3)
        self.assertEqual(list(result.data["time"]), [100.0, 101.0])
        self.assertEqual(result.astrochron_version, "1.8-fake")


if __name__ == "__main__":
    unittest.main()
