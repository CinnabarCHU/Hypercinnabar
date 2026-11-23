# Leg 138 初报综合地层图对校

打开 **Leg138_PR_Composite_Atlas.pdf**。初报有 11 个站的综合地层图，本图集按原件续页拆成 22 页。左栏保留原印图。右栏在同一坐标框内重绘 GRAPE 密度、磁化率及三个反射率波段，极性、时代、图示岩性、地层单元和深度轴沿用初报。每个物性面板有 PDF 坐标、原刊刻度和单独说明，矢量层以原始 PDF 坐标保存。

## 发布数据与船上工作流

|曲线|依据和处理|
|---|---|
|GRAPE|11 站均有独立公布的 GRAPE/GR###.MCD。使用第 3 栏公布的平滑、未校正密度与第 1 栏 mcd。所用 121,065 行都带有样品标识。第 2 栏未平滑密度可以单独导出。|
|磁化率|Site 847 使用独立公布的 SUS847.MCD，其他站依据逐孔 FIN 和该站 SPLICE 区间选取。IR 第 2 章印页 32 指明仪器读数乘 0.63 再乘 10⁻⁵ 转为体积磁化率 SI。图上以 10⁻⁵ SI 标度，故曲线用 0.63 倍读数。共 42,943 行。|
|颜色反射率|随盘 COLOR/COL*.FIN 已刊蓝 450–500 nm、红 650–700 nm、近红外 850–900 nm 的反射百分比。初报标蓝、红、红外三条黑白线。按随盘 SPLICE 区间选孔，得到 61,575 个位置，每行三波段。Site 844B 平行二进制本另作来源登记，绘图取 BH/BX 文本以避免重复。|
|解释层|磁极性、时代、图示岩性和单元是原作者的解释。右栏保留原印图该部分。retained_layers.csv 逐站说明其角色、出处和可恢复程度。|

**已发布数值独立重绘 66 个物性面板。初报原 20 点滤波完整再现 0 个。** 随盘 FIXGRAPE.F 的 gsmooth 实际使用 9 点权重，继而可选执行一次或两次。PR 图注称三个物性量皆采用 20 点高斯窗；当时各曲线输入版本、核宽和边界处理仍待确定。

右栏 GRAPE 直接使用随盘已平滑密度。磁化率和颜色另用编辑显示滤波，20 个样点的高斯权重，σ = 4 个样点，中心处于第 10 与 11 个样点之间，每条连续片段端部按剩余权重归一。换孔、换源、岩芯或段界、倒序深度及相邻记录超过 0.30 m 时折线断开。此规则和核宽属于本版编辑选择。Site 844B 在 18.3–21.5 mcd 重复取芯，本版逐孔磁化率及颜色选 3H。原章确认这处重叠，公布 GRAPE 亦选 3H，PR 对其他通道未留下明确决策。

**历史程序核查。** 用随盘 SPLICE.F 回放 Site 847 磁化率。公布本有 4,263 行，回放有 4,301 行；按全部字段和重复次数，有 4,251 行可以配对，12 行仅见于公布本，50 行仅见于回放。图集采用公布本。sus847_historical_splice.csv 另记按原顺序相等的行数、编译器及源文件哈希。这项核查只涉及拼接阶段。

## 核验与文件

- data/panel_regions.csv 登记 66 个面板的页内 pt 坐标、分面标度、编号刻度、估算的图框端点及墨迹留白。原件有轻微扫描歪斜，右栏用校定矩形。
- data/source_tracks.csv、site_series.csv 给出来源文件、URL、SHA-256、发布阶段、单位转换、读入与采用行数。逐物性轨迹可从原数据导出，行内含源文件与源行号。
- data/figure_index.csv、figure_layers.csv 对应原 PR 图号、PDF 页、图集页和独立矢量层。右栏可以出现初报未画出但后来 FIN 公布的数据，Site 845 续页 38 是一个例子。
- data/scan_trace_checks.csv 在校准后的固定深度上比较独立密度或磁化率曲线与原图同水平像素带深色墨迹的中位值，避开图框、墨迹不足或过密、覆盖重叠和候选印图留白。程序不平移两条曲线。表中给出有效深度数、Spearman 秩相关、原轴上绝对差中位数及占轴满幅比例。线宽、纸张歪斜、原曲线靠框会影响指标。
- data/alternative_scale_checks.csv 用同一校定比较其他数值阶段，分别为 GRAPECOR 公式校正后的密度、及未经 0.63 换算的磁化率仪器读数。相似形态或较小残差均不足以确定原作者曾采用某版本。反射率三条黑白线相互交叠，没有以单条墨迹中位数充作三个波段的独立核验。

在本目录运行。缓存可再生，依赖 Python、NumPy、SciPy、Matplotlib、PyMuPDF 和 Pillow。历史 Fortran 核查另外需要 GNU Fortran。校准算法见 tools/calibrate_regions.py。

```bash
python tools/collect_tracks.py /path/to/disc/primary /path/to/disc/core /path/to/cache
python tools/render_composites.py /path/to/sppr/primary/PR.pdf /path/to/cache
python tools/verify.py /path/to/disc/primary /path/to/sppr/primary/PR.pdf
python tools/replay_sus847.py /path/to/disc/primary
python tools/collect_tracks.py /path/to/disc/primary /path/to/disc/core /path/to/cache --export-site 846 --export-quantity reflectance > Site846_reflectance.csv
```
