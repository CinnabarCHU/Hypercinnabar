# Leg 138 · Scientific Prospectus / Preliminary Report

这两份官方分发件各有一份已取得、已校验的 PDF。计划发布于 1991 年 1 月，初报发布于同年 9 月。

## 范围和入口

- **publication/Leg138_SP_Proposed_Sites.pdf** 是 SP “Proposed Sites” 全段的现代版。36 页依照原次序排下 12 份站位卡、12 张航迹图、12 张勘察剖面。卡片字段及地质目标正文已对照底图校读，英文字体用 Liberation Serif / Sans；图页直接嵌入原发布页，保留标签、阶调、版面与来源文字层。
- **figures/pr_fig15_graphic_check.pdf** 标出图读的 851 站回推图坐标及现代位置差，下方 CSV 记录可复核的轴与取点位置。
- **data/site_crosswalk.csv** 为方案到实钻站的证据对照。12 个候选站中 10 个对应明确的 PR 站节；新增加的 Site 850 以及只见于航前方案的 EEQ-4A、EEQ-5 各用独立行。Site 854 对应第二优先级 WEQ-2。每个配对有原图校核后的 PR 标题。候选位置及实钻位置分别引自 SP 表 1 和 PR 表 1 的 A 孔，不假定底图的大地基准。great_circle_difference_km 是以 6371.0088 km 为球半径的诊断值。
- **data/site_holes.csv** 将 42 个孔分别挂到 PR 表 1 的孔行和作业报告小节。844A、844B 在同一小标题内。版面文本的行序是 pdftotext -layout 输出单页中的一基索引。
- **data/sp_site_cards.csv、sp_card_fields.csv、sp_survey_times.csv** 收录 12 张站位表、146 个实际刊载栏、19 个站勘时标。没有分拆列出 Primary / Crossing 的单一站勘记录沿用 SEISMIC RECORD；EEQ-2 的第二个时标在原件上写作 Secondary site。勘察厚度、预期岩性、目标站坐标和拟用仪器均在其原字段保留。
- **data/pr_site_text_blocks.jsonl.gz、pr_site_text_index.csv** 将 11 站的科学和作业两组正文分别分到对应站和来源页，每个片段记原 OCR 的起止行，可直接按站抓取原文。各页中的相邻站标题已经切开，段落内容仍标为来源 OCR。
- **data/pr_sections.csv、pr_site_figures.csv、report_items.csv** 收 22 个站级科学/作业章节入口、44 个与站点相关的科学图关系以及 SP/PR 目录。PR 在相邻章节共用的页上以章节标题起点区分。PR 两张古地理图分别有区域和绘图对象。东部图上的磁异常年龄不能直接视为各站的时标位置。西部图给 851 轨迹画了 1–9 Ma 标记，其他六站只有位置符号。
- **data/pr_plot_workflows.csv** 从 11 站的 22 张初报图逐一提取图注。全部 11 张复合柱记载多孔拼接、mcd 轴及 GRAPE、磁化率、颜色的 20 点高斯滤波；全部 11 张质量累积速率图的图注区分离散样品点与地层控制点间的均值。记录保留页码和图注文字，不据此猜定滤波参数或逐点输入文件。
- **data/survey_profiles.csv** 核对了所有实钻站的初报剖面。9 个站重复发表了 VENTURE 01 图形，比较依据为船名、刻度、线号或测线注记、反射层几何。850 的初报单道地震和 854 的初报 3.5 kHz 剖面来自 JOIDES Resolution 航中调查。原始地震道集未在这两册内取得。
- **data/pr_fig15_backtrack.csv、pr_fig15_axis_ticks.csv、pr_fig15_check.json** 为图 15 的十个符号中心与轴校准。年龄零代表原图现今站位黑点；余九个为印出的年龄十字。经度根据四个已标记刻度拟合、纬度由 0–5°N 范围内插。CSV 内的两位小数用于复查几何，不代表同精度的古地理估计。该图的现代点与 PR 表 1 的 851A 坐标约差 79 km。原图读数和实钻位置各自保留，以后可另挂具名旋转模型。
- **data/pages.jsonl.gz** 收完整 55 页 SP、110 页 PR 的源 OCR。其它正文仍按来源文字层检索。**data/sp_time.csv、sp_logging.csv、sp_transit.csv、sp_totals.csv、pr_coring.csv、pr_operations.csv、pr_lab.csv、pr_time_chart.csv** 复用已校过的全航次原表，原列显示精度、空白、孔和站小计都保留。**data/editorial_notes.csv** 记录字段差别和刊载矛盾，包含数字经纬度与图读位置以及图 15 “Sites 881”。
- **data/source_manifest.csv** 给原 PDF 的 URL、字节数和 SHA-256。陆上 IR、SR 的出处由全航次的其他模块登记。新出书的 PDF 页序不替换来源页序。

## 重建

在本模块根目录，由原件包指定包含 SP.pdf、PR.pdf 的目录。基础目录重建使用 Python 3.11 及 Poppler，图件程序另需 PyMuPDF、Pillow、Matplotlib 和 ReportLab。字体可用 typeset_cards.py 的 --fonts 指定 Liberation 家族安装目录。

~~~bash
python tools/extend.py /path/to/primary
python tools/inspect_sources.py
python tools/slice_pr.py
python tools/backtrack.py /path/to/primary
python tools/typeset_cards.py /path/to/primary
python tools/verify.py --primary /path/to/primary
~~~

第一次从 Site 846 轻目录导入时，extend.py 接受可选第二个目录参数。交付的精校 CSV 可直接作为编辑输入。源 PDF、逐页 OCR、字段转录、解析字段、图读坐标分别保存。
