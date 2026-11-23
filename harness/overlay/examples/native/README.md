# Native request examples

These requests are schema-checked examples, **not executed MATLAB validation**.
All numerical choices are illustrative, not scientific recommendations.
Provide your own data and choose units, sampling intervals, windows, search
ranges, noise settings and priors for your study. In particular the wavelet
example explicitly assumes dt=1; it does not infer spacing. The changepoint
example's prior values are placeholders to replace, not calibrated defaults.
The bispectral example sets SignificanceMethod=none and makes no significance claim.

Each file is the argument object for `acycle_native`. Use Harness or MCP, or:

```sh
acycle-deepseek --workspace /path/to/study call acycle_native \
  --arguments-file /path/to/bandpass.json
```

For direct functions not shown here, discover their exact source signature and
help via `acycle_catalog`. The GUI inspection example launches only the original
main window and records its controls; it does not prove any GUI analysis route
works unattended. Native GUI constructors can require a local graphics service.
