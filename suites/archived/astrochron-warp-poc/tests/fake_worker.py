"""R-free worker used to test the subprocess protocol."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from astrochron_warp._protocol import decode_value, encode_value


def main() -> int:
    request_path = Path(sys.argv[1])
    response_path = Path(sys.argv[2])
    request = json.loads(request_path.read_text(encoding="utf-8"))
    if request["action"] == "probe":
        response = {
            "ok": True,
            "astrochron_version": "1.8-fake",
            "rpy2_version": "3.6-fake",
        }
    else:
        function = request["function"]
        kwargs = decode_value(request["kwargs"])
        if function == "slow":
            time.sleep(10)
        if function == "tune":
            time.sleep(0.15)
            result = kwargs["dat"].copy()
            result.iloc[:, 0] = result.iloc[:, 0] + 100.0
        else:
            result = kwargs.get("dat")
            if result is None:
                result = kwargs.get("sedrates")
        response = {
            "ok": True,
            "astrochron_version": "1.8-fake",
            "rpy2_version": "3.6-fake",
            "result": encode_value(result),
        }
    response_path.write_text(json.dumps(response), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
