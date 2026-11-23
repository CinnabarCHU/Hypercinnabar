# Leg 138 编号出版图件

这个目录按图号取出四类原刊中的图体、题注或完整原页。读者可以检查原图的刻度、文字、图例、照片和印刷网点。图件中的信号是否有船上或岸上的电子数据，见[全航次图志](../../../data/figure_reproduction.csv)。本目录生成的黑白 SVG 描摹印刷墨迹，沿用原版坐标和字形，不增加图志中的数据重绘数。

## 所有图都能回到哪一页

| 原刊 | 编号图 | 图页记录 | 人工核定图体 | 机器候选 | 只回原页 | 已核准印刷描摹 |
|---|---:|---:|---:|---:|---:|---:|
| Scientific Prospectus | 3 | 3 | 3 | 0 | 0 | 2 |
| Preliminary Report | 36 | 47 | 47 | 0 | 0 | 23 |
| Initial Reports | 652 | 684 | 46 | 278 | 360 | 36 |
| Scientific Results | 515 | 555 | 16 | 146 | 393 | 9 |
| 合计 | 1,206 | 1,289 | 112 | 424 | 753 | 70 |

一幅跨页图占多条图页记录，同一张折页也可以收录不同图号。以上记录对应 70 份经 SHA-256 核对的原 PDF、1,045 个不同原页。88 幅图的所有已定位页均已人工核定图体，另 7 幅只核定了部分页。388 幅目前只有机器候选，723 幅仅提供原页。可以从[编号图索引](data/artwork_figures.csv)查图号，从[图页索引](data/artwork_pages.csv)查看各页的边界、图像尺寸、读法和原刊链接。

## 可直接打开的原像素样例

| 图件 | 出版物中的内容 | 分离结果 |
|---|---|---|
| SP Figure 2 | 海洋动力地形与环流示意图，长题注与图体有间隔 | [原生裁图](examples/SP.F2/SP.F2.p012.body.png) · [题注](examples/SP.F2/SP.F2.p012.caption.png) · [印刷墨迹 SVG](examples/SP.F2/SP.F2.p012.ink.svg) · [坐标和哈希](examples/SP.F2/SP.F2.manifest.json) |
| IR Site 844，Figure 12 | 印在黑白页上的岩芯半色调照片，保留与图同印的标尺 | [原生裁图](examples/IR09.F12/IR09.F12.p019.body.png) · [题注](examples/IR09.F12/IR09.F12.p019.caption.png) · [坐标和哈希](examples/IR09.F12/IR09.F12.manifest.json) |
| PR Figure 5 | 五面板图的题注占左下空格，右下仍有数据 | [完整图体外包矩形](examples/PR.F5/PR.F5.p036.body.png) · [独立透明通道](examples/PR.F5/PR.F5.p036.body-alpha.png) · [题注](examples/PR.F5/PR.F5.p036.caption.png) · [坐标和哈希](examples/PR.F5/PR.F5.manifest.json) |

## 在本地取图

以下命令从项目的 `Leg138/` 目录执行。需要 Python 3.11 或更新版本、PyMuPDF、Pillow、NumPy 和 SciPy。数据目录只保存坐标、核验记录以及上面三组样例。原 PDF 可以由本地备份提供，也可以按原路径从索引中的公开来源取回。

```sh
# 用现有的公开版本拉取器取一个源 PDF。下面示范 Site 844 的站章。
python tools/fetch_source.py ir/primary/VOLUME/CHAPTERS/ir138_09.pdf --root .

# 取原生图体和题注，照片保留原扫描灰阶。
python figures/core/published_artwork/tools/export_artwork.py . IR09.F12 output/figure12

# 对已核准的线图同时输出印刷墨迹 SVG 及对齐结果。
python figures/core/published_artwork/tools/export_artwork.py . SP.F2 output/sp2 --trace

# 主动查看一处未人审的机器图框。
python figures/core/published_artwork/tools/export_artwork.py . IR02.F03 output/trial --accept-candidate

# 单独导出图首或续页的完整出版页，页码从 1 起。
python figures/core/published_artwork/tools/export_artwork.py . SR.C01.FIGURE1 output/source --component page --page 3
```

第一项位置参数是包含 `ir/primary`、`sr/primary`、`sppr/primary`、`plates/primary` 等原路径的目录。对单幅图只需取回其索引记录所列的源 PDF。导出时会先对照哈希，防止不同发布版本混入。

默认 `--component auto` 导出人工核定的图体及同页可定位的题注。对多页图逐页判断。没有足够证据或尚待人审的页导出完整原刊页 PDF。只有加 `--accept-candidate` 才会按机器候选边界裁图，清单保留该等级。可用 `--component caption` 单独取题注。机器提取的题注坐标只能确认 OCR 匹配到的行，有时只到首行。初报另有 7 个续页原本未重印题注。对于没有独立题注框的页，清单标注了完整原页回退。

## 如何检查读法

- PDF 边界顺序为 `x0,y0,x1,y1`，左上角为原点，单位为 point。嵌入图的仿射变换映射到原生像素。裁图采用向外取整的半开矩形，保留边缘像素。所有 1,289 个已定位图页的底本均为一个覆盖整页的原嵌图。导出程序核对原 PDF、嵌图流和裁图哈希，并重读 PNG 或 TIFF 验证解码像素逐点相同。清单中的 PDF 哈希标识原始见证，裁图文件哈希标识这一次导出的无损编码。
- 10 个初报五面板图保留原像素外包矩形、独立题注及单独的 alpha 文件。用该文件作原生裁图的透明通道时，值 0 隐藏题注，255 保留原扫描，原裁图文件始终可以直接打开。
- 单色描摹只对经过插图类型核对的 70 个图页启用。把原生像素转换为灰度，以 `L < 128` 定义印刷墨迹，将逐行连续墨迹合并为整数像素边界的矩形路径。SVG 回渲到原图尺寸后，与该二值层逐像素相同。[逐图签验](data/trace_checks.csv)记录二值层与回渲层的哈希、黑像素数和错位数。细灰线、墨迹浓淡、扫描噪声、纸痕以及原件印刷网点应首先对照保留的原生裁图。描摹文件不提供仪器测量值或语义化坐标轴。
- 自动提议利用单一已定位图号、题注上方空白带、图像墨迹及正文排除条件。IR、SR 各随机抽验 16 个首轮候选，32 个框在原页上的图体与题注均可分辨。单独追查的 Site 845 Figure 5 把 OCR 漏掉的页眉圈进图体，已按实印位置修正，并收紧自动规则。[抽验明细](data/candidate_audit.csv) · [人工边界](data/manual_audit.csv) · [IR 岩性图与折页](data/manual_ir.csv) · [SP 与 PR](data/manual_sppr.csv)。32 个合格样本不足以为其余 424 条候选提供逐图保证。
- 已确认的 13 个同页折页图体都有独立外框、站号、刻度、图例和完整题注。保留纹样和扫描纸痕。半色调岩芯图保持与报告中一致的标尺、朝向和网点，沉积物颜色另见航次原生彩照档案。

拥有 70 份原 PDF 的本地目录可重做整卷检测、套用人工校读坐标并复核全部许可的 SVG。折页底图约有 1.33 亿像素，核验默认串行处理。

```sh
python figures/core/published_artwork/tools/find_artwork.py . --workers 2
python figures/core/published_artwork/tools/verify_artwork.py .
```

[检测覆盖](data/coverage.json) · [最终核验与计数](data/verification.json)
