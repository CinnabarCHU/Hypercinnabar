# Acycle GUIDE method migration

[DeepSeek Harness 插件 0.6.0 安装、菜单调用及重放](harness/README.zh-CN.md)

[按当前 GUI 菜单调用 GUIDE 和 master](migration/menu/README.zh-CN.md) · [全部菜单及版本选择值](migration/menu/MENUS.md)

[逐项归并方案（62 项源码归属）](audit/MODULE_CONSOLIDATION.zh-CN.md) · [helper / analyzer / plotter 契约评审](audit/METHOD_ROLE_REVIEW.zh-CN.md)

The pinned Acycle 3.1.1 implementation is available beside GUIDE through `acmaster`. [两版功能对照与并行调用](migration/master/README.zh-CN.md) · [master methods](migration/master/methods.tsv) · [menu changes](migration/master/menus.tsv)

Portable MATLAB analysis methods for the last GUIDE-era [Acycle revision, `b52ea9f`](https://github.com/mingsongli/acycle/tree/b52ea9f510f3be00bde9a0238b9898a1e2315b74). [中文迁移说明](migration/README.zh-CN.md) · [method catalogue](migration/methods.tsv) · [GUIDE menu coverage](migration/menus.tsv) · [recovered sources](migration/recovered.tsv)

```sh
git clone --branch acycle-guide-migration --recurse-submodules https://github.com/CinnabarCHU/Hypercinnabar.git
```

From the checkout, run this example in MATLAB with Signal Processing Toolbox.

```matlab
setup_migration
t = (0:255)';
data = [t, sin(2*pi*t/20) + 0.2*cos(2*pi*t/5)];
p = acmethods.Bandpass.helper(struct('data',data));
p.flow = 1/25;
p.fhigh = 1/16;
[result, id] = acmethods.Bandpass.analyzer(p);
p.result = result;
p.unit = 'm';
acmethods.Bandpass.plotter(p);
assert(isequaln(result,aclog.replay(id)));
```

Each historical package role accepts a scalar parameter struct and an optional call ID. The role catalogue lists the fields for each package. Helpers recommend parameters, analyzers produce numerical results, and plotters accept explicit data and display settings. Some data operations have only an analyzer. The reference GUIDE application continues through its original callbacks. The `matlab/+acmethods` packages can be used by code, a GUI, a workflow editor or a harness.

To take selected methods to another project, export them from the checkout. The resulting folder includes the original role files, their method dependencies, logger, selected Acycle runtime files and a checksum manifest.

```sh
python migration/export_method.py Bandpass TimeOpt Undatable --output ../acycle-methods
```

Open the output folder in MATLAB and run `setup_method`. MATLAB toolboxes and optional external orbit data must be available on the destination machine. The exporter follows MATLAB function and script names, quoted lookup names, referenced datasets and package-private files. Use the 3.1.1 `acmaster.DigitizeTrace` package for new automatic plot digitization. Historical GUIDE journals keep their recorded engines. [Digitizer example and standalone export](migration/master/README.zh-CN.md#自动追踪示例)

The journal records `init(op,params)` and `fin(status,retval)`. References point to companion MAT snapshots. `event`, `msg` and `error` contain `logging` and `details`. Replays restore the original random stream, call the recorded operation and create a new journal. Set `ACYCLE_LOG_DIR` to choose the journal directory. Move a call's whole directory to share it.

Run `python migration/check.py --figures` to compare all attributed code blocks and serialized GUIDE controls with the reference. The [MATLAB workflow](.github/workflows/guide-methods.yml) includes numerical comparisons, figure generation, a file-independent Undatable replay and package isolation tests. The [earlier upstream review](audit/) is retained.
