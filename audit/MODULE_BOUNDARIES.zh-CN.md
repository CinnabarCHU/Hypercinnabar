# 从 95 个菜单、286 个兼容包到 62 项源码归属

这三个单位分别回答三个问题：用户在主窗口能点什么、迁移分支保存了哪些 MATLAB 调用契约、每段源码由谁维护。公开方法的粒度还可以继续合并。为便于复核，现有两张交叉表分别以**菜单 tag** 和**包名**为主键。[菜单与归属](modules/menu_to_modules.tsv) · [两版包名、角色与归属](modules/package_to_modules.tsv)

## 数字如何对上

| 计数 | 统计单位与范围 |
| --- | --- |
| 130 → 95 | 固定 GUIDE 基线 `b52ea9f` 的主窗口 `AC.fig` 有 130 个具名菜单项。去掉 17 个标题和 18 项桌面操作，剩下 95 个可见的科学或数据入口，包括示例、绘图等。其迁移标记为 93 项 `method`、曲线数字化 1 项 `alternative`、线性回归 1 项 `archival`。 |
| 95 → 125 → 227 | 这 95 行的 `packages` 列合起来列出 125 个不同的 GUIDE 包名。基线的 `+acmethods` 总共有 227 个包。另 102 个包也在基线迁移中可调用，所属名称没有出现在这 95 行的显式关联列。菜单表描述入口和主要实现，`packages` 列不代表完整的传递调用图。 |
| 227 → 286 | 此处切换到 `dcba427`（3.1.1）的迁移命名空间 `+acmaster`。216 个包名在两版均有，11 个仅在 GUIDE 封装有，70 个仅在 3.1.1 封装有。故 `227 − 11 + 70 = 286`，两版并集为 297 个名字。同名的两个包仍各自绑定自己的版本。 |
| 286 个包 / 401 个角色 | 包按目录名去重，`helper.m`、`analyzer.m`、`plotter.m` 分别算角色。旧封装保存了 GUI 功能、独立原函数、产物输出以及验证程序等不同层次的入口。3.1.1 上游本身未如此划分。 |
| 95 → 56 → 62 | 依照固定的 tag 对应关系，这 95 个菜单命中 56 个归属。再加入 3.1.1 新的双谱、基线主窗口科学菜单之外的导航、工作区、设置帮助、Mini-Robot，以及工程验证，共 62 项。全段与演化 COCO 共用一个菜单，三种插值菜单则归到同一项。 |
| 286 → 57 → 62 | 从包名出发，3.1.1 的 286 个包覆盖 57 项。其余五项是 `SettingsHelp`、`Robot`、`TimeOpt`、`EvolutionaryTimeOpt`、`Lyapunov`。前两项有程序或 GUI 源码，尚无专门的 3.1.1 迁移包。后三项保留 GUIDE 版本的能力，其菜单已从 3.1.1 布局撤下。 |

3.1.1 的 286 个包可进一步按迁移用途点清。这是按每个包的实际角色汇总，同一个版本中，以下四类在这份快照恰好互斥。比例或类别名都不能替代科学方法计数。[按包查](modules/package_to_modules.tsv) · [按每个版本化角色查](modules/roles.tsv)

| 角色所在的包 | 包数 | 角色文件数 | 例子 |
| --- | ---: | ---: | --- |
| 功能工作流入口 | 118 | 199 | `PowerSpectrum`、`RegularInterpolation`，以及桌面转发器 `Desktop` |
| 专家与底层函数兼容入口 | 157 | 191 | `ftestmtm`、`mtmdofs`、`minirhos0` 等，上游原本就可作为函数调用 |
| 验证与研究实验 | 9 | 9 | 六个 COCO/eCOCO 工具、三个双谱验证工具 |
| 成果输出 | 2 | 2 | `BispectralExport`、`EvolutionaryWorkbook` |

例如基线菜单 `menu_power` 是一个功率谱入口。3.1.1 的 `PowerSpectrum` 归属共 14 个包，为 3 个工作流包和 11 个底层包；它们在 GUI 中并非 14 种可选算法。基线 `menu_interp`、`menu_interpolationGUI`、`menu_interpseries` 是三个独立入口，归入同一 `Interpolation` 家族。3.1.1 的 `Interpolation` 下登记五个包，四个工作流包和一个 `interpolate_rand` 底层包。`menu_ecoco` 则横跨两个不同产物，全段速率曲线和滑窗的位置–速率矩阵。上述归属描述维护责任，用户仍可按旧操作标识重放原行为。[旧菜单原始关联](../migration/menus.tsv) · [3.1.1 名称与实现形式](../migration/master/methods.tsv)

## 正式 analyzer 的入参约定

**只有 `helper` 可以提出或补齐科学参数的缺省值。** `analyzer` 必须先验证本次操作的完整输入，包括选择器、开关及其激活分支的数值参数。缺字段、非法值，或传空会触发原函数重新选择缺省值，都应在开始计算前报错。关闭的模型以显式 `false` 表示。对本分支无意义的字段可按契约省略；若 `[]` 是一个有明确算法含义的值，则记录这个值。执行中按已给数据计算采样步长、估计系数，或按数学定义使用常数，属于算法。Logger 的调用 ID 属于执行记录。直接调用与经过 GUI、CLI 的调用均遵循同一科学入参契约。

有两个可对照的历史入口。3.1.1 的 `RegularInterpolation.helper` 提供 `MaximumPoints` 和 `MaximumElements`，其 `analyzer` 对两项逐一检查并显式传给原函数。GUIDE 的 `PowerSpectrum-v1.0/analyzer` 则在 `noise` 缺失时跳过背景模型，现有回归样例也用这种省略方式。这是一个确切的待迁移点。归并后的公开功率谱接口应要求所有模型开关，缺失立即报错。旧日志须按记录的版本解释，不能据此为新运行补参。旧包的回归通过只验证其旧行为。可用删掉激活分支的一个字段来验收新的接口，同时检查 Logger 收到错误。[3.1.1 插值 Helper](../matlab/+acmaster/+RegularInterpolation/helper.m) · [3.1.1 插值 Analyzer](../matlab/+acmaster/+RegularInterpolation/analyzer.m) · [GUIDE 功率谱](../matlab/+acmethods/+PowerSpectrum/analyzer.m#L60) · [历史用例](../tests/test_scientific_methods.m#L30)

## 建议的维护边界

下表是对 62 项归属的修订建议。每个旧入口、回调或可重放的操作标识可以继续追踪。多项放入一个维护目录时，仍可保留原函数、方法入口和有意义的不同返回类型。只有共享输入和产物的分支才适合用同一个 `analyzer` 依 `params` 分派。

| 旧清单中的范围 | 建议的维护方式 |
| --- | --- |
| 桌面与工作区 | 菜单、窗口、剪贴板、文件选择器、当前选中数据、设置与帮助界面归 GUI。普通路径的读写、数据或文件引用的快照、目录记录排序归 Core 的 IO。Mini-Robot 的步骤、顺序、显式参数和产物依赖归工作流执行，窗口是 GUI 适配器。桌面和工作流的归属应在维护名册出现，无须占用科学方法名额。 |
| 天文解、日照量、轨道周期 | 建议一个“天文”维护目录，下面保留三个可独立调用的操作。共用的轨道资源可以登记一次，方法各自声明实际所用资源、模型、时间单位及版本。 |
| 序列与数学 | 旧表十项里，排序去重、列处理、区间裁剪与修峰、序列间运算、数值变换、导数、极值七项可归入“基础序列运算”。插值保留专门入口，管理常规、Pro、对齐参考坐标三种契约。变点归时间序列，PCA 归统计。“采样间隔”也应回到序列诊断。 |
| 统计 | 一个“统计”维护目录可以涵盖描述统计、假设检验、相关与协方差、回归，并接纳 PCA。简单操作可在薄入口中分派。检验结果、回归模型与诊断、PCA 得分与载荷保留各自明确的输出，拟合参数或置信度只由对应方法的 Helper 推荐。 |
| 图像与展示 | 序列绘图、Show Image 和原先的 Data Distribution 是展示入口，可直接使用 Plotter。原分布图调用 `histfit` 并展示摘要，未来若要向下游提供密度或计数，再将相应数值结果登记到统计。RGB 转灰度或 Lab 能返回像素矩阵，适合 Analyzer。图像剖面、数字化和追踪的选点交 GUI，显式坐标、种子和校准送 Analyzer，叠图交 Plotter。声音转换返回波形和采样率，播放交前端，导出交 IO。 |
| 工程验证 | 方法自测随其方法或测试目录维护，数据案例和发表实验可作为可重放工作流维护。研究用的脚本入口与结果继续保留。 |

天文三个操作可以用输入和产物直接辨认。`AstronomicalSolution` 按解、分量和时段读取 La04、La10 或 ZB 等轨道序列。`Insolation` 还需要纬度、日序和辐照模式等输入，其数值内核 `insoML` 读取所选解并计算辐照量，可返回时间序列或网格。`MilankovitchCal(age)` 使用 Waltham 模型给出地质年龄对应的日长和轨道周期范围。3.1.1 的 `calculate_orbit9(ageMa)` 则读取 `AstroGeo22.txt` 与 `La04gisi.csv`，返回九组频率和周期，供 eCOCO 与 DYNOT 生成目标。公开方法之间可以共享天文数据，周期计算没有必要先生成一条日照序列。[天文解入口](../matlab/+acmethods/+AstronomicalSolution/analyzer.m) · [日照入口](../matlab/+acmethods/+Insolation/analyzer.m) · [Waltham 实现](https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/MilankovitchCal.m) · [九个轨道频率](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/secular_periods/calculate_orbit9.m)

## 九个验证工具何时加入

下列是从固定 3.1.1 快照向前逐文件执行 `git log --follow --diff-filter=A` 找到的**上游首次加入日期**。GUIDE 基线为 2026-02-15。后来的 Hypercinnabar 兼容包装有单独的提交历史。

| 日期及上游提交 | 首次加入的文件 | 原来的研究用途 |
| --- | --- | --- |
| 2026-07-17 · [b95b8e3](https://github.com/mingsongli/acycle/commit/b95b8e33fe1ff6994ef023b297461e4a2653fb9c) | `runCocoEightMethodExperiment`、`runEcocoTwoMethodExperiment`、`runCocoPublicationValidation`、`validateCocoPublicationValidation` | 比较 COCO 目标构造方法，按预先指定的数据案例运行 COCO/eCOCO，复核已保存的统计结果。 |
| 2026-07-25 · [083c949](https://github.com/mingsongli/acycle/commit/083c949e5635fefb6a2227273c49329a0891147a) | `runInterleavedCvCocoComparison`、`runSyn3FourMethodPublicationStudy` | 在七个记录上运行交错交叉验证比较和研究指定的四方法对比。这一提交标为 v3.0。 |
| 2026-08-03 · [b7edf64](https://github.com/mingsongli/acycle/commit/b7edf64952d7a490dae252c102c631c113047733) | `bispectralSelfTest`、`bispectralValidateExamples`、`bispectralLocalDataValidation` | 双谱工具的确定性回归测试、五组示例验证，以及 LR04/CENOGRID 的数据验证。同期加入了用户可调用的双谱分析。 |

这九个原函数分别位于 `code/corrcoef/` 和 `code/package/bispectral/`，能在 GUI 以外独立调用。`MethodValidation` 是本次审计的归属名，主窗口没有这九项独立菜单。2026-11-23，迁移分支为它们保留了版本化入口，因此它们被计入 286 个包。[迁移提交](https://github.com/CinnabarCHU/Hypercinnabar/commit/d48e4cea93d824220998232198404c5bc1798d2a) · [上游 COCO 批量运行器](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/runCocoPublicationValidation.m) · [上游双谱验证](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralLocalDataValidation.m)

## 初版可以沿用 Acycle 的目录枚举

GUIDE 基线在 `ac.m` 的第 74 行调用 `addpath(genpath(path_root))`，3.1.1 在第 85 行做相同操作。MATLAB 的 `genpath` 自动略过名为 `private` 的目录；我们另外试了手写目录列表、对这个目录本身调用 `addpath` 的情形。对照使用同一棵临时目录，从 `code/interface/Interpolation/` 中的普通函数按名调用一份新实现。[GUIDE 启动代码](https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/ac.m#L74) · [3.1.1 启动代码](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/ac.m#L85) · [MathWorks 对 genpath 的定义](https://www.mathworks.com/help/matlab/ref/genpath.html)

| 搜索方式 | MATLAB R2024b Update 10 | Octave 10.3.0 |
| --- | --- | --- |
| `genpath(code)` 加入普通 `code/acprivate/` 和接口子目录 | 接口能直接调用 | 接口能直接调用 |
| `genpath(code)` 加入字面名 `code/private/` | 该目录被跳过 | 该目录被跳过 |
| 显式 `addpath(privateDir)` 后由接口按名调用 | 警告 `MATLAB:mpath:privateDirectoriesNotAllowedOnPath`，目录未加入，随后报 `MATLAB:UndefinedFunction` | 目录加入，接口能调用 |
| 由 `code/` 中的函数取得私有函数句柄，再由接口调用 | 能调用 | 能调用 |

**初版建议选普通目录 `code/acprivate/`**，集中放新拆出的内部实现。启动时枚举当前选用版本的 `code/` 一次即可，接口可以直接按全项目唯一名称调用。内部函数在搜索路径上普通可见，是否属于稳定公开 API 由接口目录与登记清单界定。若目录名必须严格为 `code/private/`，父目录句柄方式仍能保留 MATLAB 原生的私有可见性。两份快照有同名不同实现，枚举应限定到本次所选版本；当前迁移分支已有按版本临时切换和还原路径的代码。[实际目录测试](tests/testModuleInventoryLayout.m) · [MATLAB 原生运行日志](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45088757933/job/137413266416) · [原有版本路径隔离](../matlab/+accompat/masterPath.m)
