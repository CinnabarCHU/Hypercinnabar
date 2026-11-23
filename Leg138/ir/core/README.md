# Leg 138《Initial Reports》章节及随盘表校录

本模块保存 TAMU 发布的数字分发见证。`../primary` 为按发布目录排列的原文件，`sources.csv` 每条给出原 URL、路径、字节数及 SHA-256。20 个编号章节合计 791 个 PDF 页面，涵盖第 9 至 19 章的 Site 844–854。卷首、机构名录、出版政策也有独立底本。站章 PDF 终止后另排的岩芯资料与卷后折页在全航次配套图版模块。COREDATA、SITE_DATA 和旧软件由随盘数据模块提供。

## 查一个图表

1. 在 `chapter_items.csv` 按 `site`、`kind`、`number` 或 `item_id` 查找。例如 `IR11.F21` 指第 11 章图 21，`IR18.T01` 指第 18 章表 1。目录有 652 幅编号图和 259 张编号表，其中 13 幅图见卷后折页。题名来自卷首随盘表清单和扫描 PDF 开头的图表题文，可能只收录首行。
2. 在 `chapter_item_locations.csv` 查页。`caption_text_layer` 指扫描 PDF 现有文字层识别出的图题或表题。`page_image_checked` 指人工从扫描页核对，`narrative_reference_candidate` 指正文提及的位置。`foldout_container_from_official_contents` 给官方折页文件。`pdf_page` 从 1 开始，`printed_page_basis` 区分印刷页码边栏命中和按章起页推算。`chapter_pages.csv.gz` 保留 PDF 的现成文字层。全卷逐行文字校对与精排出版仍需后续编辑。
3. 在 `dataset_items.csv` 按 `item_id` 找 `dataset_id`，以 `datasets.csv` 找文件、表示形式及行数。跨站 CSV 包含明确站号、表号和底本定位。`table_coverage.csv` 按 259 个编号表各列一行，避免把同一表的多种表示重复计数。电子原件、先前试点及印本转录按此文件去重。当前 **104 张编号表有具名字段**（87 张有线上原文件、17 张无线上原文件）。还有 **92 张线上表只有可逆逐行版**，另 **63 张仅有本模块的索引/定位**。其他全航次模块可补充其各自的数据产品。

## 原字节、原表和新数据

`disc_list_collation.csv` 对照卷首 PDF 中 183 项随盘表目录与现行网站的 179 个 `TABLE.*` 文件。`native_tables.csv` 和 `native_lines.csv.gz` 收全 179 份文件的 17,835 个原始物理行，含抬头、空行和注释。`raw_text` 按 Latin-1 字节一一映射，`line_ending` 辨 CR、LF、CRLF、无终止符，`tokens_with_positions` 的起止是从 0 开始、末位除外的字符位置。逐字节重组回原文件已验证。逐行及分词表示支持追溯原文，在字段释义和单位尚待校定时仍可使用。

`print_tables` 收录卷首列名但线上未见的第 6 章表 1、3、4 以及第 12 章表 6，共 76 行。印本页分别为 88、91、91、351。校录保留空值及印刷数字精度，字体、上下标及区间连线转换成可检索文本。数值见证来自印本。`site846_prior` 保存既有 Site 846 的 21 张表及对应的校记、出处和逐项状态，`site846_prior_bridge.csv` 将原试点的编号连接到全卷目录。

| 已具名的跨站产品 | 数据及来源 |
|---|---|
| `tables/coring.csv` | 599 条每芯记录及 42 行孔组小计。保留原孔组序号、孔标签、月年标题、UTC 与回收率。 |
| `tables/core_depths.csv` | 597 条报告发布的岩芯区间（mbsf、mcd）、长度与复合深度偏移。mcd 和偏移属于深度配准的产品。|
| `tables/carbons.csv` | 11 站原表 2,296 行样品的出版值。666 行给 Corg；Site 854 的该表只列无机碳和碳酸盐含量。原表脚注字母、负值与空列保留。 |
| `tables/index_properties.csv`、`compressional_velocity.csv`、`vane_shear_strength.csv`、`thermal_conductivity.csv` | 合计 43 张有电子版的物性表。按资料类型分别为 4,334、3,352、1,585、861 行。原单位、方法与标签异常见 `physical_table_headers.csv`，四个 CSV 均位于 `tables`。 |
| `carbonate_repeat_samples.csv`、`carbonate_repeat_runs.csv` | 11 站报告明确给出先后 run 的碳酸钙重复分析。318 个样品行对应 645 个出版 run；另有 11 行出版的平均差。样品行保留原报告的绝对差，运行表每 run 一行。 |
| `carbonate_repeat_sources.csv` | 9 站由本轮扫描页转录，846 用既有校本，850 用随盘 ASCII。Site 850 站章印本第 843 页是指向随盘表的正文。 |

`editorial_notes.csv` 记述来源间的孔名、表头、异常数值和代表性缺项。`sample_row_id` 定位某一出版表中的一行。遇到相同样品名，也保留各行和各 run 的出处。报告只公布均值的行仍按均值保存。极差复算、古地理重建、古年龄更新如需增补，应作为新计算输出建立独立记录。

## 复建及验证

保留模块的 `core` 与 `primary` 为同级目录。使用 Python 3、PyMuPDF 和 lxml。已备份原件时可从第二条命令开始；只有首条需要向源站取缺失文件。9 张重复分析印本表的版面列坐标和读图订正在 `duplicate_carbonate.py` 中。4 张无随盘文件的手校读数在 `transcribe_print.py` 中。

```sh
python core/tools/acquire.py
python core/tools/transcribe_print.py
python core/tools/native.py
python core/tools/core_depths.py
python core/tools/physical.py
python core/tools/catalogue.py
python core/tools/duplicate_carbonate.py
python core/tools/release.py
```

`release.py` 检查 229 个源对象的摘要和长度，将逐行文本重组并与源文件逐字节比对，核对 846 全部 318 条碳表行的 7 个字段，检查图表、数据集、样品行与运行记录之间的引用关系。计数保存在 `verification.json`。
