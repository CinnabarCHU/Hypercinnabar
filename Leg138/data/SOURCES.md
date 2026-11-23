# 获取与核验 Leg 138 数字底本

从项目的 `Leg138` 目录执行以下命令。下载与校验只需 Python 3.9 或更高版本的标准库。程序读取随代码发布的 `data/source_inventory.csv.gz`，并通过 `--root` 指定底本存放位置。

```sh
# 在离线状态查询 Site 846 的 IR 站章相关底本
python tools/fetch_sources.py --doc IR.C11 --list
# 下载该站章 PDF
python tools/fetch_sources.py --doc IR.C11 --pdf-only --root /path/to/Leg138
# 取回公开的 IR 第 11 章电子表目录、README 与表文件
python tools/fetch_sources.py --prefix ir/primary/VOLUME/DATA/TABLES/CHAP_11/ --workers 4
# 两份 SR 章连同已登记的随章原表、勘误及外部对勘底本
python tools/fetch_sources.py --doc SR.C11 --doc SR.C39 --workers 4
# 批量获取重建四类报告共 1,922 页现代对读本所需的底本
python tools/fetch_sources.py --book --workers 8 --report book-sources.csv
# 离线确认所需的底本均在指定树下，并重算每个文件的字节数与 SHA-256
python tools/fetch_sources.py --book --verify-only --root /path/to/Leg138
# 按原分发类别取回岩芯图版，或获取完整来源集合
python tools/fetch_sources.py --collection CORE_PLATES --workers 4
python tools/fetch_sources.py --all --workers 4
```

全量清单有 5,434 个本地文件路径。5,425 个来自初版备份清单，另有 9 个为第二版 SR 校记使用的 PANGAEA 发布见证。不同发布本可对应同一组科学数据。`--book` 选取 76 个报告或附录 PDF 和 246 个数字原表，其中 IR 有 179 个，SR 有 66 个随章表及 1 个勘误表。图书生成器另需仓库提供的校记、结构化表与图件，运行说明见项目入口。

| `--collection` | 内容 | 文件数 |
|---|---|---:|
| `SP_PR_IR` | Scientific Prospectus、Preliminary Report 和 Initial Reports | 232 |
| `SR` | Scientific Results 的文件及 9 个第二版外部对勘底本 | 201 |
| `CORE_PLATES` | 图版、照片及目录见证 | 618 |
| `SHIPBOARD_CD` | 随盘船上数据、说明及工作流文件 | 4,383 |

`--collection` 也支持 `SP`、`PR`、`IR`、`PLATES` 和 `CD`。多个同类选项取并集，跨选项取交集。`--doc` 接受 `data/documents.csv` 中的 `doc_id`。它涵盖在来源清单中与该章明确关联的文件，查站点照片或船上仪器文件可另用 `--collection` 或 `--prefix`。`--pdf-only` 可与 `--doc` 合用，仅取该文献的主 PDF。路径前缀区分大小写。`--list` 将清单作为 UTF-8 CSV 写入标准输出，统计与核验诊断写往标准错误。给定 `--report` 时另存逐文件结果。

## 清单字段

`local_path` 是相对于 `--root` 的保存位置，也是稳定的取件键。`collection`、`series` 和 `role` 说明分发类别、系列与文件角色。`site` 记录来源清单已知的站号。`doc_ids` 以 `|` 分隔一个或多个明确关联的文献，`report_id` 只在该文献的主 PDF 上填写。`report_pdf` 与 `book_input` 为 `0` 或 `1`。`source_release` 记录纳入来源清单的批次。`url`、`bytes` 和 `sha256` 记录固定见证的来源、原始字节数及摘要。

`storage_encoding=identity` 表示原样存储。9 个 PANGAEA 文本以 `gzip` 存放，清单 `bytes` 与 `sha256` 全部针对**解压得到的发布文本字节**。下载器在 HTTP 解编码之后核验原始字节，再按本地表示保存。首次写入前校验，重复运行时核对已有见证。

`directory_snapshot=1` 标识 15 个捕获时会随源站目录模板变化的文件路径，其中两份 IR `TABLES/` 根目录快照记录相同来源 URL 和相同内容。目录重抓出现差异时，结果为 `directory_snapshot_changed`。其他文件内容相异的结果为 `source_digest_mismatch`。两者都会给出实得字节数和哈希，已有见证仍可用于历史核验。`--skip-directory-snapshots` 适用于只核验数据文件的场景。任何所选文件丢失、无法读取或摘要相异时，命令以非零状态结束。

维护者可执行 `python tools/build_source_manifest.py`，从仓库各模块的分发清单、第二版 SR 校记及文献索引确定性再生成压缩清单。`source_fetch_checks.json` 记录发布时的覆盖与取回验证结果。
