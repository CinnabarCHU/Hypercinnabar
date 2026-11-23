# 经典科学问题与已知真值模型

这六项研究任务覆盖三种推断。频谱问题要求从观测中找周期，调谐问题要求给层位赋予年龄，古自转问题要求同时估计沉积速率和天文参数。每个任务均可使用自己的算法。评分器保留原文的岩芯、代理指标、时标和单位。[机器可读的任务与评分对象](../catalog/tasks.json)

## 六个经典研究任务

| 任务 | 交给方法的资料 | 科学问题与比较对象 |
|---|---|---|
| `hays76-simplex` | RC11-120 夏季海表温度 184 行，E49-18 浮游有孔虫 δ¹⁸O 105 行。各岩芯采用原文表 2 的线性 SIMPLEX 时标 | 分别找长周期、倾角和岁差三个谱峰。表 3 给出 RC11-120 的 87、38、21 kyr，E49-18 的 109、47、24 kyr。另从提交值计算倾角/岁差周期比，与原表 1.8、1.9 分别比较。这项比值在整条线性时标等比例伸缩时保持不变。[Hays、Imbrie 和 Shackleton，1976，表 2–3](https://www.whoi.edu/cms/files/hays76sci_268464.pdf) · [RC11-120](https://doi.org/10.1594/PANGAEA.52223) · [E49-18](https://doi.org/10.1594/PANGAEA.52207) |
| `rossello-precession` | 西西里 Capo Rossello 复合剖面 76 个旋回层位的高度，两个端点年龄，以及可供选用的 La2004 北纬 65° 夏季日照 | 将各旋回层位对应到岁差循环，允许漏记旋回。参照为 Lourens 等表 1 的校准层位。该表将层位中点定在对应日照极大之后 3 kyr，并标出不参与建标的带星号层位。基准选取 40–128 m 的无星号层位，年轻到老的两个端点是 127.11 m / 2588 ka 和 40.56 m / 4403 ka。[Hilgen，1991](https://doi.org/10.1016/0012-821X(91)90082-S) · [Lourens 等，1996](https://doi.org/10.1029/96PA01125) · [校准表](https://doi.org/10.1594/PANGAEA.790776) |
| `odp846-published-clock` | ODP 846 的 322 个底栖 δ¹⁸O、319 个 δ¹³C 测量及两端年龄，可选 La2004 日照。按修订复合深度取 63.43–96.00 rmcd，实际最深观测为 95.91 rmcd | 在 1763–2502 ka 内重建底栖同位素年代。每个内部层位的偏差相对于 Shackleton、Hall 和 Pate 表 5 的发表时标。原工作还使用了 Leg 138 的区域年代约束。[原文及印刷表 5](https://www-odp.tamu.edu/publications/138_SR/VOLUME/CHAPTERS/sr138_15.pdf) · [数据集](https://doi.org/10.1594/PANGAEA.696450) |
| `newark-long-eccentricity` | Newark Basin Coring Project 的 Nursery 至 Martinsville 湖相深度等级序列，共 22,581 行。归档坐标已经过 McLaughlin 长偏心率旋回调谐 | 在同一坐标上估计载波与长周期的波长，将其比值乘以论文采用的 404 kyr，与约 1.75 Myr 的长周期比较。该结果以已有的 404 kyr 标定为条件。[Olsen 和 Kent，1999](https://doi.org/10.1098/rsta.1999.0400) · [作者的岩芯数据](https://www.ldeo.columbia.edu/~polsen/nbcp/data.html) |
| `xiamaling-precession` | 下马岭组约 1.4 Ga 的 Cu/Al 深度序列，263.420–265.496 m，共 179 行 | 联合估计沉积速率和地轴岁差频率，可提交恒星日长及边际区间。用两个时期的方法解释同一记录。[Meyers 和 Malinverno，2018，表 2](https://doi.org/10.1073/pnas.1717689115) · [Malinverno 和 Meyers，2024，表 3](https://doi.org/10.1029/2023GC011176) |
| `walvis1262-precession` | Walvis Ridge ODP 1262 约 55 Ma 的色度 a*，选取 117.36–139.75 m 窗内 1,024 个实测值，首行 117.38 m | 对早始新世记录重复沉积速率与古自转推断。与下马岭共享输出格式，保留独立的年龄、搜索区间和文献参照。[2018 年研究](https://doi.org/10.1073/pnas.1717689115) · [2024 年研究与两套原始数据的出处](https://doi.org/10.1029/2023GC011176) |

Hays 的输入采用作者后来公开的 SPECMAP 档案。便携示例在同深度取平均，按 3 kyr 采样，在各频带选 Hann 谱内最强的局部极大值。原论文报告未预白化谱的峰周期，两个岩芯分别用 91、121 个时间点以及 40、50 个滞后项。评分沿用原表单独报告的 b/c 比值。用表中已取整的周期相除会引入舍入差异。更换谱估计器也会改变单峰和周期比的偏差。[原论文表 3 及图 5](https://www.whoi.edu/cms/files/hays76sci_268464.pdf)

Rossello 输入保留高度，隐藏内部年龄、沉积旋回编号和日照编号。原表采用 La90(1,1)，示例在 La2004 日照极大值中作有序匹配并沿用 3 kyr 响应滞后。示例允许跳过日照极大值，并按偏离两端所定平均沉积速率的程度给候选匹配打分。Rossello 和实测 Site 846 的评分均单列内部层位 RMSE 及两个端点的偏差，也接受整条年龄曲线的后验样本。[原始校准说明](https://doi.org/10.1594/PANGAEA.790776) · [La2004](https://doi.org/10.1051/0004-6361:20041335) · [实现](../adapters/classic_studies.py)

### Site 846 的同位素列核对

PANGAEA 表 5 文本将第四、第五列依次标为 δ¹³C、δ¹⁸O。印刷表 5 的顺序是 δ¹⁸O、δ¹³C。例如，63.43 rmcd、1763 ka 处的氧同位素值为 3.82‰，碳同位素值为 −0.35‰。本基准保留源文件字节，读取时按印刷列序解释。执行 `python bench.py verify --sources` 会复查三份独立编排的表。在该区间，108 对数值与表 3 经校正的 Uvigerina 氧、碳及深度吻合，25 对与表 7 的年龄、氧、碳精确吻合。按表 5 网页表头的顺序比较，表 7 得到零对。表 7 是插值时间序列，两表的采样点只部分重合。[印刷原表](https://www-odp.tamu.edu/publications/138_SR/VOLUME/CHAPTERS/sr138_15.pdf) · [表 3](https://doi.org/10.1594/PANGAEA.696447) · [表 5](https://doi.org/10.1594/PANGAEA.696449) · [表 7](https://doi.org/10.1594/PANGAEA.696451)

### 地轴岁差与古日长的参照

地轴岁差频率 `k` 以角秒/年计，沉积速率 `u` 以 cm/kyr 计，恒星日长以小时计。两项任务分别报告相对于论文后验均值的偏差。提交 95% 区间时，还报告宽度以及上下端点与 2024 年表 3 的差。只提交点估计的方法可将适用的可选字段写作 `null`。[2018 年 TimeOptMCMC](https://doi.org/10.1073/pnas.1717689115) · [2024 年 TimeOptB](https://doi.org/10.1029/2023GC011176)

| 记录 | 2018 年参考值（u / k / 日长） | 2024 年参考值（u / k / 日长） | 本次 astrochron 1.8 实算（u / k / 日长） |
|---|---|---|---|
| 下马岭 Cu/Al | 0.357 / 85.79 / 18.68 | 0.353 / 87.74 / 18.47 | 0.35249 / 87.66426 / 18.47725 |
| Walvis Ridge a* | 1.316 / 51.28091 / 23.80485 | 1.309 / 51.25 / 23.75 | 1.31069 / 51.30595 / 23.73207 |

下马岭 Cu/Al 测量来自 Zhang 等（2015），Site 1262 色度来自 Zachos 等（2004）。本版采用 astrochron 示例中可核对的选择范围和重采样步长。原生 R 示例采用 61 × 61 搜索网格、TimeOptB 边际后验均值和 `alodfromk` 换算。从 R 的原生输出读取后验统计量，保留完整文本和版本。便携 Python 示例采用固定行星频率和简单谱功率网格搜索，给出点估计。[完整 R 评分](../baselines/astrochron.json) · [完整 Python 评分](../baselines/python.json)

## 有真值的功能案例

| 功能案例 | 给定条件和逐点参照 | 对应科学任务 |
|---|---|---|
| `cip-case3-forward-clock`、`cip-case3-inverse-clock` | 正向按原生成器的 3 kyr 网格和右端点沉积速率逐步累积，对照 2,902 行高度与速率。反向给全套时深节点，在 2,631 个原始观测高度检验反插值 | `cip1-case3` 从带噪代理重建年代。参照为同一条生成时标。[Sinnesael 等，2019，式 2](https://doi.org/10.1016/j.earscirev.2019.102965) |
| `odp846-segmented-clock-original`、`odp846-segmented-clock-reduced` | 给定 25 个控制点，分别对三段线性插值，各验 420 行。两个间断的上下限几乎同深，年龄相差约 53 和 17 kyr。原归档的分段插值序列是功能参照 | `odp846-oracle-original`、`odp846-oracle-reduced` 评价与稠密生成时标的偏差。实测 Site 846 的任务另用 Shackleton 等的发表时标。[归档来源](../catalog/provenance.json) |
| `laurin-weak-band-forward` | 给定含两端延拓的旋回相位节点和高斯衰减参数，核对弱带实验无噪声代理的 294 个观测深度 | `laurin-weak-band` 从固定的带噪重复试验及峰位窗口恢复局部历时。[原实验归档](../catalog/provenance.json) |
| `two-rate-forward-proxy` | 给定 40 m 速率突变、4/6 cm/kyr、三个谐波和冻结的随机扰动，核对 2,000 个固定深度上的年龄、无噪声代理和含 AR(1) 噪声的实际观测值 | `synthetic-rate-step` 仅获得带噪观测和分析窗，反推两段速率。[观测生成器](../fixtures.py) |
| `am-hilbert-envelope` | 整周期载波和调制项均落在 DFT 网格上，已知解析包络为正。验证全部 256 个样本，包括边缘 | 用于检查瞬时振幅。R 原生 Hilbert、SciPy 和 MATLAB Signal Processing Toolbox 使用同一份解析参照。[算法与输入](../catalog/cases.json) |
| `imbrie-response-continuous`、`imbrie-response-euler` | 在相同的 96 个 1 kyr 强迫样本上由老向新推进。连续模型按每个常值强迫段的指数解取样，原生 astrochron 离散模型按显式欧拉迭代。两个参照分别用块内指数与几何级数独立生成 | 检查快消融、慢生长、时间方向和步长。这里的强迫是已知的分块输入，原论文讨论冰量对天文强迫的非对称响应。[Imbrie 和 Imbrie，1980](https://doi.org/10.1126/science.207.4434.943) · [实现](../adapters/synthetic_models.py) |

可在同一环境中运行以下两个命令，分别得到软件数值偏差和地质年龄偏差。

```bash
python tools/run_profile.py python .results/cip-function cip-case3-forward-clock cip-case3-inverse-clock
python tools/run_profile.py python .results/cip-geology cip1-case3
```

每个运行目录包含请求、方法输出和逐项评分。绝对年龄或地层相位的文献解释允许修订，合成记录上的生成参数和数值参照已按文件哈希冻结。[数据来源](../catalog/provenance.json) · [冻结校验值](../catalog/checksums.json)
