"""Exercise test-only, native widget callbacks in the actual shared MATLAB."""
import sys

import matlab.engine

eng = matlab.engine.connect_matlab("AcycleDesktopTest")
try:
    assert eng.feval("gui_human_fixture", sys.argv[1]) == "ok"
finally:
    eng.quit()
