# Acycle 完整模块清单与代码存放约定

本清单以 GUIDE 移除前的 `b52ea9f` 为基线，同时保留 Acycle 3.1.1 的 `dcba427`、已考证的恢复文件和显式兼容入口。可以先确定维护归属，继续从现有位置调用原函数。逐模块查入口、参数选项、产物与两版覆盖，见[模块总表](modules/modules.tsv)。按旧操作标识查去向，见[全部公开角色](modules/roles.tsv)。[基线源码](https://github.com/mingsongli/acycle/tree/b52ea9f510f3be00bde9a0238b9898a1e2315b74) · [3.1.1 源码](https://github.com/mingsongli/acycle/tree/dcba4279168745b563e0535b954297023dd62fc7) · [Li 的 User’s Guide](https://acycle.org/docs/Acycle_Users_Guide.pdf)

这 62 项覆盖科学操作、GUI、工作流与工程验证。95 个 GUIDE 科学或数据菜单和 286 个 3.1.1 包使用另外的计数单位。逐项对应、建议的公开边界及其依据见[菜单、兼容包与公开方法](MODULE_BOUNDARIES.zh-CN.md)。

当前归并方案逐项列出维护位置、可独立调用的操作、角色以及旧操作的对应关系。下表保留第一轮的源码归属和计数。[新版逐项方案](MODULE_CONSOLIDATION.zh-CN.md) · [接口实测与评审](METHOD_ROLE_REVIEW.zh-CN.md)

## 62 项源码归属

| 范围 | 模块及其登记标识 |
| --- | --- |
| 桌面与工作区（4） | 窗口与导航 `Desktop`、文件与数据表 `Workspace`、设置与帮助 `SettingsHelp`、Mini-Robot 批量流程 `Robot` |
| 数据与天文（6） | 信号与噪声生成 `SeriesGenerator`、日照量 `Insolation`、天文解 `OrbitSolution`、轨道周期 `OrbitalPeriods`、LR04/CENOGRID `ReferenceSeries`、示例 `Examples` |
| 序列与数学（10） | 排序去重 `SortUnique`、列处理 `Columns`、插值与参考坐标对齐 `Interpolation`、区间裁剪与修峰 `SeriesEditing`、序列间运算 `SeriesArithmetic`、数值变换 `Transform`、导数 `Derivative`、极值 `Extrema`、变点 `Changepoint`、主成分 `PCA` |
| 图像与展示（8） | 序列绘图 `SeriesPlot`、数值分布 `Distribution`、采样间隔 `Sampling`、声音转换 `Sound`、图像显示 `ImageDisplay`、颜色转换 `ImageColor`、图像剖面 `ImageProfile`、曲线数字化与追踪 `Digitizer` |
| 时间序列（17） | 去趋势 `Detrending`、平滑 `Smoothing`、预白化 `Prewhitening`、全序列功率谱 `PowerSpectrum`、独立 `SWA`、演化谱 `EvolutionarySpectrum`、单序列小波 `Wavelet`、小波相干与交叉小波 `WaveletCoherence`、圆形谱 `CircularSpectrum`、相干与相位 `Coherence`、双谱 `Bispectrum`、谱矩 `SpectralMoments`、递归分析 `Recurrence`、先后关系 `LeadLag`、固定与动态滤波 `Filtering`、EMD/EEMD `EMD`、调幅 `Modulation` |
| 地层与年代（12） | 年龄模型构建 `BuildAgeModel`、深度–时间转换与调谐 `Tuning`、`Undatable`、地层对比 `StratCorrelation`、功率分解 `PowerDecomposition`、`DYNOT`、演化 Lag-1 `LagOne`、全段 COCO `Coco`、演化 eCOCO `EvolutionaryCoco`、全段 `TimeOpt`、演化 `EvolutionaryTimeOpt`、`Lyapunov` |
| 统计（4） | 描述统计 `SummaryStatistics`、假设检验 `HypothesisTests`、相关与协方差 `Association`、回归 `Regression` |
| 验证与诊断（1） | 验证数据、发表用实验和方法自测 `MethodValidation` |

目录覆盖 51 个分析模块、3 个数据模块、3 个展示模块，以及桌面、工作流和验证 5 项。全段与滑窗分析可以共用实现，输出对象的维度和含义仍各有入口。例如 COCO 的速率曲线与 eCOCO 的位置–速率矩阵。功率谱的 SWA 背景和独立 SWA 工作流也分别登记，后者还有 FDR、Bayesian probability 与自己的显示面板。菜单位置沿用 Li 的导航，源码归属另按操作和产物划分。[两版菜单可见性](../migration/master/menus.tsv)

### 覆盖与已有缺口

| 项目 | GUIDE 基线 | 3.1.1 |
| --- | ---: | ---: |
| 固定 Git 树中的 MATLAB 文件 | 246 | 337 |
| 另行标明来源的 MATLAB 文件 | 11 个恢复文件 | 1 个按调用启用的 COCO 兼容文件 |
| 文件内声明的函数和方法，含局部及嵌套声明 | 1,479 | 2,500 |
| 已有包 / 已有版本化公开角色 | 227 / 388 | 286 / 401 |
| 已标来源的照抄块出现次数 / 同版按来源和区间去重 | 710 / 684 | 425 / 398 |

两版主菜单共 135 个不同 tag，旧包名并集 297 个，789 条版本化角色均有归属。112 个非 MATLAB 路径按两棵 Git 树的并集登记，含 GUIDE 图窗、校准数据、二进制及文档。桌面、Mini-Robot 与验证工具都有维护位置，可直接组合分析角色或保留其原入口。声音转换已有返回波形和采样率的接口。[源文件](modules/sources.tsv) · [函数与回调](modules/declarations.tsv) · [资源](modules/assets.tsv) · [恢复文件来源](../migration/recovered.tsv)

总表的 `proposed_filenames` 是第一版逐项预留的名称；多个操作归到同一维护目录时，实际公开入口按操作契约确定。两个 `*_workflow_roles` 只列该版本中本组已有工作流入口所提供的角色，特定变体以角色表为准。`*_shared_declarations` 标明暂时只能共同归属的窗口声明，例如混合了全段和滑窗操作的 eCOCO 窗口。全库合计时每条声明只计一次。3.1.1 的独立 SWA 已有专门的 `helper`、`plotter`，对应 `analyzer` 仍待补齐。TimeOpt、演化 TimeOpt 和 Lyapunov 的基线角色及恢复来源继续单独登记。桌面转发能证明窗口可以打开，Harness 重放需要另行确认是否有入参齐全且能独立运行的角色。[角色与参数](modules/roles.tsv) · [逐菜单评审](MODULE_GROUPING.zh-CN.md)

## 选择属于每次调用的 params

| 现有入口 | 本次调用持久化的内容 | 维护位置 |
| --- | --- | --- |
| 插值 Pro | `method=1…9` 中选定的一项，以及 `data`、`dt`、`gap2zero`、`gapdt` | 插值模块维护旧编号与算法的对应关系。普通等距插值与参考坐标对齐保留各自的契约。 |
| Data Transform | `j` 取 16 个已实现的值之一，`checkid` 给出作用列。例如 `j=2` 使用 `edit1`、`edit2` 指定归一化区间。 | 变换模块维护旧编号及各分支所需字段。编号不连续。 |
| 功率谱 | `method` 决定三种谱估计器之一，另有六个可组合开关。例如基线的 `noise.powerlaw` 对应 3.1.1 的 `models.powerLaw`。 | 功率谱模块维护适用条件。F 检验是 MTM 的诊断，有效组合按版本处理。 |

模块维护“允许选什么、怎样解释旧值”所需的最小定义。原函数已经分派时，直接传值即可。GUI 需要展示选项时可读同一份定义。只有 Helper 可以补齐科学参数。Analyzer 只接受本次操作及其激活分支的完整合法入参，缺字段、非法值或触发底层缺省的空值应在计算前报错。原函数所需选项逐项传足。Plotter 接受确定的结果与显示参数。Registry 只需登记版本化操作及其入口。[上述选择的完整编号与字段对照](modules/selection_values.tsv)

`init.params` 引用本角色收到的入参。Helper 的 `fin.retval` 引用它给出的参数。GUI 修改后，Analyzer 的 `init.params` 引用实际提交的版本。Plotter 同样记录结果引用、面板、坐标和单位等可重建的配置。当前窗口或 axes 句柄由显示适配器在运行时传入。Logger 保持 `logger(id,attr,info)` 的约定，`fin` 使用 `status` 和 `retval`，状态为 `done`、`incomplete`、`cancelled`。私有函数掌握调用者无法得知的诊断时，可以向该次调用追加 `event`、`msg` 或 `error`。[现有调用记录实现](../matlab/+aclog/invoke.m)

## 存放、命名与去 GUI 耦合

| 源码情形 | 维护方式 |
| --- | --- |
| 已有独立函数，给足输入能得到所需结果 | 从原路径按原名直接调用，登记逻辑归属、上游提交和依赖。两个版本的签名或边界行为有差别时，按原操作标识绑定。 |
| 独立函数有默认值、画图或进度开关 | Helper 给齐参数，Analyzer 显式选择数值路径，核对下游实际副作用。例如 `ftestmtmML` 的 `plotn=0`、`minirhos0` 的 `genplot=0`、`smoothbestSpanRand` 的 `wtb=0` 在两个版本都有可用的关闭路径。 |
| 可执行脚本或 GUI 回调 | 将所读的工作区变量列为输入，将产生的数组列为返回值。单一调用点可并入所属函数，共用的代码由一个具名私有函数承接。照抄段保留 `%% Copied from …`、原提交、文件与行号。两版各有 33 个可执行独立脚本，路径集合相同。另外各有一个只含注释的 `doc/ac_acknowledgment.m`，按文档保留。 |
| 计算必须读控件、弹窗、等待进度条或打开图窗 | GUI 提供人选的点、文件或决策，实际选择进 `params`。计算过程的诊断、用户提示和错误通过 Logger 上报，图形进入 Plotter。保留原异常与部分结果的语义。如何显示日志留待 GUI 设计。只负责选点、菜单或刷新窗口的原函数可留在桌面侧。 |
| 依赖工作目录、文件、时钟或 base workspace | 核对隐式依赖，把影响重放的输入、输出位置或随机性显式化。暂用版本兼容适配时，记录来源和作用域。 |

`datapreproc` 会删除行、排序、归并、重采样，并用 `warndlg` 通知用户。处理后的数据和实际采取的动作都需要传出，单纯关闭提醒会丢掉解释。`smoothciML` 在第 35–42 行完成 Bootstrap 汇总，第 46、61 行无条件开图，这给出了计算与绘图的拆点。基线 `corrcoefslices_rank` 的 `plotn` 能控制结果图，Monte Carlo 分支仍然创建 `waitbar` 并读取 GUI 状态。[数据预处理](https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/datapreproc.m) · [Bootstrap 源码](https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/smoothciML.m#L35-L63) · [eCOCO 源码](https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/corrcoefslices_rank.m)

公开入口拟用 `code/interface/<维护组>/ac<操作>_<角色>.m`。例如 `acInterpolation_helper.m`、`acInterpolation_analyzer.m`、`acInterpolation_plotter.m`。新文件与主函数同名，新声明的名称在项目内唯一。需要抽出的内部实现集中在普通目录 `code/method/`。原有独立函数和第三方目录原位保留。注册操作和旧日志按版本绑定。原来的拟用名称仅供核对第一轮的源码归属，新的操作边界见逐项方案。[内部实现存放约定](../code/method/README.md) · [新版归并表](MODULE_CONSOLIDATION.zh-CN.md) · [目录与数值测试](tests/testModuleInventoryLayout.m)

## 建议归 Core 的通用函数

计数以两版上游源码及各自明确来源的补充文件为单位。同一模块的多个回调只算一个使用方。主窗口里可归属到具体菜单的调用记入对应模块。数据、展示和工作流可计入，纯桌面、工程验证、归属未明的混合 GUI 与单纯引用句柄不计入下表。“—”表示这一版没有此函数。[逐项使用方](modules/shared_functions.tsv) · [调用文件、作用域与行号](modules/shared_call_sites.tsv)

| 原函数 | GUIDE | 3.1.1 | 实际调用方与应保留的契约 |
| --- | ---: | ---: | --- |
| `findduplicate` | 9 | 12 | 年龄模型、相干、功率分解等。对重复坐标的每一数据列求均值，无重复时保留原行序。 |
| `select_interval` | 10 | 9 | COCO、相干、参考曲线等。按首列的闭区间选整行，保留其他列与行序。 |
| `interpolate` | 11 | 11 | 滤波、演化谱、递归分析等。旧两列等距线性插值，输入多列时也只返回坐标和第二列。 |
| `acycleInterpolateSeries` | — | 2 | 调幅、演化 Lag-1。严格多列等距线性插值，要求有限且严格递增的坐标，返回短尾与网格元数据。 |
| `acycleSamplingIsUneven` | — | 12 | EMD、滤波、递归分析、谱矩等。调用者可以指定相对容差，并取回判定和诊断。 |
| `zeropad2` | 9 | 6 | 演化谱、DYNOT、功率分解等。延拓模式、均值处理和随机状态影响结果，3.1.1 可指定半窗覆盖。 |
| `moveMedian` | 4 | 4 | 圆形谱、功率谱、预白化等。保留原版本的窗长、端点与方向行为。 |
| `rhoAR1ML` | 5 | 5 | COCO、Lag-1、预白化、小波等。逐列估计 Lag-1，另有独立的标量和小波套件估计方式。 |
| `ac_sort_dir_entries` | — | 26 | 文件 IO。相关调用用于桌面文件列表，函数本身只接收普通目录条目与排序模式。 |

建议先登记以上 8 个数值函数和 1 个 IO 函数的位置与版本。Core 可以承担维护责任，各模块继续使用原件。Core 的其他共用功能包括 Logger、引用值的读写、公共执行与回放、注册及通用入参校验。现有 `aclog.defaults` 被 60 个角色文件直接使用，`accompat.requireFields` 被 31 个直接使用。GUIDE 的 388 个角色调用 `aclog.invoke`，3.1.1 的 401 个经 `accompat.masterInvoke` 接入相同的记录约定。SWA 的工作区隔离、Taner 的 base-workspace 兼容和 COCO 的旧目标谱适配，各由领域模块维护。[平台代码归属及直接使用方](modules/platform_usage.tsv)

还有两类高频共用代码值得分别维护。功率谱和 SWA 共用 `acycleMtmTaperCount`，调谐和地层对比共用 `depthtotime`，COCO/eCOCO 共用目标谱与验证函数，它们可留在对应领域。文件列表格式处理 `strrep2`、刷新脚本 `refreshcolor`、工作目录脚本 `GETac_pwd` 和 `CDac_pwd` 由桌面及文件适配层承接。仅 `refreshcolor` 在两版就有 44 和 19 个模块涉及，输入仍来自 GUI 工作区。

`redmark` 是一个会影响重放的反例。它在函数内按系统时钟重设随机状态。基线的信号生成器和 Lyapunov 替代序列都调用它，只记录入口 RNG 无法复原这部分。可重放的调用路径须接收显式随机状态或保存实际噪声，旧实现仍按来源保留。[逐项取舍](modules/core_review.tsv) · [redmark 原实现](https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/redmark.m)

## 从清单到迁移

1. 在[模块总表](modules/modules.tsv)定位模块，按版本在[角色表](modules/roles.tsv)定位旧 `op`、入参、角色和原接口。工作流、专家原函数入口、桌面转发与版本独有操作都有各自的归属。旧 `+acmethods`、`+acmaster` 及已写入日志的 `op` 继续绑定原版本。
2. 在[源文件表](modules/sources.tsv)查源码归属、Git blob 或恢复文件哈希、脚本或函数、直接副作用和通向 GUI 的一条静态依赖路径。`retain-original-function` 可从原位置调用，`functionize-script` 进入脚本函数化队列，`detach-gui` 和 `check-plot-switch-or-split` 需要核对有效的关闭路径及需要上报的诊断。`retain-check-callee-side-effects` 提示调用者还可能经下游函数触发 GUI。目录与工作区、文件读写、时钟随机数、原生绘图及桌面适配另有标记。
3. 用[声明表](modules/declarations.tsv)定位大文件中的具体回调，从[照抄区间表](modules/copied_blocks.tsv)反查源区间、涉及的旧 `op` 及建议动作。两个版本共 1,082 个按版本去重的区间。同一段出现在多个接口时，先检查原函数能否完整满足契约，再决定是否提取单份实现。新私有函数登记逻辑所属模块、版本、原文件、源行与未来归档位置。以后物理归并时更新函数绑定，复用相同的操作标识与参数解释。
4. 每个开始归并的模块，用对应版本的数值、形状、端点、随机性、状态和关键绘图数据验收。交互预览也可使用同一组角色。[待人工确认的绑定](modules/binding_review.tsv)保留了动态调用、脚本变量和原生路径缺符号的行号。例如 3.1.1 的历史 COCO 入口对 `freq2target` 的依赖需要显式启用兼容路径。静态清单覆盖全部文件，运行验证仍需逐方法、逐科学分支开展。

维护用的输入是[模块与原名](modules/families.tsv)、[已有工作流入口](modules/workflow_entries.tsv)、[Core 取舍](modules/core_review.tsv)、[选项](modules/selection_values.tsv)和[平台职责](modules/platform.tsv)。在含两个 Git 子模块的检出目录运行以下命令，默认逐字核对生成的清单，加 `--write` 可重新生成。现有来源检查另外核对每一段 `%%` 与固定上游的逐行一致性。

```sh
python -m pip install miss-hit-core==0.9.44
python audit/tools/build_module_inventory.py
```
