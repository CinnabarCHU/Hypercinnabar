# Leg 138 Scientific Results 印表的版面索引与精校读数

全卷有 230 张已核实身份的表。前版数据库、印本转录与第二轮七表覆盖其中 53 个唯一表号，部分旧转录只涉及 Site 846。本模块为全部 230 张另建印本版面索引，其中 177 张首次取得可按页、行、列检索的表体。逐项对照记录在 `coverage.csv`。原件以 `sr/primary/` 为根目录，逐文件 SHA-256 见 `pdf_sources.csv`。

## 检索层的含义

230 个起始段和 76 个明确标为 continued 的续段共 306 段，均有实际表体读数。按版面得到 12,517 条物理基线，88,600 个表体位置格，109,125 个表体词元。一条物理基线可能包含并排的多个记录，跨行名称也可能分成多条。统计值描述版面读取规模。科学数据的行数、样品数与字段关系需要逐表校订。

- `coverage.csv` 按 item_id 记录已有数据集键、旧转录的站点范围、各段源页与候选格总数。判为 rejected 的旧引用只见于上层对象校记。
- `segments.csv` 保留起始/续页身份、印刷页码、PDF 叶号、阅读方向、题名区、表头区、表体区以及实际复核状态。PDF 坐标以原页左上角为原点，单位为点。含 90 度横置表的页仍使用原 PDF 坐标。横向续栏和纵向续行各段保持独立键，表号相同不代表可以直接上下拼接。
- `cells.jsonl.gz` 的主键为 `segment, role, row, col`。role 为 header 或 body。每格同时给出原词元、包围框、每个原词及其框、位置列、字形横跨列的范围和读取来源。发布 PDF 的识别层、另行旋转后的 OCR、人工认读的稀疏字形分别标识。数据库里的空白单元不能推定为零或物种缺失。
- `field_dictionary.csv.gz` 逐段逐栏记录原词元组成的表头候选和阅读方向下的横坐标范围。`vertical_header_candidates.csv.gz` 专门保存侧排物种名称在原 PDF 字层和转正扫描视图中的独立候选，均带来源和原版坐标。自动 OCR 保留原词形，生物分类名称尚待校订。
- `grid_rulings.csv.gz` 保存复杂矩阵上的 1,111 个版面线段候选。`row_span_candidates.csv.gz` 记录 93 个左侧分类名称可能跨越的行带、印刷分隔线与行号。物理跨度单独保存，便于后续核实哪些样品继承了该名称。

## 人工核读

`visual_regions.csv` 给出 43 次源图校核的表段范围。15 段标为 sample_geometry_checked，另有 27 段稀疏矩阵确认了范围而物种栏头仍待逐项判读，1 段是待解释的公式版面。其余 263 段来自扫描横线、文字横向对齐和原 PDF 识别词元推得的候选边界。出现实际读数证明这些段能按坐标检索，全表边界、漏行、重复栏、横向续页、置信度偏低的数字和符号仍须通过原图确认。仅具名精校文件中的字段按人工读取发布。

| 精校文件 | 核对范围 |
|---|---|
| `verified_c04_table2.csv` | 完整 7 行。各站及汇总行的斜率、截距、印出的 ± 项和相关系数可直接读取。Site 850 的相关系数为 0.88，原 PDF 字层误作 0.8S。 |
| `verified_c21_table2.csv` | 完整 37 行。按倒序保留生物事件编号、原刊分类名称与 FO、LO、FCO、LCO；保留原刊拼写。 |
| `verified_c12_table14_p29_marks.csv` | 印刷 p.261 第 14 表横向续栏，22 个字形定位到四个具名分类栏。源页未印样号，sample_assignment 保持未绑定。 |

三份均有对应的原 PDF 裁片。其他位置候选不具备上述精校等级。计算式表格、多级合并栏头、侧排分类名和稀疏分布表的科学含义均保留待核状态。

## 复建

以下命令从 `leg138_all` 目录运行。需要 Python、PyMuPDF、NumPy、SciPy、Pillow 及 Tesseract 英文识别数据。输入为 SR 原章 PDF、新版对象与候选题注索引、已有数据集索引及本目录的人工区域记录。原章 PDF 始终按字节保留。

```sh
python -B sr/core/edition2_print/build_parallel.py sr/core sr/core/edition2_print --workers 4
python -B sr/core/edition2_print/curate_samples.py sr/core sr/core/edition2_print
python -B sr/core/edition2_print/curate_biohorizons.py sr/core sr/core/edition2_print
python -B sr/core/edition2_print/curate_sparse.py sr/core sr/core/edition2_print
python -B sr/core/edition2_print/vertical_headers.py sr/core sr/core/edition2_print
python -B sr/core/edition2_print/ruled_groups.py sr/core sr/core/edition2_print
python -B sr/core/edition2_print/verify.py sr/core sr/core/edition2_print
```
