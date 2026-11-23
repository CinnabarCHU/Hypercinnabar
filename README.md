# Cyclostratigraphy Benchmark · 旋回地层学软件测试集

本分支提供两种可独立使用的测试。**Test cases** 检查一项实现是否在给定参数和版本下复现了数值结果。**Test tasks** 给出同一组地层观测，允许采用不同方法，再比较科学量、误差和不确定度。新实现可以只提交 CSV 和 JSON，评分器不需要导入候选软件。

| 测试线 | 当前覆盖 | 评分依据 |
|---|---|---|
| 30 个功能案例 | Acycle 与 astrochron 的插值、调谐、滤波、谱估计、随机重放和煤山时标。含 9 项合成模型测试，覆盖 CIP 沉积、间断两侧的年龄、弱信号与变速率代理、调幅包络和 Imbrie 冰量响应 | 逐列逐行比对解析解、生成器归档、原始 R 返回表或指定版本的 MATLAB 数值场 |
| 26 个科学任务 | 深海冰期频谱、地中海岁差调谐、Newark 湖相长周期、下马岭与 Walvis Ridge 古自转，以及既有的 PETM、CENOGRID、CIP、煤山、LR04 等问题 | 比较已发表的估计、检验预定条件、预测留出观测，或评估对生成真值的恢复 |
| 既有原生测试 | GUIDE/master 迁移测试、Acycle Harness 全部 12 个案例、上游双谱和 COCO 验证、CENOGRID 逐图与跨版本诊断、两个 Python 接口原型 | 保留原测试自身的断言、版本、输入要求和历史失败记录 |

[功能清单](catalog/cases.json) · [任务与评分指标](catalog/tasks.json) · [经典论文、研究记录与合成真值](docs/classic-studies.md) · [既有测试和资料来源](docs/sources.md) · [已运行的基线结果](baselines)

## 从一个案例开始

在此分支根目录运行。Python 3.10+ 可以准备数据、评分和运行示例基线。R 或 MATLAB 用于相应的原生实现。

```bash
python -m pip install -r requirements.txt
python bench.py list
python bench.py verify
python bench.py prepare tune-knots .results/tune/input
python adapters/python_baseline.py .results/tune/input .results/tune/python
python bench.py score tune-knots .results/tune/python
```

上面的四个观测在三个控制点间调谐。预期时间列为 100、110、130、150 ka，代理指标仍按原样对应。对同一份输入，可用 R 运行 `Rscript --vanilla adapters/astrochron.R .results/tune/input .results/tune/r`，再评分。已经安装的 Acycle 可在 MATLAB 中调用 `acycle_candidate(requestDir, outputDir, acycleRoot)`。MATLAB 入口放在 `adapters/`。

## 用新方法做一个地质问题

```bash
python bench.py prepare cip1-case3 .results/cip/input
python adapters/python_baseline.py .results/cip/input .results/cip/constant-rate
python bench.py score cip1-case3 .results/cip/constant-rate
```

CIP Case 3 给出 2,631 个高度和代理指标观测。方法提交各观测高度上的相对时间。评分分别报告整条曲线的 RMSE、总时长偏差，以及容易数错一个旋回的区间时长偏差。随附的恒速示例总时长只差约 2.31 kyr，但逐点 RMSE 达 57.84 kyr。这两个数字回答不同的问题。[CIP 论文](https://doi.org/10.1016/j.earscirev.2019.102965) · [本次基线](baselines/python.json)

若要验收软件的时深转换，可运行 `cip-case3-forward-clock` 和 `cip-case3-inverse-clock`。前者给定沉积速率函数，检查模拟器的每一步累积高度。后者给定完整时深节点，检查调谐算子在上述 2,631 个观测高度上的返回值。三项使用同一套地层坐标。[合成模型与对应任务](docs/classic-studies.md#有真值的功能案例)

| 科学任务 ID | 交付和评价 |
|---|---|
| `lavernock` | 指定波长窗内的谱峰、峰功率和同一谱峰的 5% FDR 阈值。峰位与阈值分别评分 |
| `petm-published`, `petm-broad` | 两套明确的取样范围和协议。记录全范围最优速率、与 8–15 cm/kyr 的距离、能否给出全搜索校正的 p 值 |
| `odp926b-timeopt`, `la-thure-coco` | 给出平均沉积速率，与对应记录和区间的已发表结果比较 |
| `anticosti-precession`, `anticosti-eccentricity` | 在 LL1 自然伽马记录上分别估计两种模板的平均速率和总时长 |
| `bridge-meyers`, `bridge-updated` | 同一灰度记录、两套灰层年龄约束，分别报告 C/T 界线年龄及可选 95% 区间 |
| `cenogrid-modulation` | 两种同位素在四个事先确定的频带内分别找主周期，与冻结的 v2.8 计算场比较 |
| `lr04-gaps` | 重建被抽去的同位素观测，按零散缺点和连续缺段分别报告偏差与 RMSE |
| `cip1-case3`, `meishan-tuning` | CIP 与公开生成真值比较；煤山固定两端，在 Li 的深度坐标上与已发表的 288 点调谐时标比较 |
| `odp846-oracle-original`, `odp846-oracle-reduced` | 使用完整旋回的准确控制点，对两种速率扰动强度分别重建段内年龄。两个间断的两侧分别处理 |
| `laurin-stable`, `laurin-variable-rate`, `laurin-weak-band` | 在固定 20 kyr 周期、相同类型的峰位先验下，从带噪代理序列恢复三个局部历时 |
| `synthetic-rate-step`, `synthetic-detection` | 恢复已知的分段速率；在 20 条含信号和 20 条 AR(1) 对照记录上分别计算检出率和误报率 |
| `hays76-simplex` | 从两支深海岩芯分别估计三个冰期频带主峰，核对 1976 年论文的逐岩芯周期和倾角/岁差周期比 |
| `rossello-precession`, `odp846-published-clock` | 给定两端年龄，重建地中海沉积旋回层位或东太平洋底栖同位素年代，报告独立内部层位的 RMSE |
| `newark-long-eccentricity` | 在 Newark 湖相深度等级记录上估计长周期与 404 kyr 载波的波长比，换算为长周期历时 |
| `xiamaling-precession`, `walvis1262-precession` | 从 Cu/Al 或反射色度 a* 联合估计沉积速率和地轴岁差频率，可提交恒星日长和 95% 区间。分别比较 2018 和 2024 年估计 |

## 结果协议

1. `prepare` 将观测、单位、算法参数或科学问题写入一个新的请求目录。运行候选方法时可单独交付这个目录。公开参考数据可用于回归和教学，所有成绩按开放基准解释。
2. 为每个实现建立独立的提交目录。至少写入 `method.json`，例如 `{"method":"my-method","version":"1.2.0"}`。可补充提交 SHA、随机种子、参数及预处理。功能案例写入带表头的 `result.csv`。标量任务写入 `result.json`，字段和单位见 `request.json`。曲线、留出预测和检测面板写入 `prediction.csv`。
3. 六个整条年代曲线任务还接受 `ensemble.csv`。前两列为 `segment,coordinate_m`，后续为 `draw_1,draw_2,...`，至少两条完整单调的样本曲线。评分器报告经验 CRPS、90% 区间平均宽度和参考年龄落入区间的点位比例。在煤山、Rossello 和实测 Site 846 上，该比例表示对已发表时标的覆盖。
4. `score` 输出 JSON。退出码 0 表示数值相符、满足规定条件或连续指标已计算。1 表示数值失配或未达到规定的科学条件。2 表示输入无效，例如漏行、列名/单位错误或非有限数值。文献比较保留数值偏差；结论限定在该条记录及其处理条件下。

## 复跑与扩展

```bash
python -m unittest discover -s tests -v
python tools/run_profile.py python .results/portable
python tools/run_profile.py r .results/astrochron
python tools/suites.py list
python tools/suites.py run harness-cases --case paper-petm-coco-published-protocol
```

已安装我们之前的 Python 接口原型时，可用 `python tools/run_profile.py rpy2 .results/rpy2` 或 `python tools/run_profile.py warp .results/warp` 将其输出与同一份参照逐项比较。两条命令分别调用薄封装和默认使用独立进程的领域接口。[各实现逐项结果](baselines/README.md)

原生 Harness 命令需要 MATLAB 和已安装的上游运行依赖。对新方法，同一个科学任务可以直接复用现有输入和评分器，只需增加候选输出。加入功能案例时，应给出独立参照、坐标单位、完整参数和容差；加入科学任务时，应写明待估量、论文或真值来源、比较指标，以及哪些偏差属于协议差异。[运行条件、数据署名与覆盖边界](docs/sources.md)
