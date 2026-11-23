# ODP Leg 138 · Site 846 原报告数据目录

打开 `Site846.sqlite` 可按原章查图、查表及出处。若只想浏览，先用电子表格打开 `report-catalogue.csv`，按章节或原表号筛选。21 张编号表的通用 CSV 在 `data/tables/`。这三种入口均可离线使用。

底本为 Shipboard Scientific Party 的 1992 年 *Site 846* 站章（印本第 265–333 页）、所附 CD-ROM、卷后折页，以及第 505–593 页的岩芯描述和第 669–671 页的涂片表。[原站章](https://doi.org/10.2973/odp.proc.ir.138.111.1992) · [光盘说明](https://www-odp.tamu.edu/publications/138_IR/VOLUME/DATA/README_1ST.TXT)

## 这一次核对了什么

| 对象 | 保存的内容 |
| --- | --- |
| 21 张编号表 | 每张一张 SQL 表和一个 CSV。17 张有同号原始电子表，原始字节也在 `original-tables/`。表 2、11、19、21 分别从印本第 271、301、314、321 页转录 |
| 52 幅编号图 | 每幅有原号、章节、出处、英文短题、图注转录和中文说明。跨页图逐页定位。图 21 指向折页。注明各图中可从表取得、只能图读以及仍需查找的部分 |
| 其他印页 | 章首四孔资料、第 285 页无编号年代表、3 页涂片表、89 页岩芯描述与 90 份单芯照片之间的索引，以及 9 张未编号测井图版 |
| 663 份随盘文件 | 逐文件列出站章数据、相关共用文件、程序与说明的原目录、网址、SHA-256 和数据含义。每份均可从章节目录查到。同一文件可以和多节相关 |

表 10、13–18 在正文中注明随盘收录，目录将其定位为“正文引述”。其余 14 张编号表可在所列印页查到。每张表的数字保存为文本，保留小数末位、缺项、原始符号和标签。这里的 2,334 行包括数据、区间、合计和续行。可用 `row_kind` 筛选，做数值运算时自行选择需要转换的字段。空白格在数据表中是空字符串。

图中能追查到数值输入的轨道与仅能估读的轨道，可以同属一幅图。例如，图 5 的岩性亚单元界限有正文出处，图形岩性栏另存为印图分段。图 7 的原图标明曲线已经平滑。可查各孔的电子数据，也可以单独查从印图读取的 GRAPE 和磁化率。图 45 的 19 个点只取自实线可分辨的中段，保留了像素位置、墨迹宽度和坐标标定方法。

## 按章节或表号查询

`T11` 是本章表 11，`t11` 是它的实际数据表。`F07` 是图 7。`open_page` 可直接给出带 PDF 页号的官方链接。原印本页码与阅读器从 1 开始的页号均有保存。

```sql
SELECT item_id, title, locator, available, data_note
FROM report_catalogue WHERE section = 'Organic geochemistry'
ORDER BY kind DESC, number;

SELECT sample, run_1_carbonate_pct, run_2_carbonate_pct,
       run_3_carbonate_pct, printed_absolute_difference_pct
FROM t11 WHERE edition_row = 4;

SELECT sql_name, role FROM item_dataset WHERE item_id = 'F07';
SELECT printed_page, pdf_url FROM open_page WHERE item_id = 'F07' ORDER BY part;
```

第 301 页表 11 第 4 个样品的前两次结果分别是 77.01 和 77.17，原刊绝对差为 0.17。表 8 的 2.41 Ma 控制点为 98.40 mcd，表 12 同一年龄列 108.85 mcd。表 12 的底注交代了计算后修订控制深度的经过。两张表各自保存。

```sql
SELECT path, data_note, url, member
FROM chapter_files WHERE section = 'Lithostratigraphy' AND kind = 'color_final';

SELECT item_id, locator, detail FROM editorial_note WHERE item_id IN ('T08','T12');
```

## 原件、附件与核对

`metadata/source.csv` 和数据库的 `source` 表逐件给出原始分发文件的字节数和 SHA-256。`member` 和 `package` 指向本包或配套包中的可用文件。对于 CSV 转录，`sha256` 指向官方原件，各包内 `SHA256SUMS` 才是该转录文件的校验和。随盘转录保留原文件行号。两份分发文件中内容相似的行分别留在各自文件里。

可选的 `ODP138_Site846_IR_Companion.zip` 包含逐文件的随盘结构表、各自表头、图版裁片、折页、程序和说明。整份原站章及各张单芯照片可沿目录取回，前期的底本归档也保有副本。

仅用 Python 3 标准库即可重建或检查数据库。在本目录运行以下命令。

```sh
python build.py --output new.sqlite
python build.py --verify --output new.sqlite
```

核对包括原件哈希、表图编号、数据库链接、各表行数，以及 17 张盘表共 2,218 个结构行回到原行后的非空白字符比对。该比对检出漏字和错字，列界的解释仍需按原件判断。四张印页表另附可见原图，各抽查的单元格记录在 `metadata/print-checks.csv`。图注转录和涂片等材料保留已有的校读状态，原图可随时对照。数据含义采用报告的表述，范围限于 1992 年 IR 及其附随材料。

图 7 和图 45 的读数还能从原图裁片重新生成。安装 Pillow，将下例的目录指向解压出的 `plates`。

```sh
python read_figures.py ../companion/plates --export figure_readings
```

像素坐标在图 7 中相对整页扫描，在图 45 中相对未缩放的单图裁片。图 45 的两轴按原图各自标定，空缺位置保留。执行结果会逐项与已交付的读数表比对。
