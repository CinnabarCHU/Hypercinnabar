# Leg 138 Scientific Results · 第二轮校勘

本次核验针对出版物的图表身份与起始页。编排、整幅图及续页可在对应原件中查看。47 章共 888 个 PDF 叶的原有识别层用于发现图、表、图版及附录，再逐项查读原版图注或标题裁片。校订视图有 809 个有效对象，另外保留 3 个曾误入初版的引用，用于复查历史。

## 阅读顺序

- `data/objects.csv` 同时保存活跃与撤销的键、原版坐标、物理叶和印页、以前的页号、证据图文件和格号。首行文字供搜索，整段图注与各个符号仍可能有识别误差。
- `atlas/` 提供 17 张联系表及 1 张补页。格号按从左到右、从上到下的顺序计数。正文引用、坐标错位、侧转表头及标题被拆成多块的情况可与新定位对读。
- `data/changes.csv`、`data/chapter_coverage.csv` 分别列出变化和逐章覆盖。最初的 721 个自动候选逐一回看原版，718 个可确认，3 个是正文引用。另补 21 个附录标题，改正 5 个起始物理叶。重印第 47 章图 3 的页号本来正确，但早先落到了该页的正文，已换用真图注。
- `data/excluded_reference_mentions.csv` 列出超出本章已确认编号、或指向集合表的文字线索。化石文献里的图号、图版中的分图与其他论文中的表号仍可追查。图或表完全没有标题、正文从不引用或原页识别彻底失效时，检索无法据此证明全卷没有遗漏。
- `data/print_datasets.csv`、`data/print_proofs.csv` 与 `print/` 给出新增的 7 张印表、70 行，各行回链至印页，逐表保有裁切范围和原刊见证图。尤其可对读两篇论文怎样区分观测、反演及计算层次。
- `data/row_apparatus.jsonl` 保留初版 8 条分栏有疑的**原文**及逐项建议。建议没有覆盖既有的随盘记录。另见 `data/ch23_depth_crosschecks.csv`、`data/row_witness_lines.csv` 及 `data/witnesses.csv`。9 个外部数据集以单独版本存放，其原始字节长度及 SHA-256 已复核，完整引文、作者、许可和出处保存在解压后的 PANGAEA 头部。
- `data/historical_rotation_stages.csv` 从 Pisias、Mayer 与 Mix 第 1 章表 1 的三个站群、六个转动阶段展开 30 条站点—阶段对应关系，其中 22 条属于本航次的 11 站。公开数值列采用北正、东正的极点经纬度，保留作者给定的角速度符号。原表重排见 `print/SR.C01.TABLE1.csv`。这些是当年的模型参数，各阶段按印本适用时限保留。

## 三处值得对读的证据

**第 23 章表 3。** 原附件的五条生物事件行各有十一个深度词元，而表头只给五站、各两个位置。第 23 章纸刊第 4 叶只印出开头一页；这五行都在随盘完整版中。对读 Moore 第 11 章 Tables 2–6 的五站资料，可以将第 2 至 11 个词元分别定位到 844–848。25 个事件—站点组合中有 19 组上下界与 Moore 的站表完全相符，4 组数值有差，2 组原盘列为 n.a 且站表无该事件；保留原盘数值。首词元仍单独保存，成因待考。PANGAEA 第 23 章版本 806678 给出另一种分列，其站别读数并未验证原盘首词元所属字段。

**第 35 章附录 B 和第 15 章表 9。** PANGAEA 806757 支持 847B、44.84 mcd 一行的两处空格位置和 850B、378.56 mcd 一行断开的 `18 .86`。两行可恢复字段排列；附录使用的可疑值后缀 `s` 仍按原盘保留。Site 677 的源行把孔号、间隔片段和部分数据排在一起，最后一项浮游有孔虫碳同位素缺失。早期研究中同一 mbsf 有两个孔的记录；相符的局部数值不足以补齐原件，校勘视图仅析出可以辨识的字段。

**第 36 章表 1。** 印本三列表头为 844、844、846。摘要与 Methods 点名的是 844、846、851，表内还区分东西剖面。CSV 按印本的三列依次保存，表注另记正文站序。这样既能检索作者的数据，也能回到真实的版次差异。

## 查询与复建

命令行、HTTP 与 CSV 共用同一校勘视图。Python 3.10+ 标准库即可查询，默认只监听本机。

```sh
python tools/api.py '/objects?chapter=17&kind=appendix'
python tools/api.py '/objects?status=rejected'
python tools/api.py '/row-apparatus/SR.C35.APPENDIXB?line=2065'
python tools/api.py '/print/SR.C03.TABLE6.PRINT.E2'
python tools/api.py '/rotation-stages?site=846'
python tools/api.py --serve --port 1387
```

`/coverage` 与 `/coverage/{chapter}` 给出总量或逐章统计，`/objects/{item_id}` 返回一个对象的坐标与修改记录，`/changes` 列出变化。GET 响应为 UTF-8 JSON。发布包如另有统一 API，也可直接纳入这些 CSV、JSONL 与键。

从同一源备份复建时，按如下顺序运行。影像生成依赖 PyMuPDF、Pillow；旋转表初次自动找框的辅助脚本另用 Tesseract。作品身份、图注开头和七张表的编辑判断保存在源码和校勘记录中。

```sh
python tools/collect_captions.py
python tools/make_atlas.py
python tools/build_review.py
python tools/review_references.py
python tools/print_tables.py
python tools/print_proofs.py
python tools/export_rotation_parameters.py
python tools/resolve_rows.py
python tools/validate.py
```

`tools/fetch_witnesses.py` 可以另行核取在 PANGAEA 发布的文件。正文初版、随盘原目录和先前的校记可以独立使用。此轮未完成全部图注逐字精校、续页逐叶编目、全卷印表逐格转录或全图重绘。
