# 基线实测结果

每份 JSON 都记录实现版本、逐项状态、误差与单位。Acycle 的两份结果取自同一次 GitHub Actions 原生运行。两个版本与 astrochron 的适用案例合起来覆盖全部 21 个功能案例。下表中同一案例可由多个实现运行。[首次原生验证](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45166578863)

| 实现 | 功能案例 | 科学任务与其他验证 |
|---|---:|---|
| [Acycle v2.8](acycle-v28.json) | 8/8 符合容差 | MATLAB R2024b，包含两个同位素的插值、Gaussian 滤波及完整 SWA 谱 |
| [Acycle master 固定提交](acycle-current.json) | 6/6 符合容差 | MATLAB R2024b，上游双谱自检也通过 |
| [R astrochron 1.8](astrochron.json) | 12/12 符合容差 | R 4.5.0，运行 ODP 926B TimeOpt 并重放两份原始 R journal |
| [astrochron-rpy2 0.1.0](astrochron-rpy2.json) | 12/12 符合容差 | 通过原型的 11 项测试，含真实 R 调用 |
| [astrochron-warp 0.2.0](astrochron-warp.json) | 8/8 符合容差 | 使用默认子进程后端，通过原型的 17 项测试，含真实 R 调用 |
| [独立 Python 基线](python.json) | 12/12 符合容差 | 运行全部 20 个科学任务。16 项输出连续指标，4 项未满足预设判据 |

ODP 926B 的原生 TimeOpt 在 100 个候选速率中给出 3.02220 cm/kyr。文献比较值为 3.02 cm/kyr，使用的 LOESS 窗宽约定见适配器。[完整速率扫描](odp926b-timeopt.csv) · [R 实现](../adapters/astrochron.R) · [Meyers, 2015](https://doi.org/10.1002/2015PA002850)

Python 基线在 Lavernock 找到目标窗内的峰，但没有给出该峰的 5% FDR 阈值。Howards Tract 两种协议下的最优沉积速率及 La Thure 的估计值均落在预定区间外。这四项保留各自的数值和判定。[本次数值](python.json) · [早期 Harness 的独立运行](../catalog/historical-results.json)

对于 CIP Case 3，恒速基线的总时长偏差为 +2.31 kyr，整条年龄曲线的 RMSE 为 57.84 kyr，269.85–343.95 m 区间的历时偏差为 +71.96 kyr。三个指标可分别检验终点约束、逐点年代和局部旋回计数。[CIP 任务与评分规则](../catalog/tasks.json)

## 既有工作流记录

原迁移清单工具的 15 个 Python 测试已在此次整合中重跑。GUIDE/master 的 12 个 MATLAB 套件与两个探针、菜单与 Harness 集成、CENOGRID 频谱和图件还保留了原提交的成功运行记录。[GUIDE/master](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45150530706) · [菜单和 Harness](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45162612176) · [跨版本频谱](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/44943227994) · [CENOGRID 图件](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45079914392)
