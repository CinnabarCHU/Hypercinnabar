# 审查交接与完成边界

日期：2026-11-17。公开工作分支：`CinnabarCHU/Hypercinnabar:acycle-branch-audit`。

此前会话在发布前中断；本次恢复了原工作区中的已暂存成果，没有重新发明入口集合或覆盖其人工判断。

2026-11-18 续接：已完成 [GUIDE 迁移后的耦合评估与公共 API 建议](COUPLING_AND_API.zh-CN.md)，用四个固定历史快照区分界面迁移与后续核心抽取。该报告补充本轮后续设计方向：优先保持独立计算文件不变，提取 GUI 内的准备、编排和绘图边界；尚未实现新公共 API。

2026-11-18 后续追踪：已完成 [analysis cores 的修改规模与实际调用路径](CORES_TRACE.zh-CN.md)。精确区分 `885c742` 的 15 个新增 core、10 个被改旧文件，以及整个 3.X 期间的其他修改；当前 18 个 `acycle*` 文件的直接旧依赖只有四个，GUI 路径是混合状态。`audit/cores/` 保存可重生成清单。新增三个依赖遗漏回归检查，总计 15 项 Python 检查通过；原 15 份自动报告与上游源码保留不变。本轮仍没有执行 MATLAB 或更改科学算法。

## 本轮已交付

- 上游两分支比较、固定 master 提交、412 个文件的逐文件迁移清单。
- 337 个 MATLAB 文件、2,499 个函数／方法声明的静态调用与回调证据。
- 未进入选定入口闭包的 76 个文件、活跃文件内的 58 个函数块，以及可恢复历史测试的索引。
- 19 个首批计算入口和 29 个依赖文件的规划表。
- 可重新运行的审计器、12 项作用域等行为检查，以及 `verify_audit.py` 的报告、源码、图端点和重生成核验。

核验记录分别见 `reports/validation.json`（原审查基线）和 `reports/resumption_validation.json`（恢复后的实际复核）。原始 15 份自动生成报告保留原字节；人工报告和交接材料不计入此数量。

## 下一阶段的起点

本轮完成的是用户要求优先进行的分支 review、调用关系梳理与迁移清单。下面是后续工程范围，不代表已通过运行验证：

1. Harness 已保存的基线仍为 `_Codex:acycle-harness-master-interfaces`，提交 `ecbf81a367425dd83d5400986dad87cc099057c8`。迁移其运行代码时在 `Hypercinnabar` 另开分支，并记录来源；本审查分支不混入其他私有仓库项目的历史。
2. 根据 `FIRST_WAVE.zh-CN.md` 逐项锁定接口契约，恢复相应历史测试，运行 MATLAB 回归；保留 `pdan` 与新 PDA 的不同数值约定。
3. 再处理 spectral、COCO/eCOCO、DYNOT 的 GUI 状态、绘图、进度与输出边界。
4. 76 个文件是静态未达集合。59 个文件仍明确标为 `unreached_candidate / review_no_delete`；清单不能自动触发删除。空占位、旧 GUI、兼容入口和独立计算核心已分别记录。

本次没有改动上游算法、删除 MATLAB 源码、执行 MATLAB／MEX／GUI，也没有声称完整 Harness 迁移或数值等价性验证已经完成。后续运行与 CI 应使用公开仓库分支，遵循用户已确定的仓库安排。

## 续接命令

```bash
git clone --recurse-submodules --branch acycle-branch-audit https://github.com/CinnabarCHU/Hypercinnabar.git
cd Hypercinnabar
git -C upstream/acycle fetch origin '+refs/heads/*:refs/remotes/origin/*'
python -m pip install -r audit/requirements.txt
python -m unittest discover -s audit/tests -v
python audit/tools/verify_audit.py --regenerate
```

重生成需要完整上游历史和审查时的分支 refs。若上游分支移动，`summary.json` 差异应先作为新的审查输入处理，不能悄悄重写既有结论。重生成会写入临时目录，核验失败不会覆盖已审查报告。
