# 基线实测结果

每份 JSON 都记录实现版本、逐项状态、误差与单位。各实现的适用案例合计覆盖全部 30 个功能案例。同一案例可由多个实现运行。[首版的原生验证](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45166578863) · [本次原生验证](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45188607014)

| 实现 | 功能案例 | 科学任务与其他验证 |
|---|---:|---|
| [Acycle v2.8](acycle-v28.json) | 11/11 符合容差 | MATLAB R2024b，含两个同位素的插值、Gaussian 滤波、完整 SWA 谱、Hilbert 包络和两套分段时标 |
| [Acycle master 固定提交](acycle-current.json) | 9/9 符合容差 | MATLAB R2024b，含 Hilbert 包络和两套分段时标，上游双谱自检也通过 |
| [R astrochron 1.8](astrochron.json) | 17/17 符合容差 | R 4.5.0。运行 ODP 926B TimeOpt、下马岭和 Walvis Ridge TimeOptB。分段插值调用 R 的 stats::approx |
| [astrochron-rpy2 0.1.0](astrochron-rpy2.json) | 13/13 符合容差 | 含完整 CIP 反插值。原型的 11 项测试含真实 R 调用 |
| [astrochron-warp 0.2.0](astrochron-warp.json) | 9/9 符合容差 | 含完整 CIP 反插值。默认子进程后端，原型的 17 项测试含真实 R 调用 |
| [独立 Python 基线](python.json) | 21/21 符合容差 | 运行全部 26 个科学任务。22 项输出连续指标，4 项未满足预设判据 |

两个 Acycle 环境均调用 MATLAB Signal Processing Toolbox 的 Hilbert 算子和 MATLAB 的分段线性插值。评分 JSON 记录 Acycle 提交、MATLAB 版本及上述两个算子的来源。

ODP 926B 的原生 TimeOpt 在 100 个候选速率中给出 3.02220 cm/kyr。文献比较值为 3.02 cm/kyr，使用的 LOESS 窗宽约定见适配器。[完整速率扫描](odp926b-timeopt.csv) · [R 实现](../adapters/astrochron.R) · [Meyers, 2015](https://doi.org/10.1002/2015PA002850)

Python 基线在 Lavernock 找到目标窗内的峰，但没有给出该峰的 5% FDR 阈值。Howards Tract 两种协议下的最优沉积速率及 La Thure 的估计值均落在预定区间外。这四项保留各自的数值和判定。[本次数值](python.json) · [早期 Harness 的独立运行](../catalog/historical-results.json)

对于 CIP Case 3，恒速基线的总时长偏差为 +2.31 kyr，整条年龄曲线的 RMSE 为 57.84 kyr，269.85–343.95 m 区间的历时偏差为 +71.96 kyr。三个指标可分别检验终点约束、逐点年代和局部旋回计数。[CIP 任务与评分规则](../catalog/tasks.json)

在 Newark 的 404 kyr 标定上，便携示例从两条谱峰的波长比得到 1.731 Myr，原文比较量约为 1.75 Myr。Rossello 的 La2004 峰位有序匹配在 74 个内部层位上的 RMSE 为 22.93 kyr。在下马岭，同一批 Cu/Al 观测上的简易谱功率搜索给出 93.87 角秒/年的地轴岁差频率，原生 TimeOptB 给出 87.66 角秒/年，2024 年论文参照为 87.74 角秒/年。[经典案例的参数、数据与出处](../docs/classic-studies.md)

## 既有工作流记录

原迁移清单工具的 15 个 Python 测试已在此次整合中重跑。GUIDE/master 的 12 个 MATLAB 套件与两个探针、菜单与 Harness 集成、CENOGRID 频谱和图件还保留了原提交的成功运行记录。[GUIDE/master](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45150530706) · [菜单和 Harness](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45162612176) · [跨版本频谱](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/44943227994) · [CENOGRID 图件](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45079914392)
