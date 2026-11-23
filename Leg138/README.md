# Leg 138 航次资料与数字校读版

双击 [站点浏览](browse.html) 或 [全卷目录](catalog.html)。两者都可离线使用。网页按报告自身的组织关系检索。某个编号来自航前拟钻、某个值来自后来的重复测量、某个图是现代复算，都能从对应条目分辨。分册 PDF 可从[离线分册索引](publication/chapters/index.html)打开；独立的[84 页站点校读本](publication/ODP138_Leg_Report_Edition.pdf)适合先通读。新增的[逐章校记与图件对照](revision/README.md)包含 Site 846 站章全部正文与题注的影像校读、42 孔的 546 项刊载字段和 85 个新重绘图号。

## 本地检索

首次检出运行以下命令。数据库由分支内的结构化文件构建，检索与导出使用 Python 标准库和支持 FTS5 的 SQLite。以下命令以 Python 3.12 检验。

```sh
python tools/build_catalog.py
python tools/verify_catalog.py
python tools/verify_edition2_catalog.py
python tools/verify_publication.py
python tools/serve.py
```

访问 <http://127.0.0.1:8138/>。常用查询如下，所有站号、页号均使用报告标识。

| 目标 | 本机 API 示例 |
|---|---|
| 查询 Site 850 的计划对应关系 | `/api/sites?site=850` |
| 在 Site 846 有证据关联的页中检索有机碳 | `/api/search?q=organic%20carbon&site=846` |
| 区分两次测定和刊物计算字段 | `/api/rows?dataset=IR.carbonate_repeat_runs&site=853&format=csv` |
| 导出 Site 851 的刊载有机碳和脚注 | `/api/rows?dataset=IR.ORGANIC_C&site=851&format=csv` |
| 获取 IR 第 2 章表 1 的字段、图面来源和读数 | `/api/ir-tables?item=IR02.T01`、`/api/item-rows?item=IR02.T01`、`/api/print-cells?item=IR02.T01&row=1` |
| 比较 SR 的刊载对象与撤回的目录候选 | `/api/sr-objects?status=rejected` |
| SR 第 39 章表 2 勘误版中属于 Site 846 的值 | `/api/rows?dataset=SR.C39.TABLE2.CORRECTED&site=846&limit=1000` |
| 查 SR 印表位置以及逐页分栏的原词证据 | `/api/sr-tables?item=SR.C04.TABLE2`、`/api/sr-table-cells?item=SR.C04.TABLE2` |
| SR 第 35 章附录 B 的疑行校记 | `/api/sr-apparatus?dataset=SR.C35.APPENDIXB&line=2065` |
| 查询岩芯标尺的源图位置 | `/api/roi?core=844A1H&role=printed_ruler` |
| 读取具名测井数值 | `/api/rows?dataset=CD.E2.LOG.844.ACT_GST&limit=10` |
| 查历史古位置与作者的模型参数 | `/api/geography?site=846&age=5`、`/api/rotation-stages?site=846` |
| 对看印本 OCR、校订段落和孔摘要字段 | `/api/page?doc=IR.C11&page=3`、`/api/collations?doc=SR.C15&q=raw` |
| 查 Site 846 图 7 的轨道、输入文件、绘图代码和校记 | `/api/figure-reproductions?item=IR11.F07` |
| 查原件与发布字段的描述 | `/api/sources?path=ir/primary/VOLUME/CHAPTERS/ir138_17.pdf`、`/api/fields?dataset=SR.C39.TABLE2.CORRECTED` |

通用列表的分页使用 `limit` 和 `offset`。表行可加 `format=csv`。全文索引以 PDF 物理页定位，刊载印页和机器判读的页脚另列。SR 的页内提及、图表范围和数据行中出现站号是三种不同的证据。

## 可核验的覆盖

| 对象 | 本分支覆盖与读法 |
|---|---|
| SP、PR | 12 张拟钻站卡和全部实钻站的段落边界已校读；42 孔保留计划、作业和最终刊载的不同来源。 |
| IR | 20 章、652 图、259 表。259 个表号现均有具名字段读法。179 张电子原表有可逆逐行见证；原随盘目录中另列的 4 张有印页转录。第二轮新增 92 张电子表和 63 张印表，后者覆盖 6,273 个字段位置，其中 907 个经人工逐格核读，957 个仍有待判。空格、跨行标签与两个读取方式一致的格子单列。 |
| SR | 46 篇论文加 1 篇期刊重印。公开电子表或修订版本 67 份、124,288 个刊载行。原先 721 个候选逐项查原页，确认 718，撤回 3，另补 21 个附录；现有 809 个有效对象。230 张有效印表均定位到表体，含 76 个显式续段，共 306 段、88,600 个表体位置候选格。先前无字段资料的 177 个表号也已纳入。电子表疑行、栏位置与人工精校字段各自标注。 |
| 船上数据 | 随盘 4,383 份来源可按文件回取。明确实验记录、校准后数据、拼接产品与后算图读各自保留。65 份测井产品已逐格回读，11 站的 149 个孔隙水记录逐行与章表配对。Site 844 二进制颜色表成功定位 57,969 个值的字节地址。 |
| 岩芯、涂片、地理 | 593 张彩照均核过原生 JPEG、标尺及背景。592 张有可用的沉积物候选区域，43 张做过人工整板抽查。涂片 26 页、1,156 行、25,194 格可定位；93 格为逐格人审读法。现代站位与 IR 古位置各有自己的来源。Site 844/845 的 36 个古年龄行只刊纬度；Site 854 章内题作 851 的 9 行保留两个身份，默认不在地图上放点。 |
| 原刊全文与图件 | 76 个分册、1,922 个主体来源页。153 页有明确范围的逐行影像校读，另有跨站孔摘要，合计 165 个不重复来源页。Site 846 的 IR 正文、SR 第 15 和 30 章的正文与图注已完成本轮。1,206 个原图号中，109 个已有数据及绘图代码。[逐图验收](data/FIGURES.md)和[离线图文索引](revision/index.html)均可核查材料、图表版本及尚存差异。 |

[电子原表校记](ir/core/edition2_native/README.md) · [IR 印表单元格](ir/core/edition2_print/README.md) · [SR 对象与异文](sr/core/edition2/README.md) · [SR 印表图面与单元格](sr/core/edition2_print/README.md) · [随盘工作流、反射光谱与测井](disc/core/edition2/README.md) · [原像素区域与涂片](plates/core/edition2/README.md) · [11 站速率图复建](figures/core/README.md) · [复合地层图与 106 份随盘来源](figures/core/composite_v2/README.md) · [原图、图注裁取及黑白 SVG 描摹](figures/core/published_artwork/README.md)

## 获取原件和重新出版

底本索引和材料获取无需本机数据库。已存在的本地文件会先做字节校验。若源站后来替换了文件，程序会报告差异，可作为另一份发布见证留存。[按需下载说明](data/SOURCES.md)

```sh
python -m pip install -r publication/requirements.txt
python tools/fetch_sources.py --doc IR.C11 --list
python tools/fetch_sources.py --book --workers 8
python edition2/build_edition.py . build/full --workers 4
python edition2/verify_edition.py . build/full
python edition2/verify_regions.py build/full
python tools/compare_editions.py build/full
python tools/publish_readers.py build/full build/chapters --workers 4
```

`build/full/index.html` 能离线阅读 HTML 与 PDF。每个来源页有现代文本，配合相关的字段表、图件，再附完整的原刊见证。紧凑分册除去重复的见证页，保留指向原版物理页的链接。指定 `--doc IR.C11` 可单独生成 Site 846 章。图书构建使用 PyMuPDF、ReportLab、Pillow 及模块所列 DejaVu 字体；图件和原 Fortran 工作流的要求见各模块 README。原始软件的重放、低置信 OCR 与图面校记都能在新的底本出现后单独复核。[全卷出版说明](edition2/README.md)

以前的 846 试点表与代码保存在 `previous/ir`、`previous/sr846`，旧的统计解释可按 Git 提交恢复。原出版物的作者、原测数据单位和发表版本在来源条目中独立保留。

复建完成后，可生成经过逐文件验证的离线 ZIP。将校读说明复制到构建目录，使本地生成的版本信息独立保存。

```sh
python edition2/check_fonts.py build/full
python edition2/verify_updates.py . build/full
python edition2/verify_sr_annex.py . build/full
cp -R edition2 build/release-index
python edition2/finish_release.py build/full build/release-index
python tools/package_edition.py build/full build/Leg138_Full_Edition.zip
```

本次公开分支更新 IR、SR 分册。SP、PR 的公开 PDF 沿用先前发行版，各自的新校记和本地重建代码见 [SP、PR 说明](revision/text_sp/README.md)。完整对读本包含这两册的新排版。读者自用时运行 `tools/publish_readers.py` 的默认模式即可为所有 76 册导出紧凑 PDF。
