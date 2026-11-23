# ODP Leg 138 航次档案
在解压出的 `Leg138` 目录中双击 **browse.html**。浏览器可离线选择 Site 844–854，查看航前代号和实钻孔、筛选逐行碳分析、打开图件、比较校记。网页引用的官方底本链接需联网。各数据目录内的 CSV、PNG、SVG、SQLite 和 PDF 可直接用普通软件打开。

[ODP138_Leg_Report_Edition.pdf](publication/ODP138_Leg_Report_Edition.pdf) 是 84 页现代排版校读本。页 1–30 为航次与逐站初报，31–66 为航前拟钻站，67–77 为初报速率图，78 为 SR 年代学图对校，79–82 为照片取色窗口，83 为古位置图读，84 为可点击目录。全卷逐页索引与精校覆盖率见下文。

## 本地 API 与全文检索

首次检出时先在 `Leg138` 目录运行 `python tools/build_catalog.py`，生成本机索引，再运行 `python tools/serve.py`，打开 <http://127.0.0.1:8138/>。服务、导出和重建 SQLite 使用 Python 标准库。SQLite 需启用 FTS5。浏览目录、PDF 或 CSV 无需启动服务。

| 查询 | 可运行的相对路径 |
|---|---|
| Site 850 的航中新增记录 | `/api/sites?site=850` |
| 12 个拟钻站及实钻对应 | `/api/plans` |
| Site 852 的 IR 表与出处 | `/api/items?site=852&series=IR&kind=table` |
| Site 846 的页内检索 | `/api/search?q=organic%20carbon&site=846` |
| 图版册的原页文字层 | `/api/search?q=ooze&series=PLATES&site=845` |
| 已知的 IR 第 17 章第一页 | `/api/page?doc=IR.C17&page=1` |
| 查询某刊载项有哪些数据表示 | `/api/datasets?item=IR11.T11` |
| 导出 Site 851 的有机碳，含刊载脚注和原行号 | `/api/rows?dataset=IR.ORGANIC_C&site=851&format=csv&limit=1000` |
| Site 852 的 PR–IR 作业字段对校 | `/api/rows?dataset=PR.IR.CORING&site=852` |
| 查询一张表已登记的原字段含义与测量／计算角色 | `/api/fields?dataset=SR.C39.TABLE2.CORRECTED` |
| SR 第 39 章表 2 的勘误版，限定 Site 846 | `/api/rows?dataset=SR.C39.TABLE2.CORRECTED&site=846&limit=1000` |
| 全航次明确标为第 1、2、3 次的碳酸盐重复分析 | `/api/rows?dataset=IR.carbonate_repeat_runs&limit=1000` |
| GRAPE 刊载产品与孔文件的双向行号 | `/api/rows?dataset=CD.GRAPE_SOURCE_ROWS&site=844&limit=20` |

各列表均可选 `limit=1…1000`、`offset` 及 `format=csv`；站与计划是小型完整列表。`/api/documents`、`/api/items`、`/api/evidence`、`/api/sources` 和 `/api/datasets` 提供稳定的章、图表、证据、文件及数据集标识。行查询用 `dataset` 精确指定发布版本。全文检索的默认范围是四种出版物，图版附册用 `series=PLATES`。页码为 PDF 物理页，从 1 起算；印页单列，机器识别的页脚在 `basis` 下有注明。站点过滤返回有明确关联的记录；SR 中页面提到、题名、图注和电子表中真正出现站号分别保存在 `evidence.role`。候选图注可据原 PDF 复查。

## 每个模块维护的材料

| 目录 | 内容与核验范围 |
|---|---|
| `sppr/core` | 两份官方报告的文字层、12 张精校拟钻站卡、22 个实钻站科学／作业段落、11 站图注所述的数据处理。船上新设 Site 850，与未钻的 EEQ-4A、EEQ-5 都有独立记录。 |
| `ir/core` | 全 20 章、652 个编号图和 259 个编号表。179 份随盘章表可由 17,835 条文字行及原换行完整还原。其中 104 张编号表已有具名字段，155 张仍待字段化。11 站的 CaCO₃ 重复实验表共 318 个样品、645 次具名测量，出版的逐样差与均差另列。原随盘表目录列有但未取得 ASCII 的第 6 章表 1、3、4 和第 12 章表 6 已从刊载页另建转录。不推定未找到文件的字节内容。 |
| `sr/core` | 全卷 47 章，最后一章为期刊重印。67 份电子表或其修订版本，刊载行 124,288；其中 124,280 行完成字段映射，8 行另存未能确定的原文。13 份已转录印表为 2,255 行。791 个图表、附录或图版条目中 721 个是待校的自动图注候选。站点证据与正式勘误单列。 |
| `disc/core` | 随盘站点数据、COREDATA、原程序、原目录证据、字段说明与复算表。原仪器文件的路径、已校准量、站点拼接产品、从曲线上读的值用各自来源说明。原分发只提供路径的中间件仍标未取得。 |
| `plates/core` | 593 张独立彩照的内嵌 JPEG 目录，592 页岩芯描述、26 页涂片和两张折页。每站一张照片有两块已核验原像素裁片（沉积物与标尺），另有原像素坐标。其余照片可定位与提取，但尚未逐张分割、深度配准或校色。 |
| `figures/core` | 11 站 PR 速率图的原图／重绘对照、54 个面板、230 条带原行号的 IR 区间、图面读值与未决区间。来自 IR 数据的重算线和由 PR 图面提取的点各有标签。 |
| `data` | 76 份主体出版物共 1,922 页的索引文字、现代站位、全航次碳分析样例、逐孔差异、分册和校验。图版附册另索引 620 页。古地理仅提供 PR 图 15 所刊轨迹的独立图读，原图点位误差与页图同存。 |

CaCO₃ 重复实验表单列 `sample_row_id` 和 `run_record_id`，两者的范围均限定于该份发布表。Site 853 第 22 个样品的两次刊值为 87.90% 与 87.07%，出版差栏为 0.17，复算差为 0.83 个百分点。三个刊载字段均可直接回到 IR 印页 1049。

这里的有机碳是 IR 原表明确给出的字段。2,296 个取样行中有 666 行有数，跨十站；空值、仅有无机碳、脚注均值、重复标签及负值均保留。有机碳质量百分数与质量累积速率分别记录。`data/carbon_distribution_comparison.csv` 只在取样键唯一时才比对两份分发文件的数值。Site 851 两条相同取样标识的记录不会被自动归并为一次测量或两次独立测量。

## 底本及复建

四个 `ODP138_Sources_*.zip` 均可按需展开至与本包相同的父目录，合并其中的 `Leg138` 目录。源 PDF、图像、程序、纯文本按原分发路径保存在 `*/primary`。每个包带有逐文件 SHA-256 和完整文件清单；一共 5,425 项，包括两份目录快照。它们是现存数字分发的独立备份，后续如获得新的载体，可用新见证记录补入。主包的 `SHA256SUMS` 覆盖主包内其他全部文件。也可按路径单独拉取某份底本，例如 `python tools/fetch_source.py ir/primary/VOLUME/CHAPTERS/ir138_17.pdf`。程序会核验字节数和哈希，遇到源站改版则保留本地已有见证。原 Site 846 的独立 IR、SR 试点成果随包保留于 `previous/ir` 与 `previous/sr846`。

```bash
python tools/build_catalog.py
python tools/make_browser.py --help
python tools/verify_catalog.py
```

SQLite 可从主包附带的逐页文字和编目表重建。涉及原始图像提取、从 PDF 抽取源文字、或随盘软件全流程复算时，先展开相应底本包。各模块 README 给出模块自己的构建命令。主编版面分别使用 Noto CJK 字体排中文、Liberation Serif 排重排的英文正文、DejaVu Sans 排数值与图标。PR 与 SR 原刊对照图各自沿用原图版式和黑白样式，来源截图、后配文字和代码重绘各有标记。

```bash
python tools/carbon.py . data
python tools/compare_carbon.py . data
python tools/edition.py . data publication/Station_reader.pdf
python tools/merge_edition.py . ODP138_Leg_Report_Edition.pdf
```

重画、PDF 文本提取和排版分别用到 matplotlib、PyMuPDF、Poppler 的 pdftotext 与 WeasyPrint。光谱对校使用 NumPy。复跑原 Fortran 程序需要 GNU Fortran 及模块所列兼容性补丁。核对以来源文件哈希、记录值、选行、页定位与图件为单位；PDF 字体依赖和编译器版本可能改变再次生成文件的字节哈希。
