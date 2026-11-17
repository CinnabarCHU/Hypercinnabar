# Acycle 3.X analysis cores：修改范围、直接依赖与 GUI 调用路径

核对日期：2026-11-18。上游固定于 [`dcba427`](https://github.com/mingsongli/acycle/commit/dcba4279168745b563e0535b954297023dd62fc7)，本轮远程检查确认 master 仍在该提交。本报告是源码与历史追踪，不是 MATLAB 运行或数值等价性验证。

## 主要结论

1. `Add reusable desktop analysis cores` 的精确范围是提交 [`885c742`](https://github.com/mingsongli/acycle/commit/885c742de1d582c4b56afc6aab083f412f8bd373)：在 `guicode` 外新增 15 个 core 文件、5,548 行；修改 10 个既有文件、增加 488 行并删除 971 行。后者是 **9 个函数文件和 1 个绘图脚本**，不能笼统叫“改了 10 个函数”。另有 6 个 GUI 文件和 3 个新测试文件在该提交中变化，不计入以上生产代码数字。
2. 当前 `code/seriesanalysis/acycle*.m` 共 18 个文件、6,250 行、123 个函数声明（18 个公开主函数、105 个文件内辅助函数）。其中包含两个小策略 Helper；它不是 18 项桌面科学功能的覆盖率。
3. 这些文件大多把数值计算直接实现在新文件内部，或使用 MATLAB／Toolbox 函数，并非统一包装原有 Acycle 算法。18 个文件中，14 个没有其他仓库 MATLAB 文件的直接依赖；16 个不直接调用既有的非 `acycle*` 计算文件。
4. 直接被调用的既有计算文件只有 `rhoAR1ML`、`moveMedian`、`minirhos0`、`emdNL` 四个。前三个被 prewhitening core 使用，最后一个被 EEMD 路径使用。`find_extrema` 是 EEMD 的下一层依赖。
5. GUI 的调用方式混合存在：直接调用 core、先调用兼容入口再进入 core、继续调用旧函数，以及在 GUI 内直接组织计算。是否经过 core，甚至取决于同一窗口中的具体选项。

## 统计范围与历史归因

只统计 `code/` 下、`code/guicode/` 之外的生产 `.m`，排除路径中含 `test`、`tests` 的文件；不统计 `.fig`、文档和资源。`misc` 和 `package` 中仍有 GUI Helper／其他界面，因此“目录在 guicode 外”不等于“独立计算函数”。修改以 Git 同路径 blob 差异计；行数包含校验、注释与格式变化，不是算法改动百分比。

| 比较 | 新增文件 | 修改既有文件 | 删除文件 | 不变文件 | 增加／删除行 |
|---|---:|---:|---:|---:|---:|
| GUIDE 基线 `b52ea9f` → 当前 | 93 | 58 | 4 | 141 | +38,137 / −2,846 |
| 3.0 发布 `083c949` → 当前 | 38 | 66 | 0 | 188 | +16,677 / −1,670 |
| cores 提交前 `1ed99c8` → `885c742` | 15 | 10 | 0 | 265 | +6,036 / −971 |
| cores 提交 `885c742` → 当前 | 2 | 42 | 0 | 248 | +1,761 / −552 |

第一行覆盖整个 3.X 开发期间，包括 COCO、bispectral、统计界面等独立开发，**不能归因给 analysis cores**。最后一行同样包含 COCO 等并行变化，不能把 42 个文件全部称为 core 的后续改动。各比较的基线文件集合不同，因此 66 与 58 并非包含关系。

GUIDE 基线到当前的细分：

| 目录 | 基线文件数 | 新增 | 修改既有 | 删除 | 不变 |
|---|---:|---:|---:|---:|---:|
| `seriesanalysis` | 47 | 20 | 23 | 0 | 24 |
| `corrcoef` | 33 | 47 | 8 | 4 | 21 |
| `misc` | 47 | 8 | 12 | 0 | 35 |
| `package` | 76 | 18 | 15 | 0 | 61 |

因此，对“3.X 是否基本没动原有计算目录”的回答是否定的：`seriesanalysis` 原有 47 个文件中有 23 个发生变化。不过，发生源码变化不证明科学结果变化；反过来，旧文件未动也不证明当前 GUI 还使用它。

完整文件状态在 [non_guicode_changes.csv](cores/non_guicode_changes.csv)；公开／局部／嵌套函数的声明与签名变化在 [function_changes.csv](cores/function_changes.csv)。后者按词法作用域与函数名匹配，重命名计为删除／新增，父函数块包含嵌套函数；不能把声明变动数当作独立算法数量。

## 精确追踪那 10 个既有文件

以下行数仅针对 `885c742^..885c742`，不是相对 2.X，也不是累计 churn。

| 文件 | 增／删行 | 当时的变化与当前状态 |
|---|---:|---|
| `seriesanalysis/gaussfilter.m` | +55 / −193 | 旧入口转调 `acycleBandpassFilter`；采用 corrected-bandpass-v2，中心频率必须等于边界中点。保留签名不代表保持全部旧数值行为。 |
| `seriesanalysis/tanerhilbertML.m` | +65 / −114 | 转调同一个 bandpass core；删除 base-workspace 结果桥接，显式返回响应与瞬时频率坐标；校验和算法约定也变化。 |
| `seriesanalysis/movemean.m` | +24 / −49 | 转调 `acycleFixedCountMovingSummary`；保留按样点的窗口方向与列向量输出，明确拒绝缺失值。 |
| `seriesanalysis/movmeanfbw.m` | +109 / −148 | 转调 `acycleFixedBandwidthSummary`；保留可选绘图，改变／明确窗口中心、重复窗口和最少观察数等规则。 |
| `seriesanalysis/pda.m` | +50 / −97 | 转调 `acyclePowerDecomposition`；明确窗口首末坐标跨度、FFT 长度、总功率频带和积分规则。 |
| `seriesanalysis/pdan.m` | +76 / −122 | 当时也转调 PDA core；后在 `f7eda07` 恢复旧 DYNOT 规则，当前不再调用该 core。 |
| `misc/circularspec.m` | +58 / −72 | 成为 `acycleCircularSpectrum` 的兼容入口；保留排序、默认参数、行向量输出与可选绘图。 |
| `misc/dynamic_filter.m` | +18 / −130 | 旧交互入口缩为 `dynamic_filter_lang` 包装；后者负责选边界并进入新 core。旧入口本身仍需交互。 |
| `misc/dynamic_filter_lang.m` | +19 / −35 | 保留谱图／控制点选择，选点后转调 `acycleDynamicFilter`。 |
| `misc/update_filter_axes.m` | +14 / −11 | 绘图脚本适配新响应数组与瞬时频率坐标，移除旧工作区桥接。当前桌面静态入口未达，不代表外部不可调用。 |

同一提交还修改了 `AC`、`SpectralMomentsGUI`、`coherenceGUI`、`ft`、`leadlagGUI`、`prewhitenGUI`。这些 GUI 调用点变化是新 core 真正接入桌面的证据。

当前 18 个文件中，15 个来自 `885c742`；其余分别是：

- `acycleSamplingIsUneven`：`cf479dd`，2026-08-04，早于上述提交。
- `acycleEmpiricalModeDecomposition`：`c67146e`，2026-08-12；同次修改 `eemd`（+27 / −104）和 `emdNL`（+21 / −2）。
- `acycleMtmTaperCount`：`f7eda07`，2026-08-14；在谱分析回归修复中抽出共享 taper 计数规则。

这 18 个文件的**当前 blob 均与各自首次加入时相同**。后续回归修复主要通过 GUI、旧函数或外围策略完成；这个事实不等于它们已通过完整数值验证。

## cores 直接调用的旧函数，现在是什么状态

“直接”指从某个 core 文件中的主函数或局部函数调用另一个仓库文件。MATLAB／Toolbox 函数与同文件局部 Helper 单独记录，不混进这四个既有文件。

| 旧函数 | core 调用位置 | 相对 GUIDE 基线 | core 提交是否修改它 | 目前职责与注意点 |
|---|---|---|---|---|
| `rhoAR1ML` | `acyclePrewhitenSeries:40` | 字节完全不变 | 否 | 经典 lag-1 AR 系数估计；无 GUI／文件输出。core 在外部承担输入检查，并保留 Acycle 的向前残差方向。 |
| `moveMedian` | `acyclePrewhitenSeries:278` | +19 / −36，发生于 `b95b8e3`（07-17） | 否 | 循环实现改为 `movmedian`，补充参数检查；显式保留偶数窗口方向与端点收缩。源码目标是保持定义，未在本轮验证所有边界的等价性。 |
| `minirhos0` | `acyclePrewhitenSeries:288` | +70 / −43，同为 `b95b8e3` | 否 | 原 rho/S0 网格搜索改为代数向量化，增加正值／有限检查；平局取首个最小点。保留可选绘图，但 core 省略第六参数，使用默认 `genplot=0`。 |
| `emdNL` | `acycleEmpiricalModeDecomposition:439,442` | +21 / −2，发生于 `c67146e`（08-12） | 不在初始提交；后续有改 | 修正文件内主函数名，增加可选取消轮询；还新增极值不足时的提前终止，因此不只是界面接缝变化。 |

源码：[rhoAR1ML](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/rhoAR1ML.m)、[moveMedian](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/moveMedian.m)、[minirhos0](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/minirhos0.m)、[emdNL](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/emdNL.m)。

`emdNL → find_extrema` 再增加一个间接旧依赖，`find_extrema` 相对 GUIDE 基线字节不变。EEMD 的取消回调由外部注入，不要求创建窗口；其 `eemd` 兼容入口现在固定 seed 0、使用局部随机流、不再自己创建 waitbar。这与旧的随机执行行为有区别。

`minirhos0` 保留 Plotter 不妨碍这条默认关闭绘图的调用路径；需要区分“函数包含绘图代码”和“计算必须依赖图形状态”。向量化也不能仅凭注释就宣布 bitwise 等价：归约顺序、平局规则、有效输入集合均需要运行测试。

## 18 个 core 的仓库内直接依赖

| core | 直接调用的其他仓库文件 |
|---|---|
| `acycleAmplitudeModulation` | `acycleSamplingIsUneven`、`acycleInterpolateSeries` |
| `acycleEvolutionaryRho1` | `acycleInterpolateSeries` |
| `acycleEmpiricalModeDecomposition` | `acycleSamplingIsUneven`、`emdNL` |
| `acyclePrewhitenSeries` | `rhoAR1ML`、`moveMedian`、`minirhos0` |
| 其余 14 个 | 无其他仓库 `.m` 文件的直接依赖；使用同文件实现和 MATLAB／Toolbox 函数 |

例如 bandpass core 直接实现滤波响应并调用 FFT／Hilbert；coherence core 内部实现分窗与频谱累加；PDA core 调用 `pmtm` 并实现频带积分；spectral moments core 调用 `periodogram`。不能据此说它们“没有依赖”或不需要 Toolbox。

更重要的是调用方向：`gaussfilter → acycleBandpassFilter`、`pda → acyclePowerDecomposition`，不是反过来。`rmse4leadlag`、`spectralmoments`、`erhoAR1`、`interpolate` 和 `cohac` 相对 GUIDE 基线均未改变，但相应新 core 并不直接复用它们。它们有的继续在其他模式使用，有的已不在桌面入口的静态闭包中；不能因为有新 core 就删除旧函数。

## GUI 究竟调用谁

当前 18 个 `acycle*` 名称中，有 14 个在 `guicode` 中存在直接调用点，另有 3 个通过兼容入口或其他 core 间接到达，1 个没有桌面入口路径。这里是静态可能路径，**不是 17/18 的 GUI 功能覆盖率**。

| 情况 | 当前路径与条件 |
|---|---|
| 直接 core：Gaussian／Taner | `ft.updateBandpassPreview → acycleBandpassFilter`（475、496 行）；绕过 `gaussfilter`／`tanerhilbertML` 兼容入口。Cheby1／Ellip／Butter 则仍在 GUI 分支内调用 `designfilt`、`filtfilt`。 |
| 直接 core：coherence／lead-lag／prewhite | `coherenceGUI → acycleCoherencePhase`；`leadlagGUI → acycleLeadLagRmse`；`prewhitenGUI → acyclePrewhitenSeries`。 |
| 同一个主窗口中直接 core | `AC` 中 AM、普通 evolutionary rho、固定点数统计、Gaussian 平滑、沉积速率转年龄等菜单直接调用对应 core。 |
| 经旧入口进入 core：圆谱 | `circularspecGUI → circularspec → acycleCircularSpectrum`。 |
| 经旧入口进入 core：动态滤波 | `DynamicFilter → dynamic_filter_lang → acycleDynamicFilter`；中间层还负责交互选点。 |
| 两种路径汇入同一个 core | 固定带宽均值：`AC → movmeanfbw → acycleFixedBandwidthSummary`；固定带宽中位数：`AC → acycleFixedBandwidthSummary`。 |
| EMD／EEMD | 新菜单 `AC → acycleEmpiricalModeDecomposition`；去趋势窗口 `detrending → eemd → acycleEmpiricalModeDecomposition`。 |
| Spectral Moments 混合 | `sedrate==0 && (padedge==0 || padtype==1)` 才走新 `acycleSpectralMoments`；镜像／均值／随机边界，或沉积速率估计分支，仍调用旧 `spectralmoments`。 |
| Evolutionary rho 混合 | 普通模式调用 `acycleEvolutionaryRho1`；Monte Carlo 分支仍在 `AC` 中组织 `interpolate → erhoAR1` 与随机模拟。 |
| PDA／DYNOT 继续旧计算 | `AC.menu_pda_Callback → pdan`；`DYNOS → dynotIterationWorker → pdan`。当前 `pdan` 不调用 PDA core。 |
| 新 PDA core 尚未接桌面 | `pda → acyclePowerDecomposition` 存在，但仓库桌面图没有到 `pda` 的路径。外部脚本可以直接使用二者。 |
| 新插值 core 间接使用 | `acycleInterpolateSeries` 经 AM／rho core 使用；多处 GUI 的准备步骤仍直接使用旧 `interpolate`。 |
| 小策略 Helper | `acycleSamplingIsUneven` 与 `acycleMtmTaperCount` 被 GUI／旧函数共享；调用它们不意味着整个分析流程迁移到了 core。 |

关键源码：[ft](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/ft.m#L474-L530)、[SpectralMomentsGUI](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/SpectralMomentsGUI.m#L274-L331)、[PDA 菜单](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m#L7291)、[DYNOT worker](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/dynotIterationWorker.m#L15)。完整入口名、调用者函数、行号与可达标记在 [core_callers.csv](cores/core_callers.csv)。

## 对下一步 API 工作的影响

值得保留的是显式参数／返回值、无 GUI 必需状态、部分局部随机流与可注入进度回调，以及新旧入口共享同一个实现的接入方式。需要继续处理的是新旧科学定义并存、同一功能按选项切换实现、准备步骤还留在 GUI，以及少数兼容入口实际上改变了旧行为。

对 Harness，最先建立的应是“功能 + 模式 + 数值约定 → 当前桌面实际实现”的映射。不要按 `acycle` 前缀自动优先选新 core。PDA/DYNOT、Spectral Moments 和 rho 模拟特别需要明确路径。对已经独立、结果约定明确的旧函数可以保留，只提取外层数据准备／参数解析／步骤组织；新增 core 也可作为另一种明确标记的实现保留。

## 复现与验证边界

```bash
python -m unittest discover -s audit/tests -v
python audit/tools/track_analysis_cores.py
python audit/tools/verify_audit.py --regenerate
```

机器清单：[summary.json](cores/summary.json)、[core_inventory.csv](cores/core_inventory.csv)、[direct_dependencies.csv](cores/direct_dependencies.csv)、[history.csv](cores/history.csv)、[external_references.csv](cores/external_references.csv)、[validation.json](cores/validation.json)。

本轮检查发现旧审计器把二元表达式的左操作数也当作赋值左侧跳过，例如 `fft(x).*response`。新追踪器区分二者，并新增三个相关回归检查；在归档图上补充 53 条仓库内静态边，见 [graph_supplement.csv](cores/graph_supplement.csv)。这些补充不涉及 core 的仓库间边，以上四个旧直接依赖的结论不变；外部 FFT 等调用则得到补全。原有 15 份自动报告与上游源码保留不变。本报告中的静态图仍不解析任意 `eval`、外部 MATLAB path 遮蔽或所有运行分支。

没有修改 Acycle 科学代码，也没有运行 MATLAB／MEX／GUI。源码字节相同是可验证的事实，数值算法等价性仍需分别恢复历史测试并运行。
