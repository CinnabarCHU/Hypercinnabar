# Acycle branch and migration audit

本分支是 Acycle / Acycle Harness 后续迁移工作的公开审计基线，核对日期 **2026-11-17**。Acycle 上游源码以固定提交的 Git submodule 保留；本次没有修改计算算法、删除源码或执行 MATLAB / GitHub Actions。

- [审查报告：分支、悬置代码、调用关系与迁移顺序](audit/REVIEW.zh-CN.md)
- [第一批 19 个计算入口及其完整依赖](audit/FIRST_WAVE.zh-CN.md)
- [全部 412 个文件的迁移清单](audit/reports/migration_inventory.csv)
- [函数与局部／嵌套函数、类方法](audit/reports/symbols.csv) · [调用及回调证据](audit/reports/edges.csv)
- [文件调用关系](audit/reports/file_edges.csv) · [主菜单绑定](audit/reports/menus.csv) · [待复核代码块](audit/reports/block_candidates.csv)
- [人工判断与入口集合](audit/decisions.json) · [上游源码](upstream/acycle)
- [审查交接、完成边界与后续起点](audit/HANDOFF.zh-CN.md)
- [GUIDE 迁移后的耦合评估与公共 API 建议（2026-11-18）](audit/COUPLING_AND_API.zh-CN.md)
- [Analysis cores：修改规模、旧函数直接依赖与 GUI 实际路径（2026-11-18）](audit/CORES_TRACE.zh-CN.md)

本次公开分支交付的是审计工具、清单和上游源码指针；Harness 的运行代码迁移和完整 MATLAB 回归不属于这次审计的完成声明。

## 重建与维护

```bash
git clone --recurse-submodules --branch acycle-branch-audit https://github.com/CinnabarCHU/Hypercinnabar.git
cd Hypercinnabar
git -C upstream/acycle fetch origin '+refs/heads/*:refs/remotes/origin/*'
python -m pip install -r audit/requirements.txt
python -m unittest discover -s audit/tests -v
python audit/tools/verify_audit.py --regenerate
python audit/tools/track_analysis_cores.py
python audit/tools/query_graph.py code/seriesanalysis/acycleBandpassFilter.m --direction callers
```

`audit_acycle.py` 只读取已跟踪源码和历史，不执行 MATLAB。Python 环境及版本记录在 `summary.json`。分支对比需要完整历史；浅克隆须先 `git -C upstream/acycle fetch --unshallow`。

`verify_audit.py --regenerate` 在临时目录重生成，并核对保存报告、源文件哈希和调用图端点；不会覆盖已审查结果。确认上游变化后，才用 `python audit/tools/audit_acycle.py` 更新报告并同步验证记录。

上游更新时，先取回全部分支并检查差异，再更新 submodule 和 `decisions.json` 的 `source_commit`，复核人工结论和行号，重新生成清单并提交差异。源提交不匹配、解析失败或人工条目指向不存在的文件／函数时，生成器拒绝交付不完整清单。`query_graph.py --transitive` 可查文件间依赖，但它汇总文件内所有函数，不能替代以入口为起点的可达性集合。

各 CSV 保存的是静态“可能调用”关系。未进入入口集合不等于可以删除；具体证据类型和分析边界见报告。上游及其第三方组件保留各自许可与署名；本仓库原有 LICENSE 保持不变。

`audit/cores/` 是固定历史快照的后续追踪，保留原审计报告；其 `graph_supplement.csv` 补充旧采集器遗漏的二元表达式左侧调用。当前 cores 的依赖与调用点以该目录和对应报告为准。
