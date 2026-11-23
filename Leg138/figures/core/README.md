# Leg 138 沉积速率与质量堆积速率图件对校

打开 **Leg138_PR_Rate_Atlas.pdf**，每站一页，从 Site 844 排至 854。左栏取自 Preliminary Report 印图，右栏按站章 IR 随盘表和明确标记的图读点重绘，黑白、面板位置和原图图注位置均随本站原件。字体使用 Liberation Sans / Serif，中文编校说明使用 Noto CJK。**原图图注描述左侧完整图件。** 右栏层次说明见各页页脚。矢量原件在 vector/。随盘表中的深度、年龄和均值属于出版的数据产品。

## 图页与证据

|文件|内容|
|---|---|
|data/ir_interval_witnesses.csv|11 份年代控制表和 11 份区间均值表的章号、表号、印页、PDF 页、下载 URL、大小和 SHA-256|
|data/ir_mean_source_rows.csv、ir_control_source_rows.csv|按电子原件行号保存的数值行及文本。空白、单位和标题的发行版本以对应原始文件为准|
|data/ir_mean_intervals.csv|230 个均值区间，含原表年轻端、老端、数值行、来源深度和原刊字段。缺栏留空。另列相同年龄端点的控制表深度以及两端点算出的斜率，用于对校|
|data/pr_panel_axes.csv|54 个 PR 面板在 PDF 上的位置、量纲、取值范围和区间重绘的证据类别。坐标原点是 PDF 左上，单位是 1/72 英寸|
|data/pr_rate_check.csv、pr_rate_summary.csv|逐区间从 PR 图上读取的高度、IR 刊值、差值、所用窗口、判定和逐站统计|
|data/pr_printed_marks.csv|Site 847、852、853 有机碳面板各 25、11、8 个可见十字符号的位置及图读值。连接方式沿用印图，数值不具备原实验精度，也无法据此恢复样品编号|
|data/pr_mar_spotcheck.csv|Site 848 的有机碳区间线抽查，含取样年龄窗、源图纵坐标、右表值和行页出处|
|data/figure_index.csv|每个矢量出版图的相对路径、原图裁切框和校记|

11 个沉积速率面板使用相同图读测试，230 个区间中 127 个满足辨识条件，123 个在图读容差内。4 个越界结果中，Site 844 有两段明显高度差，Site 847 有一段高度差及表外的更老图线，Site 854 的停积段墨线贴近坐标轴，0.35 m/Myr 的图读－表值差应同时考虑套印和扫描定位。其余 103 段保留在明细里。此判定只对沉积速率适用。37 个 MAR 面板的 IR 刊表区间线属于候选对照层，Site 848 有机碳面板的单项抽查有差异。余下 6 个 MAR 面板仅见独立点迹或细线，其中 3 个有机碳面板已按图读点重绘，Site 854 的 3 个 MAR 面板保留空坐标框。原页中的全部细线保存在左栏。

均值表在 Site 845 按年龄老端把数值和边界排成一条印行，随盘 ASCII 将同一行拆写。其起点和 Site 851 的起点可在各自控制表找到明确记载的 0 Ma 芯顶，表内另标来源。Site 848 表 16 第 40 行电子版的 4.58 起整组提前一栏，印页 728 明确把 4.58 放在沉积速率栏。本图按印本布列，电子版原栏位见 IR 命名原表。Site 853 表 12 第 59 行（7.28–7.50 Ma）末值 0.14 对应有机碳 MAR，非碳酸盐 MAR 栏为空；在有机碳面板另绘的 PR 十字形是独立印图读数。Site 853 表 12 电子表把深度写为 mbsf，印本表头写 mcd，本图全部以刊载年龄为横轴。所有逐站版本均随表号保存。

## 核对与复现

沉积速率以每一表列年龄区间的中央 32% 搜索水平墨迹。去除距左右轴 4.5 pt 以内的区域。原区间不足 4 pt、裁去轴区后不足 1 pt、候选墨迹低于 53/255 或越轴时均单列状态。程序在纵轴范围内独立找墨迹峰，按相邻 7 个 4× 像素带作加权定位。图读容差取满纵幅的 1.2%，是印图比对阈值。图读十字符号采用人工复查的图像中心坐标，按各站原坐标轴校准；1 PDF pt 的保守图面定位余量折算成年龄和值，一并记录。

在本目录运行，将两个输入路径替换为所用分发目录的实际位置。Python 需要 PyMuPDF、NumPy、Matplotlib、Pillow、Playwright。图集排版需要 Chromium 及 Liberation 和 Noto CJK 字体。

```bash
python tools/read_tables.py /path/to/ir/primary
python tools/check_rates.py /path/to/sppr/primary/PR.pdf
python tools/read_print_graphics.py /path/to/sppr/primary/PR.pdf
python tools/draw_atlas.py /path/to/sppr/primary/PR.pdf --chromium /path/to/chromium
python tools/verify.py /path/to/ir/primary /path/to/sppr/primary/PR.pdf
```

原始 PR PDF 的 SHA-256 为 48f7d7e22f672f499c38d610d995ad713874cfd01bc29516cf6b2f4cbe6d18c5。PDF 页号从 1 起算，印页照录。核对以电子表和出版图为界；历史仪器输出、实验复测关系及历史软件执行结果属于其他证据层。
