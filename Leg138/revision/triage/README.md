# 出版方 OCR 与扫描影像的第二次识读

此处记录机器之间的分歧，为逐页校读分配工作。报告有 76 个分册、1,922 个源页、347,324 个带位置的文本片段。本轮采用页栏读取器识别的正文、标题和图注，挑出水平、具有足够字母和长度、框高 6–24 pt 的行。全量读取覆盖此规则接受的 75,633 行，分布在 1,882 页。其中 42,363 行两种文字逐字匹配，30,297 行出现分歧，2,973 行第二次识读为空。未进入抽取范围的包括密集表格、旋转图字、短标号以及底本有、出版方文字层完全遗漏的文字。

脚本将源页文字框回投至灰度影像，按 240 dpi 裁取字行，使用 Tesseract 的英文模型独立识读。每行存原 PDF 哈希、裁片哈希、文本层地址、框坐标、两种读法和相似度。引擎输出可能把相邻印字带入目标框，也可能漏读或分错行。程序不据此修改正文。第二识读使用的裁片批次不同，抽样和全量两次运行的 OCR 字符串可能有所差异。

初次抽样使用每页至多三行，取得 5,128 行。10 个文字完全相同的样本经盲读均吻合。在 10 个分歧样本中，仅出版方正确 5 个，仅第二 OCR 正确 2 个，两者均有误 3 个。另有 10 个第二 OCR 空读样本，其中 2 个出版方也有误。各组按指定文献和分歧类型抽样，不能外推全卷错误率。[30 个盲校样本及选择方法](INDEPENDENT_SAMPLE.md)

在 Leg138 目录重建抽样及完整分册队列。对应的机器结果可在完整离线包的 `revision_evidence/triage` 下查验。

```bash
python revision/triage/compare_lines.py --sources .
python revision/triage/compare_lines.py --sources . --all-eligible --out build/ocr-lines
python revision/triage/distribute.py build/ocr-lines
```

[逐页接受行数](corpus_pages.csv) · [按文献统计与哈希](corpus_index.csv) · [全量识读统计](corpus_summary.json)
