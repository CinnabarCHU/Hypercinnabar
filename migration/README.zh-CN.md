# GUIDE 基线迁移说明

这一分支从 GUIDE 移除前的 `b52ea9f510f3be00bde9a0238b9898a1e2315b74` 取代码和科研图。可以从根目录运行 `setup_migration`，也可以单独导出一个方法。现有桌面应用继续走 Li 的 GUIDE 回调，新的 MATLAB、GUI 和 Harness 调用方可以直接使用 `acmethods.方法名.helper`、`analyzer` 和 `plotter`。[基线](https://github.com/mingsongli/acycle/tree/b52ea9f510f3be00bde9a0238b9898a1e2315b74) · [可执行示例](../README.md)

## 按菜单查找方法

[菜单表](menus.tsv) 的每一行对应 `AC.fig` 中一个有名称的菜单项。原图包含 17 个菜单标题、95 个科学或数据操作、18 个文件管理、窗口、剪贴板和帮助等桌面操作。95 项中，93 项已对接其主要计算或绘图路径，另两项的来源见下表。`method` 表示对应方法已有可调用入口。逐个菜单选项、组合参数和交互序列的验证范围请以测试代码为准。[方法和参数表](methods.tsv) · [33 个原始窗口的控件](controls/) · [279 个原始程序和图窗文件](baseline.tsv)

| 入口 | 可以直接做什么 | 来源和限制 |
| --- | --- | --- |
| TimeOpt / eTimeOpt | 获取各沉积速率的拟合、最优调谐序列、Monte Carlo 显著性和滑动窗口结果，并单独绘图 | 恢复公开历史的五个 TimeOpt 文件，全部与 2.7.1 的同路径文件逐字节一致。TimeOpt 把原对话框的选择作为 `mc_scope`，支持 `optimum`、`all`、`cancel`。 |
| Lyapunov | 单次滑窗估计、替代序列检验、随机窗口与采样率的模拟、百分位数和绘图 | 恢复同一上游提交中的五个 Lyapunov 文件。原相空间函数使用整数样本下标。单次或随机设置产生非整数延迟时，保留原函数报错，调用日志记录失败。 |
| 二元线性回归 | 返回截距、斜率与各自的 95% 区间、回归线及置信带、统计摘要和 ANOVA | 基线只有 `BivLinearRegUI` 的调用。采用官方 MATLAB 发行包 `code/test/BivLinearRegUI.m` 内的 `fitlm` 实现。该文件与后来的同名 `polyfit` 实现不同，尚无证据证明基线当时运行的确切副本。 |
| 图线数字化 | 手工像素点的线性 / 对数标定，或给出图像与种子后追踪曲线 | 手工公式来自 GUIDE。`DigitizeTrace` 支持外部原版 `getPKS(image,2)` 与 `trackline`。在本次核对的版本中二者缺失，随分支提供的 `ecocotrackn` 方案使用原图阈值、像素连通段的中点与 Li 的 eCOCO 追踪函数。它的轨迹可能与旧版不同，所选引擎随调用记录。 |
| COCO / eCOCO | 返回窗口逐沉积速率的相关、轨道数、模拟显著性和最优速率 | `nsim <= 1` 时只返回观测量，显著性字段为空且 `fin.status='incomplete'`。这修正了原回调在无模拟时索引空零分布的问题。 |
| Undatable | 以原始年代数据运行年龄–深度模型，用返回的绘图数据绘制模型、SAR 或输出 PDF | 输入文本字节和模型绘图所需变量进入快照。可在移走原输入后重放。指定非空 `writedir` 可以保留原格式输出。 |
| 天文解 / Insolation | La04、La10、ZB 系列与相应日照计算 | ZB17 的 11 份表和 Berger–Loutre 数据按下文安装。读取跨机器的外部数据仍需要对应数据文件。 |

TimeOpt 和 Lyapunov 在 GUIDE 移除前已从 Git 树删除。十个原文件按删除前的公开 Git 版本恢复。额外的回归候选采用发行包的完整文件作为核对依据。每份文件列有来源、成员路径和 SHA-256。2.7.1 参照包的版本文件日期为 2023-10-16，归档 SHA-256 为 `6155b4d57bddf6b3609e46e861900db933d45d559fb4efaebe8e7e3dfef6b4f9`。[删除提交](https://github.com/mingsongli/acycle/commit/79190165843a9530368bb9815c2c80a4aff46503) · [恢复源文件清单](recovered.tsv)

## 开发与复现

原计算函数能完整传参调用时，模块直接调用，并按原接口关闭内部绘图。原函数总会弹窗、写入工作区或将计算写进回调时，移植文件用 `%% Copied from` 和 `%% End copied source` 标出逐行照录的区段。科研输入与输出由参数结构体传递，交互选点使用坐标等显式数值。每个公开入口都可以单独记录和重放。[源码核对程序](check.py)

例如，`TimeOpt.helper(struct('dat',data))` 接受第一列为 cm 的两列数据并给出参数建议。可修改 `p.sedmin`、`p.sedmax`、`p.numsed` 或 `p.nsim` 后执行 `[r,id]=acmethods.TimeOpt.analyzer(p)`。返回的 `r.xx` 四列依次为沉积速率、包络拟合、功率拟合和二者乘积，`r.datopt` 是最优解的调谐序列。`p.result=r; acmethods.TimeOpt.plotter(p)` 可画科研图。`TimeOpt` 的原代码把一个相关计算分支注释为 Spearman，但实际调用的是未指定相关类型的 MATLAB `corr`；移植保留其实际计算。[历史内核](../upstream/recovered/code/package/timeOpt/timeOptAc.m) · [相关算法](../upstream/recovered/code/package/timeOpt/fitItls.m)

`logger(id,attr,info)` 既能独立调用，也由每个角色的函数入口使用。`init` 保存有版本的 `op` 和入参引用 `params`。正常结束、得到部分结果、无结果，分别使用 `fin.status` 的 `done`、`incomplete`、`cancelled`。`retval` 是返回值引用，无返回值则为空。例外将先写 `error` 后写 `fin`，然后把原异常抛给调用方。MATLAB 进程若遭强制终止，最后一条持久记录可能是 `init` 或中间记录。各条记录写入 JSONL，入参、结果和起始随机状态写入同目录的 MAT 文件。跨环境复现时需带上整个调用目录、同版本的方法和运行依赖。[记录入口](../matlab/logger.m) · [重放入口](../matlab/+aclog/replay.m)

导出命令 `python migration/export_method.py Bandpass TimeOpt Undatable --output ../acycle-methods` 会复制所选方法的原始角色文件及依赖，同时保留私有子目录、原始数据、计算函数和校验值。在输出目录运行 `setup_method` 即可调用。图形与数值方法可能需要 Signal Processing、Wavelet、Statistics and Machine Learning 等 MATLAB 工具箱。每个方法仅暴露有对应行为的角色。纯绘图入口或无参数建议的底层函数可在目录表中直接查到。[导出器](export_method.py) · [独立包测试](../tests/test_package_portability.m)

安装可选轨道数据可运行 `python -m pip install numpy scipy`，随后运行 `python migration/fetch_orbits.py /absolute/path/to/orbits`。在 MATLAB 中先执行 `setenv('ACYCLE_REFERENCE_DATA','/absolute/path/to/orbits')`，再执行 `setup_migration` 或 `setup_method`。下载器按 SHA-256 校验 Zeebe 原表与 NOAA `orbit91`，后者按原程序期望的变量名 `Orbit` 存入 MAT 文件。[下载程序](fetch_orbits.py) · [固定校验值](orbits.sha256)

从仓库根目录运行 `python migration/check.py --figures` 可逐行比较来源块并重读全部原始 `.fig`。MATLAB 测试同时覆盖实际参考数据、旧函数输出、带随机数的重放、绘图和拷出后的调用。静态控件清单包含 970 个序列化控件，动态创建的对话框及操作系统交互需要通过对应源码和运行测试检查。[MATLAB 测试](../tests/) · [GitHub Actions](../.github/workflows/guide-methods.yml)
