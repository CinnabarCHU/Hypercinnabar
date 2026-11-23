# Acycle 方法模块归并评审

后续的[完整模块清单与实施约定](MODULE_INVENTORY.zh-CN.md)将本页的案例扩展到两个固定版本的全部源码，给出了共用内部目录、全项目唯一的新名字及旧操作标识的对应关系。实施时以完整清单为准。

评审对象是 `acycle-guide-migration` 的 `6a1a00e`，其中 `acmethods` 对应移除 GUIDE 前的 `b52ea9f`，`acmaster` 对应 `dcba427`（Acycle 3.1.1）。以 Li 的 v2.8 User’s Guide 第 4.6、4.7 节识别用户做的分析，再沿每一版实际回调确认数据、参数和产物。[迁移分支快照][review] · [User’s Guide][manual] · [两版菜单与变更](../migration/master/menus.tsv)

**建议以用户想完成的分析组织公开模块，以实际可复用的函数组织实现。** 一个菜单可以选中同一模块的不同参数或视图，一个模块也可以调用几个原函数。`helper`、`analyzer`、`plotter` 适合做参数和返回值适配、找到对应实现、经过一次公共 Logger。算法、绘图面板、以及某个版本独有的处理各有自己的实现位置。

## 现有封装有多厚

| 对已导出 MATLAB 文件的统计 | GUIDE 基线 | 3.1.1 |
| --- | ---: | ---: |
| 包 / 角色文件 | 227 / 388 | 286 / 401 |
| 只有 analyzer 的包 / 三个角色齐全的包 | 107 / 48 | 168 / 13 |
| 每个角色文件的中位行数 | 23 | 17 |
| 至多 30 行 / 超过 100 行的角色文件 | 234 / 36 | 302 / 22 |
| 在同一版本的不同角色文件中重复收录的上游源行 | 223 | 122 |
| 角色间直接写出的公开调用边 | 14 | 4 |

行数含空行、注释及来源标记。重复源行按仓库、提交、路径、行号去重，统计的是明确标为照抄的代码。调用边按调用方和被调用的公开角色去重，只计代码中写明的包名。两版同名角色共 309 对，去掉 `%% Copied from …`、`%% End copied source` 两种标记后，有 215 对从局部 `execute` 声明到文件末尾的文本逐行相同。相同文本可能调用两版不同的原函数或依赖不同资源，适合作为共享候选，仍需验证依赖和结果。可在仓库根目录运行 `python audit/tools/module_reuse.py`，加 `--candidates` 可列出这 215 对。[统计脚本](tools/module_reuse.py) · [GUIDE 方法表](../migration/methods.tsv) · [3.1.1 方法表](../migration/master/methods.tsv)

短封装占多数，工作量集中在几组混合了不同职责的文件。还有与行数无关的缺口。3.1.1 比对表里 107 个菜单的原生转发入口是 `acmaster.Desktop.plotter`。它找到已打开的窗口，按 `tag` 调用菜单，返回 `tag`。这能保留桌面操作；后续对话框选定的数值参数不会自动进入这一条调用记录。表中的 `master_related_packages` 是相关包索引，不能用来推断 GUI 逐项调用了这些包。[桌面转发][desktop] · [菜单表的生成方式][menucheck]

## 三组应当怎样归并

### 插值

手册中的名称是 *Interpolation*。第 41–42 页把普通等距插值、可配置的 Pro 和按参考序列对齐放在一起。建议在一个插值模块内保留这些入口，再将 3.1.1 的独立 `acycleInterpolateSeries` 登记为有自己输入约定的第四种实现。[手册][interpguide]

| 入口 | 当前执行内容 | 归并时保留的区别 |
| --- | --- | --- |
| Interpolation | `AC.m` 从数据建议中位间隔，最终调用 `interpolate(data, step)`。该文件在两版 Git blob 相同。 | 线性等距插值，读取前两列，返回两列。可直接原地调用。 |
| Interpolation Pro | 现行 GUI 在 `interpolationGUI.m` 的嵌套 `updatePlot` 中选九种方法、造网格、处理间隙；现有 `acmaster` Analyzer 取自仍留在树中的 `code/misc/update_interpolationGUI.m`。 | 现行 GUI 先排序，通常按步长造网格，网格不足两点时取两个端点。现有封装少了端点补足；Analyzer 还返回旧接口使用的标题及图例。 |
| Interpolate Series | 现行 `InterplationSeries.m` 对两份输入排序，按参考坐标插值目标序列，并画三幅子图。 | 参考坐标可以不等距；超出目标覆盖时得到缺失值。当前独立包只有 Analyzer，三联图仍在 GUI。 |
| RegularInterpolation | 包装上游 `acycleInterpolateSeries`；它也被调幅和演化 ρ₁ 的计算使用。 | 多列、严格递增、资源上限、短尾及元数据构成这个版本的契约。保留原函数及其原有调用方。 |

发现了一处会改变结果的文档分歧。手册写的是按**中位间隔**判断大间隙并填 `NaN`。3.1.1 活跃 GUI 和现有 Pro 封装实际按**目标步长**乘阈值判断，把开区间内的点填 `0`。应把它登记为该版本的实测行为。若希望支持手册口径，可增加显式选项并单独登记其版本。[手册][interpguide] · [普通插值][interpbase] · [活跃 Pro 回调][pronative] · [已交付的 Pro 封装][prowrapper] · [参考序列窗口][intref] · [独立多列内核][intcore]

### Math 的数值变换

`DataTransform.analyzer` 已在一个文件里处理 16 个 `j` 值。实际障碍在于下拉框和编辑框编号成了参数名。公开目录只列 `data/checkid/j`，但区间归一化还需 `edit1/2`，指定底数的对数和指数分别需 `edit3`、`edit4`；当前 3.1.1 包也缺少这个窗口对应的 Helper。可由 Helper 把 GUI 选择和旧编号映射到变换名、目标列及相应参数，在 Analyzer 中按名称调 `zscore`、`log10`、`boxcox` 或一个带来源的小函数。对当前分支还须保留 `yt/lambda` 等既有返回字段。[手册][mathguide] · [变换 Analyzer][transform]

| 可归在同一模块的入口 | 应保留的语义 |
| --- | --- |
| Standardize / Data Transform 的标准化 | 快捷入口对第 2 列手算 `(y-mean(y))/std(y)`；窗口路径对所选列用 `zscore`。常数列可区分两者。 |
| Log10 / 指定底数的对数 / Simple Function | 旧 Log10 只输出坐标和第 2 列；窗口按选列写回原矩阵。Simple Function 对 X、Y 各用一组仿射系数。 |
| Box–Cox 的两条路径 | GUI 分支在必要时将数据平移到正值并估计 λ；已有 `boxcoxML(y,lambda)` 要求正值并使用给定 λ。应分别保留估计与应用两种选择。 |

旧编号、字段和文件输出约定由兼容入口翻译；GUI 预览、批处理和重放可以使用同一条变换实现。首次抽取时，现有 MATLAB 表达式与矩阵运算顺序一起保留。[快捷标准化][standardize] · [仿射变换][affine] · [给定 λ 的原函数][boxcox]

### 谱分析

全序列功率谱适合由一个 Analyzer 处理估计器与背景模型选择。3.1.1 的 `PowerSpectrum.analyzer`（259 行）在 MTM、periodogram 与 Lomb–Scargle 间选择，再处理六个可选模型或诊断；Plotter（321 行）画主谱、模型曲线及额外诊断窗。`computeSpectrum` 和两种幂律拟合在上游 `spectrum.m` 内部，无法从外部直接调用。`powerLawLevels`、`bendingPowerLawLevels` 和 `stableSoftplus` 的 66 行上游源代码，同时出现在这一 Analyzer 及两个独立幂律 Analyzer 中。这是可先做的、能逐行核对的去重。`redconfML`、`ftestmtmML(...,0)` 等已有可独立调用的函数继续保留在上游路径。[手册][spectralguide] · [功率谱 Analyzer][power] · [功率谱 Plotter][powerplot] · [原始嵌套实现][specsource] · [幂律][pl] · [弯折幂律][bpl]

同一目录下仍需有清楚的工作流边界。全序列功率谱输出完整频率、功率和显示掩码；某个背景模型失败后，现行接口可保留主谱并给 `incomplete`。演化谱输出滑窗矩阵和两条坐标轴，现有 `evoperiodogram`、`evoplomb`、`evopmtm` 等可分别原地调用。单独的 SWA 菜单组合 `specswafdr(data_r,0)` 和 `specbayes(data_r,0)`，上游还据此写科学数据文件。GUIDE 包已有这对调用及工作目录隔离；3.1.1 的 `SWA` 包有 Helper 和 Plotter，缺少对应的组合 Analyzer。功率谱内可选的 SWA 背景与这项独立分析的输出不同。小波相干、双谱等也各自有输入维度和产物。[演化谱][evo] · [SWA 原生调用][swanative] · [基线组合与报告][swabase] · [3.1.1 SWA 包][swapkg]

## 实现存放与日志边界

| 遇到的代码 | 建议位置与调用 |
| --- | --- |
| 上游已有可独立调用的 `.m` | 保持固定提交和原路径。在公共角色中把合法参数完整传给它；已有绘图开关时显式关闭。需要哪些原文件、资源和工具箱由打包清单记录。四个移动均值/中位数 Analyzer 就能缩成统计量 × 窗口单位四条映射：固定点数调用 `acycleFixedCountMovingSummary`，物理窗宽调用 `acycleFixedBandwidthSummary`。保留两原函数的入参、有效窗口和输出列。 |
| 只在一个窗口内可见的回调、嵌套函数、面板绘图 | 放在相应家族的 `private/` 内，如 `+PowerSpectrum/private/`。按步骤或面板抽取，保留 `%% Copied from …` 与 `%% End copied source`、原行号及提交。每个角色最多保留必要的参数适配、选择、汇总和日志。 |
| 多个包或兼容入口确实共用的抽取函数 | 置于按主题命名的内部包。例如全谱和两个独立幂律入口可同时调用同一个内部谱拟合函数。同一父目录的 `private/` 适合族内共享。跨版本复用先核实被调函数和资源、路径解析、随机状态及数值行为。 |
| 已有 `.m` 但绘图或写文件是无条件的 | 独立文件也要检查副作用。`smoothciML` 第 35–42 行计算 Bootstrap 结果，第 46、61 行直接开图，没有开关。可将这八行仅抽取一次，底下继续用已有 `smoothci`；两个视图交给 Plotter。`specswafdr` 的原始文件产物可由现有工作目录隔离收集。 |

新注册表只需描述「版本化 `op`、角色、入口或变体、实际实现」。现有方法表仍负责来源核对。GUI 控件、CLI 和 Harness 都可以调用同一公开角色；GUI 负责选择文件和显示窗体，Helper 计算建议值，用户修改后的完整参数进入 Analyzer 日志。Plotter 可按参数选择整图或一个面板，绘图目标可由 GUI 提供，复现记录保存面板名、坐标单位和样式，重放时重新创建图形目标。现行功率谱 Plotter 一进入就新建图窗，正好可用于验收嵌入子图的能力。[固定点数][smoothcount] · [物理窗宽][smoothwidth] · [Bootstrap 原函数][smoothboot] · [现有图形入口][powerplot]

现有 `logger(id,attr,info)` 能继续使用。每次直接调用公开角色，经过一次 `init` 与一次 `fin`；模型级诊断可写到当前 `id` 的 `event`。旧基线的功率谱会再次调用 `acmethods.SpectralPowerLaw.analyzer` 等公开角色，产生独立的调用文件和参数快照。兼容入口可以沿用其旧 `op`、旧参数和返回结构，同时和新入口共用内部实现。确实代表独立用户操作的子调用仍可单独记录。注册表要让旧 `op` 能选回固定的源版本，当前 `aclog.replay` 会用正则从两个允许的版本直接拼 MATLAB 包名。[嵌套调用][oldpower] · [调用日志][invoke] · [回放分派][replay]

## 建议的实施顺序和验收

1. 以插值作首个纵向试点。保留三个菜单和四种行为；建一个最小的家族索引、补 Pro 的参数推荐和参考序列三联图，再将当前 GUI 行为和旧 journal 行为分别落到对应路径。先用两个端点的反例验收，再对旧操作逐一回放。可同时用移动均值/中位数四个入口验证全程直接调用上游函数的情形。
2. 归并 Data Transform。把 16 个旧编号及条件必需参数整理成一个选择表，覆盖常数列、多列、非正数、两种 λ、输出字段。新增方法只需登记其所需角色和实现。给实现层工具函数保留原来的直接使用方式；一个独立 GUI 或 Harness 工作流按需暴露相应角色。
3. 从两种幂律和稳定 softplus 开始拆全序列功率谱；随后分离估计器、模型和绘图面板，并补 3.1.1 独立 SWA 的组合入口。验收比较完整谱与显示掩码、模型失败时的部分结果、报告文件、固定随机状态、整图和指定坐标轴。随后的 COCO/eCOCO、静态/动态滤波、EMD/EEMD 等可共享导航，按物理窗/计数窗、控制点、随机种子和结果维数决定能共享到哪一层。
4. 首个试点提交中一起适配打包和审计。当前两个来源检查器只遍历 `+包/*.m`，会漏掉移入 `private/` 的来源段。GUIDE 导出器会跟进同目录 `private/`；3.1.1 导出器会复制已选包的目录树，但只在包的顶层 `.m` 搜索跨包依赖，导出时还会带上整个上游 `code`、`data`。对新共享包提供显式依赖，并从空的 MATLAB 路径运行导出包，分别验证新入口、旧操作回放、独立调用每个角色的日志。这样抽取之后仍能单独交付一个家族。[基线检查][guidecheck] · [3.1.1 检查][mastercheck] · [导出器][exporter]

## 复核记录与范围

已运行两版来源校验和 GUIDE 控件校验（分别为 710、425 段逐行照抄，33 个 FIG、970 个控件）。下列数值比较在 GNU Octave 10.3.0 上通过 3.1.1 公开入口完成。另用 GUIDE 基线公开角色复核了普通等距插值、Pro 间隙和粗网格、两种常数列标准化。原生 GUI 的两点兜底按其 MATLAB 源表达式核对，本轮的 GUI 行为依据为源码。

| 输入 | 观察结果 |
| --- | --- |
| `x = [0;1;5;6]`、`data = [x,x,2*x]`、步长 1 | 普通插值 `7×2`，独立严格内核 `7×3`。Pro（线性、间隙倍数 2）返回 `[0 1 0 0 0 5 6]`；同一条 Pro 调用日志重放一致。 |
| 同一组数据，Pro 步长改为 8 | 已交付的 Analyzer 仅给坐标 `0`。现行 GUI 的 `numel(xq)<2` 分支给 `[0 6]`。 |
| 参考坐标 `[7;2.5;-1]`、目标 `[6 6;0 0]` | 对齐结果的坐标为 `[-1;2.5;7]`，中间值为 `2.5`，两端为缺失值。 |
| 第 2 列为 `[12;12;12;12]` | 旧快捷公式输出四个 `NaN`，所选列的 `zscore` 路径输出四个 `0`。 |
| 9 行、固定点数 3；另取物理窗宽 3、步长 1、仅完整窗口、均值取 α = 0.05 | 四个移动均值/中位数公开入口的数值结果分别与原地直调的上游函数一致。物理窗宽均值返回 6 列，中位数返回 3 列。 |

配套清单覆盖两版主窗口菜单标签并集的 135 项。`kind` 标出工作流、视图、数据资源、桌面动作、兼容项及导航标题，`candidate_group` 供讨论归属；同组仍可以保留多个独立操作。子窗口选项、只供程序调用的内核和动态依赖由各组进一步核对。`visible`、`hidden`、`absent` 取自两版菜单声明。[候选分组表](module_groups.tsv) · [现有功能差异](../migration/master/features.tsv)

[review]: https://github.com/CinnabarCHU/Hypercinnabar/tree/6a1a00eae0254267070e72b9c10c17e7ab7ab694
[manual]: https://acycle.org/docs/Acycle_Users_Guide.pdf
[interpguide]: https://acycle.org/docs/Acycle_Users_Guide.pdf#page=42
[mathguide]: https://acycle.org/docs/Acycle_Users_Guide.pdf#page=46
[spectralguide]: https://acycle.org/docs/Acycle_Users_Guide.pdf#page=56
[desktop]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+acmaster/+Desktop/plotter.m#L9-L37
[menucheck]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/migration/master/compare.py#L168-L193
[interpbase]: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/interpolate.m#L3-L19
[pronative]: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/interpolationGUI.m#L152-L215
[prowrapper]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+acmaster/+InterpolationPro/analyzer.m#L14-L68
[intref]: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/InterplationSeries.m#L128-L185
[intcore]: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleInterpolateSeries.m
[transform]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+acmaster/+DataTransform/analyzer.m
[standardize]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+acmaster/+Standardize/analyzer.m#L9-L17
[affine]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+acmaster/+SimpleFunction/analyzer.m#L9-L20
[boxcox]: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/boxcoxML.m
[power]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+acmaster/+PowerSpectrum/analyzer.m
[powerplot]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+acmaster/+PowerSpectrum/plotter.m
[specsource]: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/spectrum.m#L1569-L1662
[pl]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+acmaster/+SpectralPowerLaw/analyzer.m#L21-L43
[bpl]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+acmaster/+SpectralBendingPowerLaw/analyzer.m#L21-L70
[evo]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+acmaster/+EvolutionarySpectrum/analyzer.m#L11-L35
[swanative]: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/SWAgui.m#L139-L169
[swabase]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+acmethods/+SWA/analyzer.m
[swapkg]: https://github.com/CinnabarCHU/Hypercinnabar/tree/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+acmaster/+SWA
[smoothcount]: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleFixedCountMovingSummary.m
[smoothwidth]: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleFixedBandwidthSummary.m
[smoothboot]: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/smoothciML.m#L35-L70
[oldpower]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+acmethods/+PowerSpectrum/analyzer.m#L83-L107
[invoke]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+aclog/invoke.m#L14-L38
[replay]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/matlab/+aclog/replay.m#L9-L23
[guidecheck]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/migration/check.py#L95-L108
[mastercheck]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/migration/master/compare.py#L59-L86
[exporter]: https://github.com/CinnabarCHU/Hypercinnabar/blob/6a1a00eae0254267070e72b9c10c17e7ab7ab694/migration/export_method.py#L71-L146
