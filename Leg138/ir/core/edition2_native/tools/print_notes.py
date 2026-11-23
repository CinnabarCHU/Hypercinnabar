"""Editorial readings compared to chapter page images. Keep the electronic and printed witnesses separate."""
from selection import HERE
import csv
ROWS=[
 ('IR06.T02','24',3,89,'last_age','电子表最后一行的 Mean Age 留空，保留其五个站位速率。','印本最后一行的 Mean age 同样留空。'),
 ('IR10.T10','2–27',41,229,'rate_age_header','电子表中间列题作 Age，右列题作 Rate，例 12.32 行分别为 30.0 与 0.41。','印本把中间列题作 Sediment rate (m/m.y.)，右列题作 Age (Ma)；深度 12.32 m 对应速率 30.0、年龄 0.41。电子版两个字段特加 as_header。'),
 ('IR13.T16','40',52,728,'missing_column_padding','深度 103.35、年龄 10.54 行的 4.58 印在原 ASCII 的 Corg 字符位置，其后 0.70、0.32、0.21、0.11 都左移。','印本 CaCO₃=65.59，Corg 空，沉积速率=4.58，DBD=0.70，bulk MAR=0.32，CaCO₃ MAR=0.21，non-CaCO₃ MAR=0.11，Corg MAR 空。'),
 ('IR13.T15','18',50,726,'partial_sample_label','电子行首为 138-848，仅能定出站号，不能据此确定孔位。','印本该行 core label 留空、仍给出 43.00、47.55、4.56、0.96。'),
 ('IR14.T04','2',28,762,'header_hole_differs_from_station','电子文件的表题写 Site 849，分组标题写 Hole 844B。','印本的表题与孔组标题也作 Site 849、Hole 844B。保留原孔名，站章归属单独列。'),
 ('IR15.T04','3–9',21,829,'hole_in_print_only','电子版缺失孔位标题，其范围值存入 hole_unspecified 开头的列。','印刷表题及孔位标题可核，孔名明确为 Hole 850B。'),
 ('IR15.T14','7–46',41,849,'no_hole_in_source_table','电子表只给 core section 与 interval，无分组孔名。40 行照录。','印刷表头与样品栏同样只有 core/section/interval。跨表对齐须另记依据。'),
 ('IR18.T12','59',30,1052,'Corg_MAR_column','该行出版值依次含 81.0、8.95、0.80、0.71、0.58，末值 0.14 靠近最右列。','印本末值 0.14 确在 Corg MAR 栏，non-CaCO₃ MAR 留空；旧版 figures/core/data/ir_mean_intervals.csv 两列次序曾置反。'),
 ('IR12.T03','6','','','damaged_native_event','事件残文为 iliania lacunosa，原行尾部有一段与前部重复/错位的值。','所选网上站章 PDF 的相关位置是正文提及随盘表。保留行尾 unresolved_source_fragment，完整材料可据原文行查阅。'),
]
with (HERE/'print_witness_notes.csv').open('w',encoding='utf8',newline='') as f:
 w=csv.writer(f);w.writerow(['item_id','native_source_lines','chapter_pdf_page','printed_page','issue_kind','electronic_reading','comparison_note']);w.writerows(ROWS)
