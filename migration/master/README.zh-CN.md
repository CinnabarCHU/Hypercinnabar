# GUIDE 基线与 Acycle 3.1.1 的功能差异

本分支把移除 GUIDE 前的最后一个提交 `b52ea9f` 和上游 `master` 的 `dcba427` 分别固定在 `upstream/acycle`、`upstream/master`。前者通过 `acmethods` 调用，后者通过 `acmaster` 调用。原来的数值内核、图窗和历史补回文件均可按各自版本继续使用。后续上游提交需要另行对比。[基线](https://github.com/mingsongli/acycle/tree/b52ea9f510f3be00bde9a0238b9898a1e2315b74) · [Acycle 3.1.1](https://github.com/mingsongli/acycle/tree/dcba4279168745b563e0535b954297023dd62fc7) · [上游代码差异](https://github.com/mingsongli/acycle/compare/b52ea9f510f3be00bde9a0238b9898a1e2315b74...dcba4279168745b563e0535b954297023dd62fc7)

## 菜单与文件如何变化

| 比较项 | GUIDE → 3.1.1 |
| --- | --- |
| 主窗口菜单声明 | 原有 130 个，当前 128 个，合并去重共 135 个。123 个标签两端均有。 |
| 可见入口 | 121 个两端初始可见。新增可见入口是双谱和设置。原先可见的 6 个标签从声明中消失，另有 2 个改为隐藏。这里的可见性取自原 FIG 和当前程序化布局。 |
| 改换父菜单 | ANOVA、两个样本检验、正态性检验和卡方拟合优度搬到 Bivariate；PCA 搬到 Math。原 Multivariate 标题改为隐藏。 |
| 文件树 | 两端共 459 个不同路径。104 个新增、99 个修改、47 个移除、209 个内容相同。25 个 `data/` 文件全部逐字节相同。 |
| 数值与其他非主 GUI 源码 | `code/guicode/` 以外的 `code/**/*.m` 有 93 个新增、58 个修改、4 个移除、141 个相同。此口径包含包内 GUI、辅助函数、导出和验证程序。 |
| 原始图窗 | 移除 32 个 `.fig`，Undatable 的 `code/package/undatable/undatableGUI.fig` 在两端字节相同。 |

下表列出会影响方法选择或结果解释的变化。逐菜单表给出两端父菜单、初始可见性、回调、相关包和源码位置。文件表包括全部路径和两端 Git blob，对源代码完全相同的文件也保留记录。[135 个菜单标签](menus.tsv) · [功能差异和证据](features.tsv) · [完整文件树对照](sources.tsv) · [函数签名变更](../../audit/cores/function_changes.csv)

| 工作流 | 影响和保留方式 |
| --- | --- |
| COCO / eCOCO | 同一菜单演变成 Adaptive、Fixed-target、Blocked 和 Interleaved 等工作流。新版区分对整个沉积速率扫描校正的 p 值和逐速率 p 值。Adaptive eCOCO 的直接 core 默认按样本计数分窗，现代 GUI 路径使用物理深度分窗。旧 COCO、兼容目标模型和新算法都保留独立入口。 |
| 双谱 | 新增 bispectrum、biphase 和平方双相干。脚本默认关闭推断，可显式选择 IAAFT 最大统计量校正。双谱自己的 `InputPolicy='prepare'` 有独立的可配置不规则采样容差；严格模式才使用近等距规则。 |
| Gaussian / Taner 与动态滤波 | 新带通核校验中心频率，按半功率边界构造频响。Taner 显式返回瞬时频率的坐标。动态滤波支持用上下界控制点调用数值核；原交互绘点入口也在当前上游快照中。 |
| 功率谱 / 演化谱 | MTM 的自由度取实际 taper 数，显示上限、物理 Nyquist 和稳健红噪声拟合上限分别处理。零填充默认使用等于输入行数的精确 NFFT。频率或周期坐标、SWA、弯折幂律拟合和演化谱窗覆盖都有实质修改。 |
| DYNOT / Power Decomposition | 新版 DYNOT 使用同一个逐次模拟函数；即使用户不勾选 Median，50 分位仍参与绘图与保存。旧的 v2 菜单原本和主 DYNOT 菜单都调用 `DYNOS`。旧、新数值步骤和图形各自保留。 |
| 平滑、插值及预白化 | 当输入为 `[1;NaN;3;5]`、窗宽为 3 时，旧 `movemean` 逐窗忽略 NaN，给出 `[1;2;4;4]`，新版拒绝非有限输入。新均匀插值遇到短尾段时会留下余量。预白化仍用历史的前向残差。 |
| EMD / EEMD | GUIDE 基线已经提供两项，3.1.1 恢复了开发中途暂时下线的菜单，另提供显式种子、IMF 方差贡献、进度和取消控制。 |
| 统计及数字化 | 新版线性回归使用有限行、`polyfit`、Pearson r/p 和 RMSE。旧版迁移保留发行包里的 `fitlm`、区间和 ANOVA。单样本 t 图以 t 统计量定标。数字化从两个旧窗口改为合并窗口，新增可从种子追踪连通暗线的 Strict / Loose 算法。 |
| 从菜单撤下 | TimeOpt、eTimeOpt、Lyapunov 和单独的 Lag-1 v2 科学入口保留在 `acmethods`。Lag-1 v2 和主 Lag-1 的历史实现分别保留。新版 `AC.m` 仍有部分撤下菜单的回调定义。 |
| 桌面操作 | Open Working Directory 的标签仍在但已隐藏；另一个 Open *.fig 标签在旧版就已隐藏，此次从布局消失。语言从独立菜单移入设置，语言选择暂时禁用。新声明的 log10、norm 和 utilities 为隐藏兼容控件。 |

四个从非 GUI 目录消失的旧文件是 `corrcoefslices_rank.m`、`cyclecorrsig.m`、`freq2target.m` 和 `period2spectrumB.m`。各自仍有旧版可调用包。新版的 `corrcoefslices_rankNew`、`cyclecorrsigNew`、`freq2targetNew` 和 `freq2targetFixed` 各有明确的参数契约。调用方应按所需目标模型选择。[两版 COCO 调用链](../../audit/cores/) · [旧版方法表](../methods.tsv) · [新版方法表](methods.tsv)

当前上游还有一个会在运行时显现的断点。六个保留文件 `cyclecorr`、`cyclecorr4`、`cyclecorr4sig`、`cyclecorr5`、`cyclecorr_rank` 和 `cyclesig_rank` 仍引用已经移除的四参数 `freq2target`。直接按 master 执行，相应分支会报告缺少函数。若给这六个包或其四个上层入口的参数添加 `p.legacyTarget = 'guide-b52ea9f'`，调用期间会启用经过逐行校验的旧函数，选择会随参数写入日志并用于重放。现代 COCO 工作流使用自己的目标构造。[兼容函数与来源](../../upstream/compatibility/coco/freq2target.m) · [依赖它的旧核](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cyclecorr4.m)

## 在 MATLAB 中并排运行

从迁移分支根目录运行 `setup_migration`。首次克隆使用 `--recurse-submodules`；已有检出执行 `git submodule update --init --recursive`。两个版本都用 `helper`、`analyzer`、`plotter`。方法表标明每个包实际提供的角色、必填输入及源码。新版 wrapper 在调用期间切换 MATLAB 函数搜索路径，发生错误时也恢复原路径。GUI 或 Harness 可以把返回的参数 struct 交给用户修改后再运行。

```matlab
setup_migration
t = (0:255)';
d = [t, sin(2*pi*t/32) + 0.2*cos(2*pi*t/8)];

old = acmethods.Bandpass.helper(struct('data',d));
old.flow = 1/40; old.fhigh = 1/24;
[a,oldId] = acmethods.Bandpass.analyzer(old);

now = acmaster.Bandpass.helper(struct('data',d));
now.options.lower_frequency = 1/40;
now.options.upper_frequency = 1/24;
[b,newId] = acmaster.Bandpass.analyzer(now);

assert(isequaln(a,aclog.replay(oldId)));
assert(isequaln(b,aclog.replay(newId)));
```

每个调用自己的 `init.op` 会记录版本，例如 `Bandpass-v1.0/analyzer` 和 `Bandpass-v3.1.1+dcba427/analyzer`。`v1.0` 表示原 GUIDE 迁移接口版本。参数、返回值与初始随机状态随日志保存。双谱结果的 `Created` 是上游生成的运行时间，比较重放时应比较谱矩阵、配置与推断结果。需要导出双谱时，`BispectralExport.plotter` 走原版的唯一目录和原子保存流程。

```matlab
p = acmaster.Bispectral.helper(struct('data',d));
s = acmaster.Bispectral.analyzer(p);
v = acmaster.Bispectral.helper(struct('result',s));
v.settings.Visible = 'off';
acmaster.Bispectral.plotter(v);
```

当前发行包的实验管线具有文件 I/O；运行发表用 COCO / eCOCO 批处理时，需要提供它请求的输入目录、数据和输出目录。为其他项目单独打包可以运行下面的命令。导出件包含所选 wrapper 及其引用的其他方法、本版上游运行时代码和数据，用于保留动态回调及资源查找的行为。

```sh
python migration/export_method.py --revision master Bandpass Bispectral --output ../acycle-311-methods
```

## 自动追踪示例

新 GUI、脚本和 Harness 的自动追踪使用 `acmaster.DigitizeTrace`。在仓库根目录，下面的例子以原图左上数据点为种子，以图上的刻度把像素换为横轴 Value 和纵轴 Time。像素坐标采用 MATLAB 的一基 `[列 行]`。四个校准点依次对应 x 最小、x 最大、y 最小、y 最大。[Acycle 示例原图](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/data/Examples/Example-PlotDigitizer.jpg) · [GUIDE 历史与旧调用重放](../README.zh-CN.md#旧数字化器的自动追踪)

```matlab
setup_migration
img = imread(fullfile('upstream','master','data','Examples','Example-PlotDigitizer.jpg'));
cal = struct('pixels',[91 1106; 595 1106; 91 1028; 91 94], ...
    'limits',[-200 1400 0 120],'logX',false,'logY',false);
p = acmaster.DigitizeTrace.helper(struct('image',img,'seeds',[164 164],'calibration',cal));
p.mode = 'Loose';  % 'Strict' stops sooner at discontinuities or large pixel jumps
[r,id] = acmaster.DigitizeTrace.analyzer(p);
acmaster.DigitizeTrace.plotter(struct('image',img,'result',r));
assert(isequaln(r,aclog.replay(id)));
```

`r.pixels` 是追踪路径，`r.data` 是标定后的坐标。这张图的主要走向为纵向，算法沿每一行选一个像素。在 Time 约 61 的尖锐右向折返处，用图上的黑点中心 `[571 553]` 对照，即可检查自动路径错过顶点的距离。需要原始测点时，可用手工 Digitize 点击圆点中心。单独交付新版自动追踪可执行以下命令，在导出目录运行 `setup_method` 后即可使用相同的三个角色。[独立包测试](../../tests/test_master_export.m)

```sh
python migration/export_method.py --revision master DigitizeTrace --output ../acycle-digitizer
```

## 如何核验覆盖范围

`python migration/master/compare.py` 读取两棵固定的 Git 树和原始 `AC.fig`，校验清单、所有 `%% Copied from` 段落、文件路径及角色 ID。新版有 286 个方法包、401 个角色，其中包含 229 个在当前源码重新定位并核对的旧角色。逐菜单表的 `master_related_packages` 列列举相关部件，一个菜单可以由多个部件组成。源码相同和科学结果等价是两种不同的检验，后者需要给定数据、参数和比较指标。[新版测试](../../tests/test_master_migration.m) · [独立导出测试](../../tests/test_master_export.m) · [原生菜单验证](../../tests/test_master_native_menu.m)

原版桌面可分别从固定提交的 `ac.m` 启动。桌面有跨调用存活的图形句柄，建议把两代原 GUI 放在各自的 MATLAB 会话中。运行 3.1.1 桌面时，可向会话加入迁移目录的 `matlab/`，通过 `acmaster.Desktop.plotter(struct('tag','menu_settings'))` 触发实际菜单。此日志记录所触发的入口；用户随后在原生窗口内作出的选择仍由原窗口处理。需要自动重放的分析可直接调用相应方法，并传入选定参数。原 GUI 的鼠标序列、不同操作系统的窗口外观，以及所有工具箱和参数组合尚未逐项回归。

基线回归使用 3.1.1 MATLAB 发行包中的 `fitlm` 副本，尚无法确认 `b52ea9f` 部署时的同一文件。旧数字化器的双参数 `getPKS(image,2)` 和四参数 `trackline` 仍缺定义，历史接口和已标记的替代路径一并保留。单独核对 v2.8 与 v3.0.3 的发布源码后，可以确认新版回归和数字化器在 v3.0.3 已与当前固定 master 逐字节相同，v2.8 则能确认五个 TimeOpt 原文件。[两个发布包的逐项核对](../README.zh-CN.md#v28-与-v303-的发布包核对)

