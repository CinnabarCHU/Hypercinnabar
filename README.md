# CENOGRID 正文与补充图件

[综合版的 16 幅图](figures/manuscript)按稿件顺序列于下表。原稿两幅图均编号为 2，`F2h` 表示轨道变量 *h*，`F2iso` 表示底栖同位素。每个图号下的 `plot.svg` 可直接打开，`main.py` 可重新生成 MATLAB FIG 和 SVG。

| 正文图 | 内容 | 附图 | 内容 |
|---|---|---|---|
| [1](figures/manuscript/F1/plot.svg) | 六组偏心率与长周期滤波 | [S1](figures/manuscript/S1/plot.svg) | 采样、LOWESS 与 PETM 处理 |
| [2h](figures/manuscript/F2h/plot.svg) | 两套轨道解的 *h* 小波谱 | [S2](figures/manuscript/S2/plot.svg) | MTM 谱与联合显著性判据 |
| [2iso](figures/manuscript/F2iso/plot.svg) | 底栖同位素、滤波与短偏心率频带功率 | [S3](figures/manuscript/S3/plot.svg) | 高斯滤波、PDA 与调制峰间距 |
| [3](figures/manuscript/F3/plot.svg) | MTM、SWA 与 FDR | [S4](figures/manuscript/S4/plot.svg) | Taner 滤波与演化 FFT |
| [4](figures/manuscript/F4/plot.svg) | 四条序列的 80–140 kyr 频带功率 | [S5](figures/manuscript/S5/plot.svg) | 两条同位素的连续小波功率谱 |
| [5](figures/manuscript/F5/plot.svg) | 两种同位素与两套天文解的演化谱 | [S6](figures/manuscript/S6/plot.svg) | 轨道解长周期滤波与小波谱 |
| [6](figures/manuscript/F6/plot.svg) | 同位素小波功率与全局谱 | [S7](figures/manuscript/S7/plot.svg) | 五组小波相干与相位 |
| [7](figures/manuscript/F7/plot.svg) | 轨道与同位素的小波相干和相位 | | |
| [8](figures/manuscript/F8/plot.svg) | 偏心率调制与已发表的碳同位素记录 | | |

## 复现基准与相位约定

谱分析采用 Acycle 的 `v2.8` 正式标签 `e3553eb`。在这两条记录上，2026 年 1 月 30 日的 `1f8fd71` 给出相同的 SWA 背景和 5% FDR 阈值，精度达到原始导出的有效位数。结果支持这套历史实现，作者实际安装的提交仍待确认。[Acycle v2.8](https://github.com/mingsongli/acycle/releases/tag/v2.8)

图 2iso 和 S3 在 PETM 处理后再扣去整段均值，然后运行历史高斯滤波。图 2iso、4 和 S3 的 PDA 均积分 80–140 kyr。图 5 和 S4 对同位素使用 0.30–1.80 cycles/Myr 的 Taner 通带，对偏心率使用截止于 1.80 cycles/Myr 的低通。图 6、S1、S5 使用分支中与 v2.8 等效的已计算图件。图 1、2h、S6 源自轨道程序，图 8c、d 沿用已发表图形的曲线。

**图 7 和 S7 使用取反后的两个同位素序列。** 在四组轨道–同位素配对中，图中相位与原符号序列相差 180°。碳–氧配对的两端同时取反，相位保持一致。所有配对的平方相干度均保持一致。解释原始同位素相对于轨道的领先或滞后时，应先还原这 180°。

## 重新出图

在仓库根目录运行以下命令。`--cached` 使用已分发的 MATLAB 数值场。安装 Python 依赖并令 MATLAB 位于 PATH 后，指定 `--output` 即可把 FIG 与 SVG 写入自己的目录。

```sh
python -m pip install -r requirements.txt
python main.py F3 --version manuscript --cached --output output/F3
python figures/manuscript/F7/main.py --cached --output output/F7
```

去掉 `--cached` 可从输入重算，所用上游提交见 [Acycle 版本表](versions/acycle.json)。[综合版逐图配置](versions/manuscript.json)记录 16 幅图的计算来源。[其他版本和参数对照](figures)可用于复核。
