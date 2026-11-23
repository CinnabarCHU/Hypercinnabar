# Initial Reports · Leg 138 随盘仪器数据与船上工作流

本目录收录 ODP 官方数字分发树中除 TABLES 以外的文件。站章随盘表另由 IR 卷目录管理。三个互补入口是 sources.csv（来源和哈希）、site_summary.csv（各站资料覆盖）和 family_summary.csv（各类数据的解析范围）。原始文件位于独立底本包中；仅需少数数据时可以从官方源按文件拉取。这里的“原件”指取得的数字分发文件。当前的目录清单以网页分发版本为界，不推断物理光盘镜像中每个扇区的内容。

## 分发文件与字段

- sources.csv 对应 COREDATA、PROGRAMS、READ_DIR、README_1ST.TXT 和 SITE_844 至 SITE_854 的完整官方目录清单。每份文件均记录 URL、字节数、SHA-256 和取得方式。已校验的 Site 846 旧分发件复用原字节。listed_paths.txt 与 directory_listings.jsonl.gz 分别保存文件名和 90 个官方目录索引的原始 HTML。BASE64 解码后可按每条记录的 SHA-256 复核目录快照。
- file_index.csv.gz 按路径标明仪器或资料类别、记录性质、解析到的数值记录数、保留的源文本行数和异常行数。原刊身份由来源 SHA-256、文件内行号和字段共同定位。文件行号从 1 起算；二进制块使用零起算字节偏移。
- carbon.csv.gz 列出各站 CARBON 原文件的 2,296 条刊载行。666 行有有机碳百分比。空位保留为空，原文小数精度作为字符串保留。Site 854 的 63 条记录只有无机碳和碳酸盐的刊载栏。所有数值连同原孔、岩芯、段号、取样区间、mbsf 和 mcd 原样留存。两册不同表中的同一样品仍可分别引用。
- physical_index.csv.gz、thermal_conductivity.csv.gz、vane_shear.csv.gz、compressional_velocity*.csv.gz 将可确认字段的物性表逐行转录。844 的 COMPVEL 只有深度与校正波速两列，单列一份。854 的官方 PP 目录未列 COMPVEL。
- core_offsets.csv.gz 共 599 条岩芯行，保留孔深与复合深度并列。core_sections.csv.gz 收录 COREDATA 中 39 个原文件的 585 条切段行。854 的三孔可查到 854.ADJ 和 DEPTH854.FIN，该目录没有对应的 CORE854*.DAT。first_grape_depth.csv.gz 记录各芯首次 GRAPE 测量深度的转换关系。
- age_models.csv.gz 保留各站 AGE、MCD_AGE、MBSF_AGE 的不同年代学序列，共 637 条。低分辨率 AGE 中的原始定年事件注也纳入。depth_transform.csv.gz 存 MCD–MBSF 对应点；splice.csv.gz 存各段开始位置和孔序号。年代学估计与取芯位置分别保存。
- GRAPE DAT 保存分发的较早密度记录，包含同一深度的重复读取与两个原刊处理整数。847B 与 847C 的 33,320 行在 mbsf 后还有一个 N 字符，作为 record_flag 原样保留。FIN 包含复合深度、刊出的未校正密度、校正密度和校正后平滑密度。MCD 为跨孔拼接，MBS 是重标至等效海底以下深度的跨孔产品。
- spectrum_files.csv.gz 索引每个岩芯段的 511 通道反射率文件，保留测量头、光谱校准式和历史仪器计数文件名。分发树中无这些头部点名的 .raw 计数文件。全航次含 3,803 份光谱、124,873 行。850B30X6.REF 与 850B36X2.REF 保留数据行但没有 END OF DATA 尾标。849C02H2.REF 的 36 行在目录中属于 849，行内却写作航次 849、站号 0848；两层标识并存。TEN 与 FIN 为波段汇总文件。844 孔 B 的不带 H/X 后缀的 COL844B.FIN 含二进制数据，内嵌标签可读；未给它赋予数值字段。BH、BX 两份同站文件分别保留。
- 日志与间隙水文件的行布局会随站号、工具或产品改变。原文字段头在 ascii_headers.csv.gz，相应文件通过 read_disc.py 可逐行导出。多行测井曲线及间隙水变量本轮未作跨站列对齐。缺项、重复、哨兵和原文格式均保留。

## 三种可重跑的检查

1. **GRAPE 刊载序列对应。** 对各孔 FIN 按 SPLICE 的左闭右开区间及孔号取行，按区间与原行次排序。11 站 GRAPE.MCD 的 121,065 个刊载行均可定位回 FIN 源行，样品、MCD 与未校正密度一致。将 MCD 的平滑密度按 GRAPECOR 的校正式转换，全部行的差异不超过 FIN 刊载精度的半单位。10 个站可照原序完整重建。844 的选行规则另外选出 GR844B.FIN 第 1305–1461 行，共 157 行。未改变两边的源表；逐行映射及该段另列在 replay/grape_source_lines.csv.gz，按站汇总在 replay/splice_membership.csv。
2. **历史 Fortran 重放。** 五个 F77 程序以 GNU Fortran 14.2.0 的保守编译选项重放，可确认的三处兼容性修改分别是消去重复类型声明、给被舍弃的实数输入字段正确声明类型、把绝对数据路径改作本机工作目录；原文件完整保留。修补补丁、编译条件及双方源码哈希在 replay/。MBSFSPLI 在有分发 MBS 的 10 站全部逐字节复现，比较前只统一换行。854 可从原 MCD 和转换表生成 3,596 行，官方目录未列可用于比对的 GR854.MBS。DAT 经 FIXGRAPE、DEP_ADJ 和 GRAPECOR 再与 42 份孔级 FIN 比较，845A 在刊出精度逐行相同；其余 41 孔分别保留配对数、各字段一致数和两侧独有数。同一套 SPLICE 可从 FIN 读取校正密度，其数值与 README 所述未校正 MCD 产品所属阶段不同。replay/grape_replay.csv 给出三条检查路线的结果。重算出的文件仍属重算结果。
3. **光谱和波段。** replay/reflectance_511_to_ten.csv 按各 .REF 的校准式把像元映射到波长，按 450–500 nm 起的十个 50 nm 左闭右开区间求平均并核对 TEN。replay/reflectance_ten_to_three.csv 将各个可读 FIN 的刊载三波段分别与 TEN 第 1、5、9 波段比较。样品按孔、芯、芯型、段、取样区间与出现次数配对，两边 mbsf 的差异另记。全航次有 122,305 个光谱行与 TEN 在同一刊载样品身份、区间及出现次序下配对，共 1,223,050 个波段比较，其中 1,183,331 个在 0.1 个百分点以内。该阈值仅描述核对差距；原表数值与来源仍然保留。

## 调用

Python 3.11 或更新版本可按路径查验、拉取和导出单个数据表。下列 PRIMARY 指底本包内含 COREDATA、SITE_844 等目录的父目录。

~~~bash
python fetch_sources.py PRIMARY --verify-only
python fetch_sources.py PRIMARY --prefix SITE_849/CHEM/
python read_disc.py PRIMARY SITE_849/CHEM/CARBON.849 > Site849_carbon.csv
python read_disc.py PRIMARY SITE_846/GRAPE/GR846B.DAT --fetch > Site846B_GRAPE.csv
python check_splice_membership.py PRIMARY replay
python check_optics.py PRIMARY replay
python replay_grape.py PRIMARY replay
~~~

check_optics.py 使用 NumPy。重放程序需 GNU Fortran，可用 FC 和 FC_EXTRA_FLAGS 指定本地编译器。read_disc.py 只把已确认布局的字段赋名，其他文本可依文件和源行检索。逐行导出时 row_status 和尾列保存所有未能按模板解出的行。公开分发索引来源为 ODP Leg 138 Initial Reports 的 VOLUME/DATA/，其 README_1ST.TXT 随底本收录。
