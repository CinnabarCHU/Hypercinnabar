# GUIDE 基线迁移说明

这一分支从 GUIDE 移除前的 `b52ea9f510f3be00bde9a0238b9898a1e2315b74` 取代码和科研图。可以从根目录运行 `setup_migration`，也可以单独导出一个方法。现有桌面应用继续走 Li 的 GUIDE 回调，新的 MATLAB、GUI 和 Harness 调用方可以直接使用 `acmethods.方法名.helper`、`analyzer` 和 `plotter`。[基线](https://github.com/mingsongli/acycle/tree/b52ea9f510f3be00bde9a0238b9898a1e2315b74) · [可执行示例](../README.md)

## 按菜单查找方法

[菜单表](menus.tsv) 的每一行对应 `AC.fig` 中一个有名称的菜单项。原图包含 17 个菜单标题、95 个科学或数据操作、18 个文件管理、窗口、剪贴板和帮助等桌面操作。95 项中，93 项已对接其主要计算或绘图路径，另两项的来源见下表。`method` 表示对应方法已有可调用入口。逐个菜单选项、组合参数和交互序列的验证范围请以测试代码为准。[方法和参数表](methods.tsv) · [33 个原始窗口的控件](controls/) · [279 个原始程序和图窗文件](baseline.tsv)

| 入口 | 可以直接做什么 | 来源和限制 |
| --- | --- | --- |
| TimeOpt / eTimeOpt | 获取各沉积速率的拟合、最优调谐序列、Monte Carlo 显著性和滑动窗口结果，并单独绘图 | 恢复公开历史的五个 TimeOpt 文件，全部与 2.7.1 的同路径文件逐字节一致。TimeOpt 把原对话框的选择作为 `mc_scope`，支持 `optimum`、`all`、`cancel`。 |
| Lyapunov | 单次滑窗估计、替代序列检验、随机窗口与采样率的模拟、百分位数和绘图 | 恢复同一上游提交中的五个 Lyapunov 文件。原相空间函数使用整数样本下标。单次或随机设置产生非整数延迟时，保留原函数报错，调用日志记录失败。 |
| 二元线性回归 | 返回截距、斜率与各自的 95% 区间、回归线及置信带、统计摘要和 ANOVA | 基线只有 `BivLinearRegUI` 的调用。采用官方 MATLAB 发行包 `code/test/BivLinearRegUI.m` 内的 `fitlm` 实现。该文件与后来的同名 `polyfit` 实现不同，尚无证据证明基线当时运行的确切副本。 |
| 图线数字化 | 手工像素点的线性 / 对数标定，或给出图像与种子后追踪曲线 | 手工公式来自 GUIDE。原图窗禁用 Auto-digitize。新分析使用 [3.1.1 追踪入口](master/README.zh-CN.md#自动追踪示例)。旧日志继续使用记录的外部 `getPKS(image,2)` / `trackline` 或本分支的 `ecocotrackn` 替代算法。 |
| COCO / eCOCO | 返回窗口逐沉积速率的相关、轨道数、模拟显著性和最优速率 | `nsim <= 1` 时只返回观测量，显著性字段为空且 `fin.status='incomplete'`。这修正了原回调在无模拟时索引空零分布的问题。 |
| Undatable | 以原始年代数据运行年龄–深度模型，用返回的绘图数据绘制模型、SAR 或输出 PDF | 输入文本字节和模型绘图所需变量进入快照。可在移走原输入后重放。指定非空 `writedir` 可以保留原格式输出。 |
| 天文解 / Insolation | La04、La10、ZB 系列与相应日照计算 | ZB17 的 11 份表和 Berger–Loutre 数据按下文安装。读取跨机器的外部数据仍需要对应数据文件。 |

TimeOpt 和 Lyapunov 在 GUIDE 移除前已从 Git 树删除。十个原文件按删除前的公开 Git 版本恢复。额外的回归候选采用发行包的完整文件作为核对依据。每份文件列有来源、成员路径和 SHA-256。2.7.1 参照包的版本文件日期为 2023-10-16，归档 SHA-256 为 `6155b4d57bddf6b3609e46e861900db933d45d559fb4efaebe8e7e3dfef6b4f9`。[删除提交](https://github.com/mingsongli/acycle/commit/79190165843a9530368bb9815c2c80a4aff46503) · [恢复源文件清单](recovered.tsv)

## v2.8 与 v3.0.3 的发布包核对

两个 GitHub Release 各提供同一份源码的 ZIP 和 tar.gz。GitHub Release API 在两版均返回 `assets: []`，发布者未另传安装包。实际下载的 v2.8 ZIP 有 345 个文件（234 个 `.m`），v3.0.3 ZIP 有 402 个文件（316 个 `.m`）。去掉归档根目录后，已逐文件核对内容与各自标签的 Git blob，并在所有 MATLAB 源文件中检查了函数定义与调用。[v2.8 · e3553eb](https://github.com/mingsongli/acycle/releases/tag/v2.8) · [v3.0.3 · 8eea944](https://github.com/mingsongli/acycle/releases/tag/v3.0.3)

| 待查代码 | v2.8 | v3.0.3 | 对迁移的意义 |
| --- | --- | --- | --- |
| TimeOpt / eTimeOpt | `code/package/timeOpt/` 内的 `timeOptAc.m`、`timeOptSimAc.m`、`eTimeOpt.m`、`fitItls.m`、`harm1ML.m` 齐全 | 五个文件均缺 | 五个原件与本分支从 `f4027a8` 补回的文件逐字节相同。[v2.8 源码](https://github.com/mingsongli/acycle/tree/e3553eb00b4890c0071ef64b213df34db5670de5/code/package/timeOpt) |
| 旧图线追踪 | `DataExtractML.m` 与 GUIDE 基线逐字节相同。第 781 行调用 `getPKS(Ig01,2)`，第 810 行调用四参数 `trackline`。标签只提供单参数序列求峰函数 `getpks(data)` | 仍只提供单参数 `getpks`。新窗口用 `traceSeedCurve` 从种子连通分量追踪，其 `plotdigitizer.m` 与固定的 3.1.1 master 字节相同 | 两个标签中均未找到旧图像函数定义。保留外接旧引擎、标明来源的替代引擎，以及独立的新版追踪入口。[旧调用](https://github.com/mingsongli/acycle/blob/e3553eb00b4890c0071ef64b213df34db5670de5/code/guicode/DataExtractML.m#L781-L810) · [单参数函数](https://github.com/mingsongli/acycle/blob/e3553eb00b4890c0071ef64b213df34db5670de5/code/seriesanalysis/getpks.m#L1) · [新版追踪](https://github.com/mingsongli/acycle/blob/8eea94423759e872a353b6a67987a58ccb0cddf8/code/guicode/plotdigitizer.m#L615-L642) |
| 线性回归 `BivLinearRegUI` | 无该函数或调用 | `code/package/univariate/BivLinearRegUI.m` 对有限数据用 `polyfit(x,y,1)` 拟合；整个文件与固定的 3.1.1 master 字节相同 | 能确定新版回归的来源。GUIDE 基线的 `AC.m` 只有调用；采用的 `fitlm` 副本出自 3.1.1 MATLAB 发行包的 `code/test/`，两个标签都无法确认基线部署时用的是哪一份。[v3.0.3 回归](https://github.com/mingsongli/acycle/blob/8eea94423759e872a353b6a67987a58ccb0cddf8/code/package/univariate/BivLinearRegUI.m#L14-L44) · [发行包原件与哈希](recovered.tsv) |
| Lyapunov | 未收录补回的五个内核 | 仍保留两处对 `lyapunov_timeseries` 的调用，未收录这五个内核 | 原件可从两个标签之间的 2025 年提交 `f4027a8` 获取。[五个原文件](https://github.com/mingsongli/acycle/tree/f4027a865e22cf64500e7145aef592b944df3f98/code/package/lyapunov) · [v3.0.3 的调用](https://github.com/mingsongli/acycle/blob/8eea94423759e872a353b6a67987a58ccb0cddf8/code/guicode/AC.m#L10930) |
| 从 master 消失的四个旧函数 | 四参数 `freq2target.m`、`cyclecorrsig.m`、`period2spectrumB.m` 与 GUIDE 基线逐字节相同。`corrcoefslices_rank.m` 也在，但文件内容有差异 | 这四个旧文件名均已消失 | 旧 COCO 兼容入口继续用 GUIDE 基线的 `freq2target`；v2.8 提供了可交叉验证的原件。[四参数实现](https://github.com/mingsongli/acycle/blob/e3553eb00b4890c0071ef64b213df34db5670de5/code/corrcoef/freq2target.m) · [兼容选项](master/README.zh-CN.md) |

v2.8 标签内的 `code/bin/ac_version.txt` 仍写作 `2.7.1`，`ac_date.txt` 为 `20231016`。与提供的 `code.zip` 比较，过滤系统元数据后，两套 `code/` 都有相同的 307 个文件路径，其中 304 个文件字节相同。231 个 MATLAB 文件中，唯一的差异位于 `code/package/swa/specswa.m` 的一行，v2.8 把 `revmin == 0` 改成 `revmin <= rev1 && revmin <= rev2`。另外两个差异文件是 `ac_lang.txt` 与 `ac_pwd.txt`。因此这份旧包也能佐证 TimeOpt 和旧数字化调用的来源。[版本标记](https://github.com/mingsongli/acycle/blob/e3553eb00b4890c0071ef64b213df34db5670de5/code/bin/ac_version.txt) · [SWA 条件](https://github.com/mingsongli/acycle/blob/e3553eb00b4890c0071ef64b213df34db5670de5/code/package/swa/specswa.m#L159)

## 旧数字化器的自动追踪

2019 年 2 月 18 日，v0.3.2 首次加入 Plot Digitizer。第一次提交的 `DataExtractML.m` 已调用双参数 `getPKS(Ig01,2)` 和四参数 `trackline`，而同一提交的 `DataExtractML.fig` 已将 `push_auto` 设为 `Enable='off'`。公开历史里这个图窗共有四份不同的 Git blob，四份中的 Auto-digitize 都可见但禁用。v2.8 用户手册第 50–51 页展示了灰色按钮，操作步骤是四点校准后点 Digitize 手工取点。由此可以确认旧回调缺少依赖；公开材料没有显示曾有正式启用的 GUIDE 自动追踪。[首次加入时的回调](https://github.com/mingsongli/acycle/blob/38fda849ff5df5de514c9987a0a8687d95f67446/code/guicode/DataExtractML.m#L525-L565) · [原始图窗](https://github.com/mingsongli/acycle/blob/38fda849ff5df5de514c9987a0a8687d95f67446/code/guicode/DataExtractML.fig) · [GUIDE 基线控件](controls/DataExtractML.tsv#L22) · [手册](https://acycle.org/docs/Acycle_Users_Guide.pdf)

| 核对范围（2026-11-23） | 结果 |
| --- | --- |
| 两条公开分支与全部 24 个标签可达的 482 个提交，含 v2.8 以前的 9 个 GitHub Release | 检索了 1,970 份内容各异的 MATLAB 源码及编辑器备份（`.m`、`.asv`）。只找到单参数序列求峰函数 `getpks(data)`，`trackline` 只在 `DataExtractML.m` 中被调用。[上游标签](https://github.com/mingsongli/acycle/tags) · [Release 列表](https://github.com/mingsongli/acycle/releases) |
| 仓库内嵌 v0.2.0 MATLAB ZIP，及官方历史下载目录中的 v0.3.1、v0.3.3、1.0 MATLAB ZIP | 前两个包尚无这套数字化器。后两个包有相同的调用和禁用按钮，四个包均无所需函数定义。[v0.2.0 ZIP](https://github.com/mingsongli/acycle/blob/6b60951411091cc3e2d3b89b775f24afa41a17f5/acycle_v0.2.0/Acyclev0.2.0.zip) · [v0.3.3 MATLAB ZIP](https://www.dropbox.com/scl/fo/050pwjk3lvtblg8wzyucs/AG_rtvp73L2ZfVLlyPzJYKo/old%20versions/Acycle0.3.3-MatLab.zip?rlkey=ts8ibtwv3ozln18iympq6w2sq&dl=0) · [1.0 MATLAB ZIP](https://www.dropbox.com/scl/fo/050pwjk3lvtblg8wzyucs/AEwlw8AphqlFuQaOav_S01k/old%20versions/Acycle1.0-Matlab.zip?rlkey=ts8ibtwv3ozln18iympq6w2sq&dl=0) |
| 23 个公开 issue（22 开、1 关）、9 个 PR，及两者合计 23 条讨论评论 | 未找到针对这两个函数或旧自动追踪的报错。#32 有人提到函数签名问题，该 issue 给出的调用栈是小波分析的 `chisquare_inv → fmin`。[上游 issues](https://github.com/mingsongli/acycle/issues?q=is%3Aissue) · [#32 的评论](https://github.com/mingsongli/acycle/issues/32#issuecomment-2676838106) |

新分析使用 3.1.1 的 `acmaster.DigitizeTrace`。可启用的 Auto-digitize 和 `traceSeedCurve` 可以追到 2026 年 2 月的 GUI 改写。GUIDE 的手工标定及已有 `acmethods.DigitizeTrace` 记录沿用原有入口，重放时保留日志中的引擎。[新版按钮和回调](https://github.com/mingsongli/acycle/blob/03a1f80d0bea2ebc765112d1964a33901045c40c/code/guicode/plotdigitizer.m#L178-L186) · [3.1.1 导出与调用示例](master/README.zh-CN.md#自动追踪示例)

同一轮向前追查也核对了回归窗口。旧 Release 中没有 `BivLinearRegUI.m`；该路径在公开 Git 历史中首次加入时已经使用 `polyfit`。GUIDE 基线的 `fitlm` 候选来源仍见上表。[首次公开的回归实现](https://github.com/mingsongli/acycle/blob/389a741f26d15de7aea1484624b52c878510f26a/code/package/univariate/BivLinearRegUI.m#L14-L24)

## 开发与复现

原计算函数能完整传参调用时，模块直接调用，并按原接口关闭内部绘图。原函数总会弹窗、写入工作区或将计算写进回调时，移植文件用 `%% Copied from` 和 `%% End copied source` 标出逐行照录的区段。科研输入与输出由参数结构体传递，交互选点使用坐标等显式数值。每个公开入口都可以单独记录和重放。[源码核对程序](check.py)

例如，`TimeOpt.helper(struct('dat',data))` 接受第一列为 cm 的两列数据并给出参数建议。可修改 `p.sedmin`、`p.sedmax`、`p.numsed` 或 `p.nsim` 后执行 `[r,id]=acmethods.TimeOpt.analyzer(p)`。返回的 `r.xx` 四列依次为沉积速率、包络拟合、功率拟合和二者乘积，`r.datopt` 是最优解的调谐序列。`p.result=r; acmethods.TimeOpt.plotter(p)` 可画科研图。`TimeOpt` 的原代码把一个相关计算分支注释为 Spearman，但实际调用的是未指定相关类型的 MATLAB `corr`；移植保留其实际计算。[历史内核](../upstream/recovered/code/package/timeOpt/timeOptAc.m) · [相关算法](../upstream/recovered/code/package/timeOpt/fitItls.m)

`logger(id,attr,info)` 既能独立调用，也由每个角色的函数入口使用。`init` 保存有版本的 `op` 和入参引用 `params`。正常结束、得到部分结果、无结果，分别使用 `fin.status` 的 `done`、`incomplete`、`cancelled`。`retval` 是返回值引用，无返回值则为空。例外将先写 `error` 后写 `fin`，然后把原异常抛给调用方。MATLAB 进程若遭强制终止，最后一条持久记录可能是 `init` 或中间记录。各条记录写入 JSONL，入参、结果和起始随机状态写入同目录的 MAT 文件。跨环境复现时需带上整个调用目录、同版本的方法和运行依赖。[记录入口](../matlab/logger.m) · [重放入口](../matlab/+aclog/replay.m)

导出命令 `python migration/export_method.py Bandpass TimeOpt Undatable --output ../acycle-methods` 会复制所选方法的原始角色文件及依赖，同时保留私有子目录、原始数据、计算函数和校验值。在输出目录运行 `setup_method` 即可调用。图形与数值方法可能需要 Signal Processing、Wavelet、Statistics and Machine Learning 等 MATLAB 工具箱。每个方法仅暴露有对应行为的角色。纯绘图入口或无参数建议的底层函数可在目录表中直接查到。[导出器](export_method.py) · [独立包测试](../tests/test_package_portability.m)

安装可选轨道数据可运行 `python -m pip install numpy scipy`，随后运行 `python migration/fetch_orbits.py /absolute/path/to/orbits`。在 MATLAB 中先执行 `setenv('ACYCLE_REFERENCE_DATA','/absolute/path/to/orbits')`，再执行 `setup_migration` 或 `setup_method`。下载器按 SHA-256 校验 Zeebe 原表与 NOAA `orbit91`，后者按原程序期望的变量名 `Orbit` 存入 MAT 文件。[下载程序](fetch_orbits.py) · [固定校验值](orbits.sha256)

从仓库根目录运行 `python migration/check.py --figures` 可逐行比较来源块并重读全部原始 `.fig`。MATLAB 测试同时覆盖实际参考数据、旧函数输出、带随机数的重放、绘图和拷出后的调用。静态控件清单包含 970 个序列化控件，动态创建的对话框及操作系统交互需要通过对应源码和运行测试检查。[MATLAB 测试](../tests/) · [GitHub Actions](../.github/workflows/guide-methods.yml)
