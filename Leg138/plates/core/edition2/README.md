# Leg 138 岩芯照片、描述页与涂片表

`examples/Leg138_optical_segmentation.pdf` 展示六张照片的原图与分区对照，`data/site_coverage.csv` 列出 11 站的覆盖量。使用精简版时，可按 `data/photos.csv` 的原址下载需要的照片。每种结果均定位到保存时校验过的发布 PDF。

## 从彩照中取像素

593 张原版 PDF 各内嵌一份原生 8 位 RGB JPEG。全部照片各定位出一条左侧厘米尺、一个避开印字和管列的背景小窗。4499 个预期位置中有 4497 个检出持续的成对管沿。管内进一步筛得 7300 个候选沉积物矩形，分布在 592 张照片。保留 6 个人工查明的标签、白衬管或空隙排除带。汇总涵盖全部 12,989 个矩形。593 个 PDF、其内嵌 JPEG 和每个矩形的解码 RGB 字节串均已核对并保存校验值。

| 资料 | 打开后可以检查什么 |
|---|---|
| `data/photos.csv` | 每张照片的原址、底本和内嵌 JPEG 哈希、尺寸、几何质量类别与区域数 |
| `data/lanes.csv` | 自左向右的板上列序、管沿强度、前后端坐标、内部管沿中断以及内窗覆盖比例。列序指照片的位置；物理节号或 CC 仍需回读原图上端 |
| `data/regions.csv` | 每个矩形的稳定编号、角色和原生 JPEG 像素框。左、上包含；右、下不含。横向原点在左，纵向原点在上 |
| `data/roi_rgb_checksums.csv.gz` | 每个矩形的原始解码像素哈希和尺寸；不含 PNG 文件头 |
| `data/qa.csv`、`data/reviewed_exclusions.csv` | 43 张人工整板抽检的理由、范围及问题；6 个显式人工排除带的位置与依据 |
| `data/anchor_overlap.csv` | 每站一个人工内窗与一个人工标尺窗，分别计算与新版区域的像素重叠比例 |
| `examples/native_crops/` | 四个无损 PNG 和定位、来源、像素哈希及文件哈希；其余区域按需导出 |

`photographed_liner` 保留整列可见照片，包括标签、断裂和白色空隙。`sediment_candidate` 表示管内与邻近底板有足够 RGB 差异、且避开管沿及端帽的候选窗。`printed_ruler` 与 `board_background` 分别保存厘米尺和底板取样窗。`reviewed_non_sediment_band` 是肉眼核过并向相邻像素留有余量的排除框。读数全部来自未经白平衡和辐射定标的档案照片；扩展到绝对反射率、CIE 色度或深度序列需要独立的定标与配准。

自动程序在缩至 540 像素高的图像上探测列板，再把边界向内换算回原生图像。套管几何以成对边缘在纵向上持续出现为依据，允许纸条或白色空隙造成内部信号中断。沉积物候选区另要求管沿强度和相邻底板 RGB 差异达阈值。精确参数集中在 `tools/segment_photos.py`。最终裁片从原始 JPEG 直接取出，没有重采样。

43 张整板抽查按站、窄图、低分辨率、弱边界、缺乏材料候选及早期算法易截断的实例选取。审核针对整板定位可见性；6 个排除带另查原生像素。首版人工选定的 11 个沉积物内窗全部落在相应管列里，其中 10 个被候选层完全覆盖，849B2H 的覆盖为 35.64%。手选标尺窗与自动标尺的交叠为 88.24%–100%。845A1H 的两处空板位保留待判。848B8H 的 8 个管列均可见，其样品与亮底板的颜色非常接近，自动候选窗数为零。各站的浅色沉积物也可能仅有局部进入候选层。测量色度前应检查对应照片的候选区域内有无标签、阴影或暴露内衬。

## 岩芯描述页编号

`data/vcd_page_identities.csv` 在 592 页中并列记录表头、印版照片标号、直接可对应的彩照以及只有表头支持的候选彩照。第一版所缺的一侧标号共 170 页，已逐一检查原 PDF 的局部扫描，位置和转录见 `data/vcd_visual_readings.csv`。

- 169 页补出的另一侧标号与已有读法相符。
- Site 845 第 29 页刊印的表头为 844C-19H，照片标为 845A-29X。
- Site 846 第 30 页刊印的表头为 846B-30X，图面照片标号读作 346B-30X，官方文字层亦如此。首字符位于印刷照片左沿，无法从现有数字副本确定是否缺墨。仍可由表头查到候选彩照。

先前已记录的两条共页描述、缺单张彩照的岩芯以及 846 第 41 页第二张照片，请同时参阅上一版 `../data/vcd_secondary_records.csv` 和 `../data/core_photo_gaps.csv`。

## 怎样核对涂片表

11 册涂片记录共 26 页，从真实印刷网格定位到 1156 个数据行和 25,194 格。11 站各有 19–25 个印刷字段，列头按原组和原序核对过所有站页。例如 `texture_clay` 表示 Texture data 组里的 Clay，`mineral_clay` 表示 Mineral 组里的 Clay。两个字段分别保存。站内后续行省略孔号的写法亦按来源保留。

| 资料 | 内容 |
|---|---|
| `data/smear_field_dictionary.csv` | 各站逐列的原刊分组、名称、位置和机器字段名 |
| `data/smear_grid_pages.csv` | 每页出处、原始 PDF SHA-256、印页、实际网格边界及文本配准方式 |
| `data/smear_text_registration.csv` | 844 第 2 页、845 第 2 页及 852 第 1 页有文字层错位。150 个逐行样品锚点同时记录官方文字坐标、印刷行中心和位移 |
| `data/smear_rows.csv` | 1156 行的样品标记、深度、岩性、OCR 原读、当前读法与页内行坐标 |
| `data/smear_cells.csv.gz` | 每格对应的字段、上下左右界、OCR 原字符、当前读法、判读状态与依据。坐标以 PDF 左上角为原点，单位为点 |
| `data/smear_visual_reviews.csv`、`data/smear_846_inherited_review.csv` | 本版新核 53 格，其中 34 格更改了 OCR 读法。另继承 Site 846 已有的 40 格校记。 |
| `data/smear_folio_readings.csv` | 从扫描页脚补读的 6 个印页编号 |
| `examples/Smear_853_row3.png`、`examples/Smear_853_row3.csv` | 原图截取的完整一行及各格文本和证据 |

星号、数字、空格与 D/M 等标记各自保留。549 个存在墨迹无文字或异常 OCR 字符的格子尚待人工核对。可在 `smear_cells.csv.gz` 中筛选 `reading_evidence = source text layer and located cell` 且 `status` 以 `check_` 开头或等于 `ink_without_text`。其他未逐格校对的 OCR 数字亦保留其机器判读状态。没有文字且墨迹很少的格子保留为空，不回填为零。已经核过的格子用 `edition_reading` 查当前读法，`source_ocr_literal` 始终可追溯。

## 运行

以下命令在本目录运行，`../../primary` 指包含 `VOLUME/` 的图版底本目录。依赖 Python 3.12、PyMuPDF、NumPy、SciPy 和 Pillow。仅重建光学裁片时只需 Python、PyMuPDF 和 Pillow。

```bash
python tools/export_regions.py ../../primary output --core 844B2H --role sediment_candidate
python tools/export_regions.py ../../primary output --roi 848B8H.L00.board_background.01
python tools/export_regions.py ../../primary all_rulers --all --role printed_ruler
python tools/export_smear_cell.py ../../primary S853.P01.R003 output/smear_row.png
python tools/export_smear_cell.py ../../primary S853.P01.R003.C19 output/smear_cell.png
```

完整重建如下。源表、人工校记或矩形发生变化时，应重新计算对应的检验文件。

```bash
python tools/segment_photos.py ../../primary --workers 4
python tools/verify_regions.py ../../primary --workers 4
python tools/vcd_identities.py ../../primary
python tools/smear_cells.py ../../primary
python tools/edition_metrics.py
python tools/qa_sheets.py ../../primary review_sheets
python tools/qa_atlas.py ../../primary examples/Leg138_optical_segmentation.pdf
```
