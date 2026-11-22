# Acycle GUIDE method migration

The numerical and desktop reference is the last GUIDE-era Acycle revision, [mingsongli/acycle at b52ea9f](https://github.com/mingsongli/acycle/tree/b52ea9f510f3be00bde9a0238b9898a1e2315b74). The submodule `upstream/acycle` fixes the original MATLAB files, figures, data and authorship. The `audit/` directory preserves the earlier comparison of Acycle releases.

Clone this branch with its submodule and run `setup_migration` from the checkout in MATLAB. Each method package lives in `matlab/+acmethods`. Its `helper`, `analyzer` and `plotter` functions accept a parameter struct and an optional invocation ID. Each role can be called directly. Numerical dependencies are resolved from the pinned source. Original users and scientific publications are credited in the source comments. Copied ranges have MATLAB section markers and an upstream path and line range.

```matlab
setup_migration
request = struct('data', [0; 1.1; 2.5; 3.1; 7.3; 9.2]);
options = acmethods.circularspec.helper(request);
options.pn = 37;
[result, id] = acmethods.circularspec.analyzer(options);
```

The `logger(id, attr, info)` function writes an invocation journal. The first `init` records `op` and the `params` reference. The final `fin` records `status` and the `retval` reference. Status values are `incomplete`, `cancelled` and `done`. A returned empty value has an empty reference. The `event`, `msg` and `error` attributes carry `logging` and an empty `details` struct. Archives can move as a directory. `aclog.read(id, reference)` resolves a snapshot in a later session. Set `ACYCLE_LOG_DIR` to choose the archive directory, or supply an ID created by `aclog.newId`.

Run `addpath('tests'); test_migration` in MATLAB from the checkout. Headless numerical tests and the GUI reference have separate coverage.
