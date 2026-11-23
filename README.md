# ODP Leg 138 · 赤道东太平洋

本分支整理 1991 年 Ocean Drilling Program Leg 138 的航前计划、航后初报、Initial Reports、Scientific Results 和随盘材料。12 个拟钻站、11 个实钻站、42 个孔，以及各章自己的图表和原页都是独立检索入口。

| 入口 | 内容 |
|---|---|
| [现代版分册目录](Leg138/publication/chapters/catalog.csv) | 76 份 PDF 共 3,622 页、合计约 15.2 MiB，按来源页保留现代正文、具名表和已核的图件对照。选取 [Site 846 站章](Leg138/publication/chapters/IR.C11.pdf)、[航前计划](Leg138/publication/chapters/SP.pdf)、[初报](Leg138/publication/chapters/PR.pdf) 或 [Shackleton 等的年代学章](Leg138/publication/chapters/SR.C06.pdf) 即可直接翻阅。章内原刊链接使用原来源物理页号。 |
| [84 页逐站校读本](Leg138/publication/ODP138_Leg_Report_Edition.pdf) | 航次与站点、12 张拟钻站卡、11 站速率图对校、碳酸盐重复测量、岩芯与标尺分离。 |
| [11 站复合地层柱图](Leg138/figures/core/composite_v2/Leg138_PR_Composite_Atlas.pdf) | 22 个原图页与独立重画并排，含 66 个密度、磁化率与反射率面板。图旁区分发布值、显示滤波及原刊解释层。 |
| [使用、导出和复建](Leg138/README.md) | 双击离线浏览，或启动本机 JSON／CSV API。可按某一站、图表、孔、数据发布版本或文件 SHA-256 回溯。 |
| [出版图件提取](Leg138/figures/core/published_artwork/README.md) | 逐图分列原页、已核图框和机器候选。可从原 PDF 裁出岩芯照片与图注，并把经验证的黑白线图描成可缩放的 SVG。 |
| [逐图验收与证据](Leg138/data/FIGURES.md) | 1,206 幅正式编号图逐幅登记原页、可用数据、重绘范围和待核状态，各站的岩性解释层和物性层分项说明。 |
| [原分发件索引](Leg138/data/source_package_checks.json) | 5,425 项基础来源的文件长度和哈希能逐件核对。原件可按章、载体和前缀获取，新增外部对勘见证单列。 |

```sh
git clone --single-branch --branch odp-leg138 https://github.com/CinnabarCHU/Hypercinnabar.git
cd Hypercinnabar/Leg138
python tools/build_catalog.py
python tools/verify_catalog.py
python tools/verify_edition2_catalog.py
python tools/serve.py
```

本地服务入口为 <http://127.0.0.1:8138/>。也可直接双击 `Leg138/browse.html` 按站查询和导出，或双击 `Leg138/catalog.html` 查看全航次的图表、岩芯和古位置。GitHub 在线浏览文件时可以直接查看分册 PDF。原底本和嵌入整页见证的重排大卷可在本地独立重建。

报告的刊值、推测的 OCR 读法、重复测定、修订版本和从图面取出的值各有独立标记。例如 Site 853 原刊两次 CaCO₃ 读数为 87.90% 与 87.07%，原表差栏为 0.17 个百分点；校记另给复算差 0.83。引用某项数据时请一并引用该条的作者、章节、表号和发布版本。来源站提供[卷目与书目](https://www-odp.tamu.edu/publications/citations/cite138.html)。本仓库的代码许可与原出版物各自的署名、权利说明分别保留。
