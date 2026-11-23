# ODP Leg 138 · Site 846 · Scientific Results

这份校读本按 1995 年《Scientific Results》的章节、原表和原图编号组织。查询和重绘均可离线完成。数据库保留每份发布版本的字段、单位和行次，计数时以选定的数据表为边界。

## 打开

双击 **Site846_SR.html**，选择章节、图表和版本。点击表格首列可见原出处、文件行或印页位置、校记及 SHA-256。支持搜索、导出当前查询的 CSV 和单条记录的 JSON。图 3 的双页对照已嵌入网页。建议使用近期版本的 Firefox、Safari、Chrome 或 Edge。

可选原件包 `ODP138_SR_Source_Companion.zip` 解压后得到 `sources/`。将它放在 HTML 同目录，离线浏览时可点“本地底本”。物理行号从 1 起算，包括表头与空行。文本文件的记录同时附有原行文字。浏览器的 PDF 阅读器决定页码锚点能否直接跳转，界面同时给出印刷页码。

Python 3.10 或更新版本可启动只读 HTTP API，与单文件版共用界面。此功能只使用 Python 标准库。

```sh
python app.py
```

打开 `http://127.0.0.1:8460/`。原件放在其他目录时，可用 `python app.py --sources /path/to/sources` 指定。API 返回原字段、读数、来源 URL、校验值及记录出处。

| 用途 | 端点示例 |
|---|---|
| 出版目录与入库范围 | `/api/chapters`、`/api/items?chapter=15` |
| 一张表的各发布版本 | `/api/datasets?item=c27_t1` |
| 按样号取数 | `/api/rows/c27_t1_print?q=C4-1%2C68-70&limit=10` |
| 精确定位一行 | `/api/row/c27_t1_print/171` |
| 校记与处理关系 | `/api/reviews?chapter=27&page=608&field=sst_c`、`/api/relations?item=c15_t5` |
| 导出指定版本 | `/csv/c43_appa_print` |

## 范围

| 章节 | 已整理的原表与附件 |
|---|---|
| 15，Shackleton、Hall 和 Pate | 表 1、3、5、6、7 依光盘原表录入。表 2、4、8 由印页转录。表 9 的对象为 677 站，原页及完整盘文件可查。另存 PANGAEA 该系列的全部五张子表。图 1–11 均有印页索引。 |
| 27，Emeis 等 | 表 1 的 227 行、表 2 的 3 行由印页录入。表 1 与 PANGAEA 的样号及全部 16 个数值栏位都做了逐行对读。图 1–4 已定位，图 3 的四个面板已从印表重绘。 |
| 33，Le 等 | 表 1–3 均已转录。附录按印本前后两段各存 239 行。后段沿用前段表头，列义有待考证。附录的 PANGAEA 发布单列。图 1–10 已定位，图 7 的续页一并登记。 |
| 43，Mix、Le 和 Shackleton | 附录 A 的 809 条分析、附录 B 的 654 行年龄模型均由印页对读转录，定位到页、印刷栏、表内行。另存 NOAA 附录 A、B 及最终序列，以及 PANGAEA 的两份发布。图 1–11 已定位。 |
| 跨站 | 第 3 章四孔的深度转换，6 章表 3、20，23 章表 3、5 的本站栏或本站行，35 章附录 A–C 的本站行，39 章表 2 的原盘与更正发布。第 1 章图 7 附原始电影 A–F、图注勘误，第 4、44 章的相关图提供印页入口。 |

全卷 47 篇进入书目索引。四篇主文共 14 张编号表、3 份附录和 36 幅编号图。库中 42 份数据表共有 53,305 个**发布行**，包括并列版本、不同数据产品及 39 章原盘的 844B 行。图件重绘的样例为第 27 章图 3。其余 35 幅主文图已定位于原刊，尚待重绘。四篇的连续正文也有待精校重排。

## 三个可复核的例子

**独立分析与最终序列。** 第 43 章 p.848 左栏第 3、4 行，846B-1H-1 的 33 cm，同由 OSU 分析 *C. wuellerstorfi*。两次 δ¹⁸O 为 3.65 和 3.88‰，δ¹³C 为 −0.10 和 −0.06‰。NOAA 附录 A 第 6、7 行分别保留两次分析，另发最终序列第 4 行给出 3.765 和 −0.080‰。p.852 表注说明附录 A 已作类群校正，C. wuellerstorfi 的 δ¹⁸O 和 U. peregrina 的 δ¹³C 分别加过 0.64 和 0.90‰。NOAA README 的 *raw data with depth scales* 指它在本文工作流中的位置。

**同一表的发布差异。** 第 27 章表 1 的 `C4-1,68-70`，p.608 最后一行，印本 SST 读作 25.3 °C，PANGAEA 给 23.3 °C。印本有机碳堆积速率用 mg cm⁻² kyr⁻¹，PANGAEA 用 g cm⁻² kyr⁻¹。按单位换算后，有机碳通量列的全部可比读数一致。全表 3,632 个数值位置（含空格）中，只有上述 SST 格在换算后有数值差异。

**附录换栏与深度异读。** 第 33 章附录前半列出十个类群，后半从首个样品重新开始，沿用原表头。p.690 回排处的第八数值列出现 367 等三位整数。后段按 `slot_01` 至 `slot_10` 保存。同页第 63 行样号 `846B-3H-4,79`，印本为 23.84 mcd、23.83 rmcd，PANGAEA 的前段记录为 23.84、2383.00。两段同序号的样号也偶有出入，跨段对应须逐项考证。

## 释读与校记

- mbsf、船上 mcd 和修订 rmcd 各保留原字段。第 6 章表 3 使用 mcd，第 15 章表 6 使用 rmcd。在第 33 章附录的 PANGAEA 发布中，通用的 Depth sed 栏按该数据集的说明是船上 mcd。
- 第 15 章表 3 按分析编号分行。表 4 给类群调整系数，表 5 给已选择、平均和赋龄的序列，表 6 给年龄模型，表 7 是 3 kyr 网格上的平滑插值。表 7 使用 5.99 kyr 全宽，图 5、6 使用 8.99 kyr。光盘全部 1,463 行及 `-9999.00` 原样保留。PANGAEA 表 7 的 1,383 行，与盘本有 δ¹⁸O 的行逐值对得上。SQL 视图 `c15_interpolated_numeric` 将缺测码映射为 NULL。
- 第 23 章表 3 第一组站点表头下有 5 行出现额外数值或断行，本站上下界留空，事件及完整原行可用 `WHERE record_note <> ''` 定位。原文件中明确印作 `n.a` 的格保留该字样。
- 第 39 章旧随盘文件含 197 条 844B 分析。出版社于 2000 年 3 月 29 日更正后，846B 有 264 条，846D 有 2 条。分析对象为全沉积物。原件包保存两份完整文件，库内的本站记录指向更正表的物理行。
- 第 43 章附录 A 对读 NOAA 后，段内位置、三个深度、两项同位素在 809 行中逐值吻合。21 行的刊本 section 与 NOAA 的标识在统一大小写、横线和前导零后仍有差异，包括孔号、芯号及 H 的有无。附录 B 的深度、年龄及速率经 Ma/ka、m/Myr 与 cm/kyr 换算后，与 PANGAEA 的 654 行吻合。
- `catalogue/print/cell_reviews.csv` 保存 OCR、刊面读数与仓储对照值。图像比对使用出版社 PDF 的扫描层，数值对读使用作者或仓储文件。同读也可能承袭原刊错误。各表量纲和数据处理关系见 `field_notes`、`datasets.description`、`relations`。PDF 页坐标以左上角为原点，单位为点。小型印表以表内行号定位，其余印表额外给出行中心高度。

## 重绘与重建

`proofs/Chapter27_Figure3_Comparison.pdf` 将重绘和原刊裁片放在两张同尺寸页面上，翻页即可核对。TOC、CaCO₃、估算干密度及烯酮指数分别有 226、210、227、191 个非空点。四条线各自按非空观测顺次连接，纵轴为 rmcd，深度向下。保留原图分栏、上下刻度、黑色线点和图注位置。重绘字体为 Liberation Sans 与 Liberation Serif，图注重新措辞，对照页保留原图注。

在解压后的主目录中运行以下命令，假设 `sources/` 位于同目录。维持原始字段值的 SQLite 表以文本存数，用 SQL 做计算前须按原量纲、缺测符号显式转换。示例见 `examples.sql`。

```sh
python verify.py
python verify.py --sources sources
python build.py --sources sources --out rebuilt.sqlite
python verify.py --db rebuilt.sqlite --sources sources
python tools/standalone.py --out Site846_SR.html
```

刊本校读成果独立存放在 `catalogue/print/`，可直接编辑、比较和重建。主库及离线网页的重建只依赖标准库。图 3 重绘另需 Matplotlib、PyMuPDF 和 Liberation Sans/Serif 字体。抽取印页裁片只需 PyMuPDF，长表抽取整行，小表返回全表供按表内行号复核。

```sh
python tools/figure27.py --source-pdf sources/official/VOLUME/CHAPTERS/sr138_27.pdf
python tools/source_crop.py c27_t1_print 171 --sources sources --out p608_row86.png
python tools/ocr_check.py --sources sources --out ocr-differences.csv
```

`catalogue/sources.csv` 列出 URL、DOI（适用时）、字节数及 SHA-256。原件包保留出版社在线分发的 178 件、9 件 PANGAEA 及 4 件 NOAA 文件。随盘目录包括 66 个科学 ASCII 文件、6 段 QuickTime 影片和历史软件分发文件。此次的载体是公开的文件级分发。原始光盘的扇区镜像及独立馆藏印本留待后续校勘。各作者和数据仓储的引文请以对应 DOI 或原文件为准。
