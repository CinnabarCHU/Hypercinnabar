# Leg 138 随盘数据复核第二版

本版补足第一版中只按文字保留的孔隙水、测井，以及 Site 844 的二进制颜色文件。所有文件位置相对于 IR 随盘 DATA 根目录。行号从 1 开始，二进制下载字节地址从 0 开始。原始十进制字符、限定符、重复的列名与版次差异均可回查。

## 孔隙水

`water.csv.gz` 收录 11 份 CHEM/INTERSTI 的 149 行。每行给出原刊录的样品标识、区间、深度、pH 与化学字段；继承上方孔号的小表另存孔标题行。某站没有某列时，相应字段为空。源字符 `**`、`-`、`_`、`<10`、`<<10` 均保留。原表头与附注见 `native_headers.csv.gz`，数字分发件逐文件 SHA-256 见 `water_sources.csv`。

- 对照随盘 TABLES 的同名章表，149 行全部按孔、芯、段、取样区间配对。在两版均有的 2,056 个字段中，2,044 个词元逐字相同。差异集中在 Site 844 的 12 个深度。比如 CHEM 第 12 行为 19.0，TABLES 的第 13 行与纸面 p.158 同为 119.0。三方逐项记录见 `water_print_depths844.csv`，源表数值继续单独保留。
- `water_print_units.csv` 逐站逐字段记录印本单位与页码，配有从原 PDF 独立提取的主表和续表表头。ASCII 表头中出现 mM、mmM 和省略单位的不同情况。Site 851 印本自身写成“µ m”；Site 844 印本给 salinity 列写了 mM，Site 847 写 ‰。跨站合并时应选择并记录版本。
- Site 848 表 10 续页 p.717 刊有 10 个氨值，均为 <10 µM。CHEM 与 TABLES 电子表都省略氨列。`water_print_only848.csv` 来自纸面影像，按芯、段、区间、顺序、Li 和 Si 复核配对。印本 B 孔段落里的后 6 个样品在 CHEM 写为 A 孔，两种孔号分别保留。原影像裁片见 `site848_table10_continued.png`。

## 测井

`log_sources.csv` 索引 65 份随盘测井产品，`logs/` 按原文件分别提供 CSV。不要假定两个站的同名工具串含有相同列或相同顺序。原头只给站号时，索引中的孔号留空。按文件、头部行和列号释义见 `log_dictionary.csv.gz`。重复名使用列位置区分，如 GD__1、GD__2；印错的 SI02、AL203、CACAO3/CAO、重复 XRF 列名亦保留。附盘 READ_DIR/LOGS.ACR 与 OXIDES.LOG 给出的说明与单位可逐条查到。

共 112,810 个记录，占 135,092 个物理数据行，1,280,581 个数据格全部回读并逐格核对原文件。OX_ERROR 每个深度跨三行，区分 FACT、各氧化物下限与上限。原始栏位共有 70,104 个 -999.2500 词元及 44 个满栏星号。两种符号均保留，不进入计算复核。

- `log_oxide_bounds.csv` 按深度匹配 OXIDES 与 OX_ERROR。60,727 对可数值检验，其中 58,397 个公布值落在公布界限内。按元素、站点记录具备完整数据的比例。
- `log_ratio_tests.csv` 把 ACT_GST 的四个指示比值与随盘 LOGS.ACR 所列公式核对，分母、分子和公布结果均纳入小数点后四位的舍入范围。PIR 的 16,513 个可检记录均不能用原定义的无量纲比值解释，另验 100 倍比值时有 13,192 个落入舍入范围。这是按版本记录的计算结果，公开值未作整体重标度。同文件内 LIR、IIR、SIR 的通过计数另列。

## Site 844 二进制颜色文件

`binary_color844.csv.gz` 给出 COL844B.FIN 内的 6,441 行及 9 列浮点值，每格对应的原分发文件地址和宽度在 `binary_color_byte_map.csv.gz`。标签区与长度字段分别检出九个表头、九次 6441。六个字段的 38,646 个大端单精度数值序列经原始字节比对，与 COL844BH.FIN 全部 5,289 行和 COL844BX.FIN 第 4–1,155 行吻合。另三列是表头所列的红/蓝、红外/红、红外/蓝。19,323 个比值中有 19,321 个按单精度除法逐位一致，首行两值保留二进制自身给出的精度。BX 前三行在 ASCII 中单列。

文件含 CRLF，通过换行映射可读取浮点数组。两个单元中原浮点编码本身含 0D0A，逆变换需要独立的 ASCII 或计算值来区分，两处有专门字节校记。源文件 SHA-256、输入大小、校验数量在 `binary_verification.json`。数值区以外的容器设置和图形状态仍待格式文档。后人如取得另一载体，可据字节地址直接核对这一恢复。

## 拼接及光谱异文

- Site 844 的 COREDATA/844.ADJ 给 3H 加 2.25 m，给 4H 减 8.55 m。在 SPLICE.844 指定的 B 孔 [18.3, 21.5) mcd 内两个岩芯各有 157 行。站章 p.121 记载取出 3H 后钻杆未前进，4H 重新取了同一地层；p.146 再次讨论双重取芯。已发表 MCD 的这个区间只收录 3H。增加“此段采用 3H”的显式选择后，Site 844 全部 12,586 行恢复公布顺序。此选择由公布结果和开钻记录共同支持。工作流中的决策、另一份岩芯的观测分别见 `splice844_overlap.csv`。
- `spectrum_file_checks.csv.gz` 给 3,803 个 REF 的独立波长带核验；`optical_exceptions.csv.gz` 列出有定位的 4,200 个配对样品，至少一个波段偏差 >0.1 个百分点，其中 3,839 个在 844B、37 个在 845A、324 个在 846C。严格按印出的样品号和出现序配对时，2,568 个 REF 行、406 个 TEN 行缺少对应方。Site 850 两个文件缺 END 标识，数据行均完整记录。现有版本无法确定 4,200 行偏差的处理历史。
- Site 849 的 849C02H2.REF 把航次/站号写成 849/0848，文件头也沿用 848 的原始文件名。以目录 849 作为独立候选，与 138/849 对应 TEN 的 36 行 × 10 波段全部在 0.05 个百分点内；将同样区间与 Site 848 的 848C02H2.REF 比较，36 行中没有任何一行 511 通道全同。两套身份和逐行证据在 `spectrum849_identity_hypothesis.csv`。
- Site 854 的 854C06H6.REF 与 854X06H6.REF 刊有相同扫描时间、原仪器文件名与逐行样品标识。49 对样品的每一对均有反射值不同，最大差 24.0 个百分点，两套均无匹配的 TEN 行。可据此判定它们公布了不同值，独立测量与同次测量的重新处理仍需原始计数或处理日志区分。`spectrum854_variant_rows.csv` 和 `spectrum_duplicate_summary.json` 记录逐行与全盘核验。

## 复建

下述命令从 `leg138_all` 目录运行。前四项中的字段抽取、二进制恢复、测井数值核对仅依赖 Python 标准库。印本比勘/裁图使用 PyMuPDF 与 Pillow，波段核对使用 NumPy。涉及 IR 章表的命令会读取 IR 分库的章 PDF、按原盘 TABLES 生成的具名表及原 Site 846 转录。

```sh
python -B disc/core/edition2/extract_fields.py disc/primary disc/core/edition2
python -B disc/core/edition2/decode_color844.py disc/primary disc/core/edition2
python -B disc/core/edition2/verify_logs.py disc/primary disc/core/edition2
python -B disc/core/edition2/collate_water.py ir disc/core/edition2
python -B disc/core/edition2/render_water_evidence.py ir disc/core/edition2
python -B disc/core/edition2/check_anomalies.py disc/primary ir disc/core/edition2
python -B disc/core/edition2/check_spectrum_duplicates.py disc/primary disc/core/edition2
```
