# ODP Leg 138 · Scientific Results

本目录沿用原卷顺序。选择章节后可以找到站点关系的原句、原刊图表的位置、随盘同名表的逐行数据以及勘误。章节表涵盖 46 篇研究论文及第 47 章期刊重印。印页与 PDF 物理页分别记录。第 47 章保留其在本卷中的位置，期刊版的页码和书目见出版社目录。

## 如何使用

在本目录运行以下示例。数据导出只需要 Python 标准库。

```sh
python tools/export_table.py --list
python tools/export_table.py SR.C39.TABLE2.CORRECTED --site 846 -o site846_isotopes.csv
python tools/export_table.py SR.C41.TABLE1.PRINT -o all_sites_sr_summary.csv
python tools/export_table.py SR.C06.TABLE28 -o site854_accumulation.csv
```

| 文件 | 阅读方法 |
|---|---|
| `chapters.csv`、`pages.jsonl.gz` | 原卷次序、作者、DOI、印页范围与每一 PDF 页的搜索文字。文字为官方 PDF 原有识别层，保留错误和原排版顺序。印页的识别或推定依据逐页记录。 |
| `source_manifest.csv`、`distribution_tree.csv` | 原文件相对路径、出处、长度、SHA-256、当前获取状态，以及官方章节/随盘目录逐项比对。检索包与原文件合用时，相邻的 `primary/` 为原文件根目录。 |
| `items.csv`、`caption_anchors.csv` | 图、表、图版和附录的命名项与物理页面。自动定位者包含出处文字和 PDF 文本块边界。版面旋转的三张表另外查读。印刷图注候选尚未全面精校，引用、漏检和 OCR 错字仍可出现。坐标字段属于文本块，精校附加项的位置以页为单位。 |
| `site_evidence.csv`、`dataset_site_evidence.csv` | 题名、摘要、正文、图注候选、先前 846 专项校核和印表行分别标示。并列站号与范围中的内插站号可分辨。正文提及站点可能出现在文献综述。电子表另给来源、首末行和涉及该站的记录数。多站并排表的同一行可以有多个站号。 |
| `assets.csv`、`errata.csv` | 附件和所属图表的关系、勘误对象、原件、更正件与发布日期。保留第 1 章六个影像面板以及第 21 章图 17 折页。 |
| `datasets.csv`、`field_roles.csv` | 随盘表/附录及其更正文件的字段顺序、数据性质和行数。卷内每份表独立存在，允许重复样号及作者采用不同年龄、深度或解释。字段角色是编目说明，数值单位与特殊含义需与原表头、附注和论文对应。 |
| `records.jsonl.gz` | 每条电子记录包含数据集键 `d`、顺序号 `n`、物理源行区间 `lo` 至 `hi`（从 1 开始）、站点列表 `s`、依原列序保存的值 `v` 及可选校记 `note`。值为字符串，保留有效位数、空值、作者占位符和脚注。歧义行的 `v` 为 null。 |
| `nonrecord_lines.csv`、`unresolved_records.csv` | 表头、注释等其余非空物理行，以及分栏歧义行的原文、出处与原因。可在独立原件中查到每一行。 |
| `print_datasets.csv` | 从印本重新转录的数据，列出纸刊来源及独立 CSV。846 专项已有 12 份转录、2,244 行及逐格校记；本次补入第 41 章表 1 的 11 站、11 行。印表转录行数另计。 |
| `figures/SR06_Figure11_comparison.pdf` | 同页对照第 6 章图 11 的出版社印页 98 及从随盘表重绘的结果。配套数据 CSV 含 11 个站，被画入原图的 10 站另有标记。 |
| `print/SR41_Table1*` | 第 41 章印页 814 旋转 90° 的完整印表、逐格转录及文字附注。印本汇总了各站沉积覆盖、钻深、速率、区域地形、热流和作者判断的近基底 Sr 同位素剖面特征。 |
| `verified846/` | 先前专项的印表、校记、核验截图、项目索引和字段说明；第 27 章图 3 从已精校印表直接绘制。 |
| `verification.json` | 源文件哈希、行与字段、站点联系与出版物数量的核验结果。 |

## 来源与版本

出版社 SR 主目录、正文及出版附件在 `source_manifest.csv` 中列为 ODP。实际按字节复核了 179 个官方文件。SR 的章节和影像子目录中公开列出的 174 份叶文件都收录，余下五份官方文件是该两棵树以外的目录、书目、索引或更正件。随盘说明提到 Macintosh 的 QuickTime 2.0，在线分发的 `CHAP_1/MAC/` 列表为空。可获得的六幅 MOV 及 Windows 播放软件原分发文件均有记录。历史软件作为原件保存。另有 13 份此前收集的 PANGAEA/NOAA 存档资料，来自 846 专项；本轮核对其本地字节及既有来源，其他站点的所有后续数据出版物尚待专门编目。

第 39 章表 2 同一表号有两个发布版本。随盘文本含 197 行、仅 844B。出版社 2000 年 3 月 29 日的更正件含 2,472 行，跨 11 站。每份文件须通过各自数据集键访问，两者总数是发布行数。这里没有跨版本推定每行的独立测量身份。第 1 章勘误更正的是出版物目录的 CD-ROM 部分对图 7 的描述。

第 6 章图 11 的图注指向 Tables 18–28。原版图上实际有 10 个面板，顺序为 Sites 844–853；Table 28 包含 Site 854 的沉积速率，作为随盘数据保留。本次从各站作者发布的速率序列重绘，照原保留 0–10 Ma 的绘图窗口、两列布局、黑色曲线和原图注位置，嵌入 Liberation Sans 和 Liberation Serif。晚于 10 Ma 的表行和未绘的第十一站仍在所附数据中。

第 3 章附件保存 GRAPE 记录所在样品位置及 mbsf、mcd、rmcd 三套深度。附件不含密度读数。第 15 章表 9 收录用作比较的 Leg 111 Site 677，保留原站号。全卷 PDF 文字现作为检索层，尚未完成全文精校、全部印表逐格重录和全部图版重绘。目录计数应与这些不同层次的交付对应。

## 重建与验证

将源备份置于本目录上一级的 `primary/`，保留原相对路径。参考工具适用于 Python 3.10+，PDF 解析使用 PyMuPDF，HTML 解析使用 lxml，绘图使用 Matplotlib。

```sh
python tools/build_tables.py
python tools/build_roles.py
python tools/build_publications.py
python tools/figure6_11.py
python verified846/figure27.py --source-pdf ../primary/official/VOLUME/CHAPTERS/sr138_27.pdf
python tools/validate.py
```

若要重新比对网上目录，可以运行 `python tools/check_distribution_tree.py`。读取纸本截图的局部范围、旋转方向和数据脚注保存在印表说明中。回查早期读数时以原件和对应的校记为准。
