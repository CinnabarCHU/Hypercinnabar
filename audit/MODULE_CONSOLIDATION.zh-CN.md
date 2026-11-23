# Acycle 逐项归并方案

按原始菜单与源码归属顺序列出 62 项。下表的 89 行是可独立维护的操作、视图、桌面功能或工程任务。第一列会因拆分而重复。第二列给出 48 个维护组及各组的建议操作名，同组可以有多个公开入口。角色列描述拟议接口；已发布的版本化入口按原名留存。

完整对账覆盖 135 个菜单 tag 和 297 个旧包名。每个包可按 GUIDE 和 3.1.1 两栏查询其实际角色，合计 789 条版本化记录。菜单映射表示窗口所能配置的功能，专家包映射表示维护去向；两者都不改写旧日志的调用目标。Mini-Robot 的按钮调用单独从源码核实。

[按菜单或包名查去向](modules/consolidation_index.tsv) · [每条旧操作、角色及源码行号](modules/roles.tsv) · [接口评审、重点分组与验收](METHOD_ROLE_REVIEW.zh-CN.md) · [逐行编辑的方案](modules/consolidation.tsv)

H、A、P 分别表示 `helper`、`analyzer`、`plotter`。横线表示由 GUI、Core、IO 或工作流自身提供入口，或由资源目录按内容分派。已有图件可以复用另一操作的 plotter。标出的新角色要逐操作验收后才能使用。

## 桌面与工作区

| 原源码归属 | 新维护组与操作 | 类别 | 角色 | 归并依据及应保留的行为 |
| --- | --- | --- | --- | --- |
| `Desktop` | 桌面 · `DesktopNavigation` | GUI | — | 菜单、窗口、焦点和命令转发归 GUI。旧 Desktop 启动入口仍可回放相应桌面行为。 |
| `Workspace` | 工作区 · `WorkspaceUI` | GUI | — | 打开、剪贴板、当前选中项、表格与刷新由桌面管理；取得文件引用后再调用 IO。 |
| `Workspace` | 工作区 · `WorkspaceIO` | Core | — | 无界面的目录排序、路径和输入快照可共享；保留 ac_sort_dir_entries 和 strrep2 兼容入口。 |
| `SettingsHelp` | 桌面 · `SettingsHelpUI` | GUI | — | 设置、语言、帮助、手册与更新各保留原动作；只有脱离窗口的偏好读写才归 Core。 |
| `Robot` | 工作流 · `MiniRobotWorkflow` | 工作流 | — | 保留 Mini-Robot 的固定步骤、跨步参数、输出与历史重试。主窗多选后逐文件打开 RobotGUI，每窗处理一条序列；执行器调已有方法。 |

## 数据与天文

| 原源码归属 | 新维护组与操作 | 类别 | 角色 | 归并依据及应保留的行为 |
| --- | --- | --- | --- | --- |
| `SeriesGenerator` | 序列生成 · `SeriesGenerator` | 科学计算 | H · A · P | 确定性信号与随机噪声共享时间轴和合成序列输出；记录分量和随机状态，redmark 原位复用。 |
| `Insolation` | 天文 · `Insolation` | 科学计算 | H · A · P | 纬度、日序、轨道解确定辐照量；序列与网格保留坐标。纬度–日序动画为结果视图及导出。 |
| `OrbitSolution` | 天文 · `OrbitSolution` | 数据 | H · A · P | 按解、分量和时段取轨道参数与时间轴，可直接供日照或后续分析使用。 |
| `OrbitalPeriods` | 天文 · `OrbitalPeriods` | 科学计算 | H · A | 按年代与模型求周期或频率表；单位、模型和返回列随版本记录，原独立函数可单用。 |
| `ReferenceSeries` | 参考数据 · `ReferenceSeries` | 数据 | H · A · P | 共用区段与列选择；LR04、CENOGRID 的数据版本、列义和单位写入引用。 |
| `Examples` | 示例数据 · `ExampleCatalog` | 数据 | — | 原十二个入口保留为可单独选取的示例资源或演示配方；读取、显示和案例执行按各自内容处理。 |

## 序列与数学

| 原源码归属 | 新维护组与操作 | 类别 | 角色 | 归并依据及应保留的行为 |
| --- | --- | --- | --- | --- |
| `SortUnique` | 序列整理 · `SortUnique` | 科学计算 | H · A | 显式选择排序、缺失行和重复坐标处理。findduplicate 可供其他操作原位调用。 |
| `Columns` | 序列整理 · `Columns` | 科学计算 | H · A · P | 列索引与列操作决定输出表，表格选区留给 GUI；原入口的列顺序和输出形状可分别重放。 |
| `Interpolation` | 序列整理 · `Interpolation` | 科学计算 | H · A · P | 普通等距与 Pro 共用目标网格与序列输出；九种插值、缺口及多列行为由完整参数和来源版本选择。 |
| `Interpolation` | 序列整理 · `InterpolateSeries` | 科学计算 | H · A · P | 第二条序列给出参考坐标；保留双输入入口，底层可与等距插值共用能证明等价的代码。 |
| `SeriesEditing` | 序列整理 · `EditInterval` | 科学计算 | H · A | 同一维护组按区间选取、删段、造缺口；动作、闭端点、保留行或填充规则显式化。 |
| `SeriesEditing` | 序列整理 · `ClipValues` | 科学计算 | H · A | 阈值裁剪按数值作用，保留阈值、列及旧版本输出。 |
| `SeriesEditing` | 序列整理 · `Depeak` | 科学计算 | H · A | 按显式上下阈值截住异常振幅；原 depeaks 返回原坐标和截幅值，不承担区间删除。 |
| `SeriesArithmetic` | 序列数学 · `MergeSeries` | 科学计算 | H · A | 旧 menu_add 实为纵向拼接、排序并处理重复坐标；保留合并次序。 |
| `SeriesArithmetic` | 序列数学 · `MultiplySeries` | 科学计算 | H · A | 逐行相乘并按两套坐标返回。旧循环用第一条记录的值序列初始化累积乘积，须保留重复计入第一条记录的行为供回放。 |
| `Transform` | 序列数学 · `Transform` | 科学计算 | H · A · P | 十六种数值变换用方法选择；对数、标准化的快捷入口保留别名和原数值约定，Box–Cox 可附 λ。 |
| `Transform` | 序列数学 · `AffineAxes` | 科学计算 | H · A | 对两轴分别给出乘数和偏移。保留坐标也会改变这一契约，可复用 Transform 的推荐和展示。 |
| `Derivative` | 序列数学 · `Derivative` | 科学计算 | H · A | 输出坐标随差分阶数缩短；保留显式阶数、坐标和结果。 |
| `Extrema` | 序列数学 · `Extrema` | 科学计算 | H · A · P | 峰谷位置和数值是返回值；数量或方向按分支传入，底层找峰函数保留原名。 |
| `Changepoint` | 序列分段 · `Changepoint` | 科学计算 | H · A · P | 变点后验、分段模型和诊断独立；按原方法版本绑定先验、模拟与随机状态。 |
| `PCA` | 多变量统计 · `PCA` | 科学计算 | H · A | 坐标列处理显式，保留载荷、得分、解释方差和坐标对齐结果；可用通用序列视图画得分。 |

## 图像与展示

| 原源码归属 | 新维护组与操作 | 类别 | 角色 | 归并依据及应保留的行为 |
| --- | --- | --- | --- | --- |
| `SeriesPlot` | 序列视图 · `SeriesPlot` | 视图 | H · P | 单列、多列、错位及高级版由数据与样式配置驱动。GUI 编辑布局，plotter 复现已定配置。 |
| `Distribution` | 统计视图 · `DistributionView` | 视图 | H · P | 原 histfit 的核拟合与标注形成图，返回空；独立重画。分布拟合优度检验另有数值报告。 |
| `Sampling` | 采样诊断 · `SamplingRate` | 科学计算 | H · A · P | 相邻坐标差和位置是可保存的结果，间隔分布图为其视图。 |
| `Sampling` | 序列通用函数 · `SamplingGrid` | Core | — | 原位复用采样均匀性判别与容差诊断；已有版本化直接调用保留。 |
| `Sound` | 声音转换 · `SeriesSound` | 科学计算 | H · A | 计算波形 y 和采样率 Fs 可在无声卡环境重放；播放属前端，写音频属 IO。 |
| `ImageDisplay` | 图像视图 · `ImageView` | 视图 | H · P | 读取和显示图像，缩放、滚动归 GUI；重画只需图像引用与显示设置。 |
| `ImageColor` | 图像处理 · `ImageColor` | 科学计算 | H · A · P | 灰度与 Lab 共享图像输入和像素矩阵输出；颜色空间、通道和编码必须随结果保存。 |
| `ImageProfile` | 图像测量 · `ImageProfile` | 科学计算 | H · A · P | 显式给折线顶点，输出采样点与各通道值；Transect 还返回累计距离及控制点距离。选点归 GUI，覆盖图可重画。 |
| `Digitizer` | 图像数字化 · `Digitize` | 科学计算 | H · A · P | 给定像素、标定点、轴限及线性或对数尺度，得到数据坐标；GUI 负责取点。 |
| `Digitizer` | 图像数字化 · `DigitizeTrace` | 科学计算 | H · A · P | 给定种子追踪曲线；保留 GUIDE 替代引擎与 3.1.1 Strict/Loose 的区别，结果再标定或叠加显示。 |

## 时间序列

| 原源码归属 | 新维护组与操作 | 类别 | 角色 | 归并依据及应保留的行为 |
| --- | --- | --- | --- | --- |
| `Detrending` | 趋势与平滑 · `Detrending` | 科学计算 | H · A · P | 返回趋势及残差，拟合器、窗或阶数随分支给足；和纯平滑共用已有拟合代码。 |
| `Smoothing` | 趋势与平滑 · `MovingSummary` | 科学计算 | H · A · P | 均值或中位数、固定点数或物理窗宽用显式参数选择；保留边界处理和可用计数。 |
| `Smoothing` | 趋势与平滑 · `GaussianSmoothing` | 科学计算 | H · A · P | 高斯加权与普通滑动汇总共用坐标整理，单列核宽与权重约定。 |
| `Smoothing` | 趋势与平滑 · `BootstrapSmoothing` | 科学计算 | H · A · P | 重采样产生区间；带宽选择、样本数、置信度和随机状态可单独追踪。 |
| `Prewhitening` | 趋势与平滑 · `AR1Prewhitening` | 科学计算 | H · A · P | 返回预白化序列与系数，可复用 AR(1) 估计；与去趋势分开登记。 |
| `PowerSpectrum` | 频谱 · `PowerSpectrum` | 科学计算 | H · A · P | 三种谱估计器与六个可组合背景或诊断标志归参数表，保留整个谱、模型结果和各模型状态。 |
| `SWA` | 频谱 · `SWA` | 科学计算 | H · A · P | 独立 SWA 有 FDR、贝叶斯概率、报告及面板；功率谱中的 SWA 选项只共享适用计算。 |
| `EvolutionarySpectrum` | 频谱 · `EvolutionarySpectrum` | 科学计算 | H · A · P | 滑窗输出位置×频率，记录步长、补零及所选版本；与全段谱共享单窗内核。 |
| `EvolutionarySpectrum` | 频谱成果 · `EvolutionaryWorkbook` | 成果 IO | — | 在现成矩阵上导出工作簿，独立记录目标、表格布局和文件引用。 |
| `Wavelet` | 小波 · `WaveletSpectrum` | 科学计算 | H · A · P | 单序列时尺度功率、全局谱及尺度汇总共用变换；不同面板可复用一个结果。 |
| `WaveletCoherence` | 小波 · `WaveletCoherence` | 科学计算 | H · A · P | 双输入 WTC 与 XWT 标出分量、显著性及后端；区别于单序列谱，同一窗口可分别调用。 |
| `CircularSpectrum` | 事件谱 · `CircularSpectrum` | 科学计算 | H · A · P | 事件或坐标的圆形谱及检验独立，周期网格与模拟配置随输入传入。 |
| `Coherence` | 交叉谱 · `Coherence` | 科学计算 | H · A · P | 双序列频域的相干与相位是共同产物；保留平滑或频带与单位。 |
| `Bispectrum` | 高阶谱 · `Bispectrum` | 科学计算 | H · A · P | 预处理、估计、替代检验归双谱族；双相位、双相干等图层可单独重画。 |
| `Bispectrum` | 高阶谱成果 · `BispectralExport` | 成果 IO | — | 读取已算结果并写文件，登记文件引用及设置；旧 plotter 标识可重放。 |
| `SpectralMoments` | 频谱 · `SpectralMoments` | 科学计算 | H · A · P | 返回窗内谱矩；单窗估谱和移窗逻辑尽量直接复用。 |
| `Recurrence` | 非线性序列 · `Recurrence` | 科学计算 | H · A · P | 距离、递归矩阵与可选 RQA 统计按原分支显式选择，图从结果生成。 |
| `LeadLag` | 时序关系 · `LeadLag` | 科学计算 | H · A · P | 在滞后网格求误差曲线及最优滞后；底层 RMSE 可单独调用。 |
| `Filtering` | 滤波 · `FixedFiltering` | 科学计算 | H · A · P | 固定频带滤波保留类型、频界、roll-off 与响应；显式给原数值函数全参。 |
| `Filtering` | 滤波 · `DynamicFiltering` | 科学计算 | H · A · P | 随坐标变化的频带由控制点定义；输入与固定频带不同，叠加响应或瞬时频率复用绘图。 |
| `EMD` | 模态分解 · `EMD` | 科学计算 | H · A · P | EMD/EEMD 共享 IMF 与残差输出；集合方法单列噪声、次数和随机状态。 |
| `Modulation` | 调制 · `AmplitudeModulation` | 科学计算 | H · A · P | 包络与调幅序列可复用滤波相关函数；保留自己的输入处理、坐标和结果。 |

## 地层与年代

| 原源码归属 | 新维护组与操作 | 类别 | 角色 | 归并依据及应保留的行为 |
| --- | --- | --- | --- | --- |
| `BuildAgeModel` | 年龄标尺 · `BuildAgeModel` | 科学计算 | H · A · P | 按所选峰或谷和给定周期生成控制点、深度–年龄模型与沉积速率；选择和显示留给前端。 |
| `BuildAgeModel` | 年龄标尺 · `SedimentationRateToAge` | 科学计算 | H · A | 速率序列、单位与参考年龄决定积分结果，单独保留方向和端点约定。 |
| `Tuning` | 年龄标尺 · `AgeScale` | 科学计算 | H · A · P | 使用已有年龄模型作域转换，输入另含待调记录；与新建模型各有可重放入口。 |
| `Undatable` | 年代不确定度 · `Undatable` | 科学计算 | H · A · P | 原年龄–深度模拟、输入文件快照及随机状态保持独立。GUIDE 与 master 的角色覆盖分别记录。 |
| `StratCorrelation` | 地层对比 · `StratCorrelation` | 科学计算 | H · A · P | 记录两剖面与明确的对比点，返回对齐产物；编辑对比线属于 GUI。 |
| `PowerDecomposition` | 频带功率 · `PowerDecomposition` | 科学计算 | H · A · P | 按窗与频带输出功率；保留原 pda 与 3.1.1 契约。DYNOT 可复用适用内核。 |
| `DYNOT` | 沉积噪声 · `DYNOT` | 科学计算 | H · A · P | 噪声比例、模拟与区间是独立产物，DYNOS 与各版本开关和分位数留在记录中。 |
| `LagOne` | 沉积噪声 · `LagOne` | 科学计算 | H · A · P | 演化 Lag-1 与蒙特卡洛带共享操作族；旧版/V2 与确定性/随机结果明确标识。 |
| `Coco` | 天文匹配 · `Coco` | 科学计算 | H · A · P | 全段沉积速率扫描，明确目标构造、交叉验证及显著性；保留单独研究函数和旧模型绑定。 |
| `EvolutionaryCoco` | 天文匹配 · `EvolutionaryCoco` | 科学计算 | H · A · P | 局部速率–位置矩阵与追踪是独立产物；全段 COCO 可共享目标谱，复现时须有滑窗配置。 |
| `TimeOpt` | TimeOpt · `TimeOpt` | 科学计算 | H · A · P | 全段速率扫描、目标频带与拟合诊断独立，保留已恢复依赖的来源。 |
| `EvolutionaryTimeOpt` | TimeOpt · `EvolutionaryTimeOpt` | 科学计算 | H · A · P | 滑窗位置与局部拟合形成二维输出，可复用全段拟合的原函数。 |
| `Lyapunov` | 非线性序列 · `Lyapunov` | 科学计算 | H · A · P | 指数估计及替代模拟同族，嵌入、模拟数、随机状态及恢复实现随版本保存。 |

## 统计

| 原源码归属 | 新维护组与操作 | 类别 | 角色 | 归并依据及应保留的行为 |
| --- | --- | --- | --- | --- |
| `SummaryStatistics` | 描述统计 · `SummaryStatistics` | 科学计算 | H · A | 按变量给出描述量与报告。报告格式交给展示，百分位等函数仍供其他使用者直接调用。 |
| `HypothesisTests` | 统计推断 · `OneSampleT` | 科学计算 | H · A · P | 一列样本与参比均值，显式检验方向，返回 t、自由度、区间与原报告。 |
| `HypothesisTests` | 统计推断 · `TwoSampleTests` | 科学计算 | H · A | 两列样本，保留 t、F、秩和、KS、AD 等历史选项及原报告；记录检验名，旧 tabIndex 按版本解释。 |
| `HypothesisTests` | 统计推断 · `DistributionTest` | 科学计算 | H · A | 对指定分布作卡方拟合优度检验，所选分布进入参数；和核拟合展示独立。 |
| `HypothesisTests` | 统计推断 · `Normality` | 科学计算 | H · A | 一个样本的多检验正态性报告，保留一起运行的旧检验及每项结论。 |
| `HypothesisTests` | 统计推断 · `ANOVA` | 科学计算 | H · A | 多组等均值检验返回 F、平方和及原报告；不压成共同的 p 值接口。 |
| `Association` | 统计关系 · `Correlation` | 科学计算 | H · A | 两列的 Pearson、Spearman、Kendall 及显著性可共用一次调用。 |
| `Association` | 统计关系 · `Covariance` | 科学计算 | H · A | 协方差矩阵和 Bootstrap 区间需重采样次数、随机状态；独立入口。 |
| `Regression` | 回归 · `LinearRegression` | 科学计算 | H · A · P | 拟合、残差和诊断独立；GUIDE 发行包恢复候选的 fitlm 与 master 的 polyfit 结果分别绑定版本。 |

## 验证与诊断

| 原源码归属 | 新维护组与操作 | 类别 | 角色 | 归并依据及应保留的行为 |
| --- | --- | --- | --- | --- |
| `MethodValidation` | 双谱测试 · `BispectralSelfTest` | 方法自测 | — | 确定性方法自测，随双谱测试维护，显式运行并保留旧日志。 |
| `MethodValidation` | 双谱案例 · `BispectralExamples` | 验证案例 | — | 五组指定示例验证，保留输入和判据，可由测试或 Harness 点名运行。 |
| `MethodValidation` | 双谱案例 · `BispectralLocalDataStudy` | 验证案例 | — | 以 LR04/CENOGRID 运行双谱验证；真实数据来源、区段及输出应能追踪。 |
| `MethodValidation` | COCO 研究配方 · `CocoEightMethodExperiment` | 研究配方 | — | 九条记录八种目标设计的比较；保存研究设置及检查点。 |
| `MethodValidation` | COCO 研究配方 · `CocoPublicationValidation` | 研究配方 | — | 六个预定记录的全段 COCO 研究，保留预设和成果清单。 |
| `MethodValidation` | COCO 研究配方 · `EcocoTwoMethodExperiment` | 研究配方 | — | 六个记录的两种 eCOCO 比较，保存完整局部速率网格。 |
| `MethodValidation` | COCO 研究配方 · `InterleavedCvCocoComparison` | 研究配方 | — | 七条记录的交错交叉验证对比，保留随机配置及每组检查点。 |
| `MethodValidation` | COCO 研究配方 · `Syn3FourMethodStudy` | 研究配方 | — | 特定研究的四方法组合，保留固定条件及全段、滑窗两类结果。 |
| `MethodValidation` | COCO 成果核查 · `CocoPublicationCheck` | 成果核查 | — | 读取已保存的成果和参数复核；独立记录核查结论，无需重跑原数值实验。 |

## 数量与维护

GUI 3、Core 2、工作流 1、科学计算 66、数据 3、视图 3、成果 IO 2、方法自测 1、验证案例 2、研究配方 5、成果核查 1。

编辑用 TSV 中的 `*` 接收同一旧归属内尚未显式列出的包或菜单，`-` 表示没有该类入口。多个操作可以来自同一菜单。每个旧包只有一个主维护去向；跨组原函数调用另见调用清单。新操作名为提案，登记版本、函数签名及物理目录可分步落实。[调用清单](modules/shared_call_sites.tsv) · [重建脚本](tools/build_module_inventory.py)
