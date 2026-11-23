# Acycle User Guide case-study acceptance

This suite runs all three complete **Chapter 6** case studies in the Acycle v2.8 User Guide (2025-07-18) against the migrated menu interfaces. It does not claim to test every illustrative operation in Chapters 3–5, the visual desktop GUI, or autonomous DeepSeek planning.

Each `helper`, `analyzer`, `plotter`, and replay request goes through the production `acycle_harness_menu` MATLAB bridge. Its request JSON, response JSON, journal, native MAT references, and exported figures remain in the artifact. The driver reads the native return values to connect steps; it does not reimplement scientific methods. This is a deterministic acceptance driver, **not an LLM transcript or a test of the Python/Node tool orchestration**.

```matlab
addpath('tests/user_guide');
r = run_user_guide(pwd, fullfile(pwd,'guide-results','wayao'), 'wayao');
assert(r.execution_ok);
assert(r.criteria_ok);
```

Replace `wayao` with `insolation` or `etp`. MATLAB R2024b CI includes Signal Processing, Statistics and Machine Learning, and Curve Fitting toolboxes. Run `python tests/user_guide/verify_fixtures.py` to validate the pinned inputs before execution. No API key is used by this suite.

| Case | Printed guide pages | Pipeline |
| --- | --- | --- |
| Insolation | 108–111 | Sort, remove mean, 2π MTM with explicit NFFT=2001, evolutionary FFT (400 kyr window, 3.2 kyr step) |
| La2004 ETP | 112–117 | Sort, remove mean, same MTM, evolutionary FFT, Morlet wavelet (Torrence–Compo; 10–700 kyr display) |
| Wayao Carnian GR | 118–131 | Sort/unique, sampling intervals, 0.33 m interpolation, 80 m LOWESS, 2π MTM/robust AR(1), 40 m evolutionary FFT, Gaussian 0.022–0.034 cycles/m, 405 kyr peak age model, tune the original data, COCO (1000 simulations), eCOCO (45 m window; 500 simulations) |

The chronological order of independent diagnostic panels may differ from the manual. Filtering/tuning runs before the more expensive COCO checks; neither takes its parameters from COCO. The source spectrum, target age, rate grid, and random seed are fixed before execution. The master MTM implementation is also evaluated on the same prepared series with explicit options.

`manifest.json` records input SHA-256 hashes, source revisions, acceptance criteria, and discrepancies between prose, screenshots, and callbacks. `report.json` separates actual execution and scientific criteria. A plot error does not stop the remaining calculations, but does fail execution acceptance. A failed scientific claim stays failed; the runner does not tune settings to make it pass. A finite evolutionary/wavelet matrix alone is not proof of the guide's qualitative interpretation.

Two specific caveats matter when interpreting output:

- The example ETP file numerically matches `z(E) + 0.5 z(T) - z(P)` (maximum difference below 5e-9 using the bundled La04 data and sample standard deviations). The guide's prose omits the 0.5. Inputs are retained unchanged.
- The GUIDE spectrum callback leaves `padtimes` unassigned when the explicit NFFT field is selected. The portable wrapper can receive both arguments: this suite selects its explicit-NFFT branch and passes NFFT=2001. It tests the documented numerical settings, not that faulty GUI callback.

The full age model returned by the historical BuildAgeModel code also contains a suspect endpoint extrapolation (multiplying a depth difference by a sedimentation rate). The diagnostic report compares those endpoints with linear extrapolation. The actual tuning uses the saved peak tiepoints, as the guide instructs, through the original `depthtotime` function. No scientific kernel is silently corrected here.

The first real run found that literal NFFT=2001 does not reproduce the stated 22.4 kyr insolation peak. A separately labelled 5× padding diagnostic tests the grid visible in the guide's plotted frequency labels (e.g. 422/10005 ≈ 0.0421789). Both results and the original failed criterion are retained.

The initial Rayleigh-only peak check falsely rejected the Wayao ~1.8 m claim at 1.82045 m, which rounds to the guide's value. The final check reports both the Rayleigh-bin comparison and agreement at printed precision, accepting either. This rule does not remove the literal-NFFT insolation/ETP discrepancies. Initial run results remain part of the audit trail.

The original `ecocoplot` also reads `main_unit_selection` from the GUI's base workspace. Its migrated legacy plotter now calls `code/method/acLegacyEcocoPlot.m`, which preserves the original drawing code and supplies a local English display context. The pinned upstream function and all numerical COCO/eCOCO calculations remain unchanged.
