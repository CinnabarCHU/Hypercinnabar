# Leg 138 岩芯记录与图版

11 个站点各自保留岩芯描述、涂片记录、按岩芯发布的彩色照片，以及站章引用的卷后折页。岩芯描述是船上把观察、划分、解释和仪器曲线编到一起的记录。涂片表记载显微观察和成分估计。折页是依据物性、反射率和深度模型制作的图件。分别保存图版、已经发布的彩照和裁片，可保留每份资料的身份及核对依据。

## 文件

| 文件 | 内容 |
|---|---|
| `data/plate_sources.csv` | 617 份发布 PDF 的原址、相对路径、字节数、SHA-256 和页数 |
| `data/plate_directory_witness.csv` | 官方照片目录网页的出处与校验值；个别 PDF 扩展名为小写 |
| `data/station_summary.csv` | 每站原件数、描述页数、涂片页数和折页章节/图号 |
| `data/vcd_pages.csv` | 592 张岩芯描述页的表头、页内照片编号、查到的独立照片及识别证据。仅从表头推测的照片另列于 `form_based_photo_candidate` |
| `data/vcd_secondary_records.csv` 和 `data/core_photo_gaps.csv` | 共页记录、附注，以及岩芯作业表有记录而官方照片目录缺单张照片的六块岩芯 |
| `data/vcd_checked_headers.csv` | 人工对照原件所能识别的 21 个疑难页眉。原附文本层的识读仍在逐页目录中保留 |
| `data/smear_pages.csv` | 11 本涂片表的 26 个页定位；行、列及成分数值仍待转录与校对 |
| `data/foldouts.csv` | 两张卷后折页的 13 幅图，包括 11 个站各一幅和两幅航次综合图；提供图注定位坐标 |
| `data/plate_page_text.jsonl.gz` | 620 页描述、涂片和折页的原 PDF 文本层及逐页出处。可用来检索，识读、段落顺序和表格列对应关系仍需要回原页核实 |
| `data/native_photo_catalog.csv` | 593 张彩照的像素尺寸、PDF 图像对象、色彩空间、压缩方式与嵌入 JPEG 的校验值 |
| `data/optical_regions.csv` | 11 张示范图各两个核对过的矩形、出处、像素尺寸和源哈希 |
| `optical/Optical_windows_Leg138.pdf` | 4 页彩色示例图册。每站展示第 3 节的沉积物内窗和相同纵向范围的厘米尺，链接至官方图版 |
| `optical/patches.csv`、`optical/row_rgb.csv`、`optical/*.png` | 22 个无损 PNG、裁片像素与文件哈希，以及 11 个沉积物裁片每行印刷照 R/G/B 均值 |
| `data/plate_verification.json` | 全部底本、原始 JPEG 数据流、索引和 22 个 PNG 的一致性检验结果 |

原 PDF 的彩色 JPEG 是历史数字分发件。PDF 自带一张 JPEG，可以直接取其字节流，无需将 PDF 截屏、重新缩放或再压缩。分发图像没有为本包建立辐射定标或统一白平衡；JPEG 分量与船载仪器测得的光谱反射率需分别使用。示范只截取核对过的内窗与标尺部分，未进行全岩芯分割。PNG 裁片无损保存解码后的像素；曝光、印片与数字化造成的误差仍存在。矩形以 JPEG 左上角为原点，左、上包含，右、下不含。行号是图像原生像素 y，未换算岩芯深度。

## 校记例

- Site 845 描述书 PDF 第 29 页的表头读作 **Site 844, Hole C, Core 19H**，右栏照片标示 **845A-29X**。逐页目录同时保留两种读法。检查时按页面原样并排看。
- Site 846 描述书第 41 页包含 846B-42X 和 846B-43X，两者均有独立彩照。该站有 89 张描述页和 90 张彩照。
- Site 847 描述书第 27 页还包含 **847B-27X** 的第二张记录表，印刷区间为 241.5–251.2 mbsf。IR 第 12 章随盘岩芯作业表第 36 行记为 241.5–247.0 mbsf，回收 0.04 m。两份发布记录的数值及出处应同时保留。
- 两张较小的彩照 846D20X 和 851C1H 原文件名扩展名为 `.pdf`，两者原生高度均为 1063 像素。其余 591 张高度为 2700 像素。目录或抽取程序应保留大小写。

## 复算

以下命令从本目录运行。依赖 Python 3、PyMuPDF、Pillow 和 NumPy。`../primary` 是包含 `VOLUME/` 子目录的原件目录。阅读精简包时可先按源表下载原件或运行下载程序。

```bash
python tools/fetch_plates.py ../primary data
python tools/index_print_assets.py ../primary data
python tools/optical_windows.py ../primary optical
python tools/optical_atlas.py ../primary optical/Optical_windows_Leg138.pdf
python tools/verify_plates.py ../primary .
```

`optical_windows.py --whole` 可另外导出 11 张示例的嵌入 JPEG。需要从其他彩照导出时，脚本的 `get_native(path)` 返回解码图像、保真的 JPEG 字节流和原 PDF 对象信息。核验其他照片仍须回看原图，重新定出岩芯组织、边缘、空隙、标签与标尺的坐标。
