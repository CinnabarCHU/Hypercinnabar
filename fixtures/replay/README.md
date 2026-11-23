# 从 Python 记录 astrochron 调用，在 R 中重放

这个例子给出了两份可独立重放的运行记录。记录端通过 rpy2 调用原版 astrochron 1.8，重放端只使用 R。两次计算使用 R 4.5.0，在同一 Linux 环境下完成。

| 目录 | 记录的操作 | 核对结果 |
| --- | --- | --- |
| `examples/tune/` | 将 81 点序列按 4 个控制点调谐，在下方面板标出 85 ka | 81 × 2 数值表、列名与行名完全相同。800 × 600 的 PNG 逐像素一致。去掉参考线事件后，下方面板有 151 个像素发生变化。 |
| `examples/ar1/` | 在已有随机流中生成 32 点 AR(1) 序列 | 32 × 2 数值表、列名与行名完全相同。作为对照，只重设最初的整数种子会使 32 个噪声值全部改变。 |

## 重放附带的记录

安装 R 包 `astrochron`、`jsonlite` 和 `hdf5r` 后，从解压目录运行下面的命令。指定的输出目录应尚未创建。验证附带的记录时，R 和 astrochron 版本须与清单相同。也可以按下一节用本机版本重新记录。

```sh
Rscript --vanilla replay.R examples/tune replay-tune
Rscript --vanilla replay.R examples/ar1 replay-ar1
```

每次都会在新目录写入 R 重新计算的 `result.csv`。第一条命令还会生成 `replay-tune/tune.png`。PNG 的像素可受平台、字体和图形设备版本影响。

## 从 Python 重新记录

安装 Python 包 `rpy2`、`pandas`、`numpy` 和 `hdf5storage` 后运行以下命令。记录示例使用了 rpy2 3.6.6、pandas 2.2.3、NumPy 2.3.5 和 hdf5storage 0.2.2。

```sh
python record.py my-records
Rscript --vanilla replay.R my-records/tune my-tune
Rscript --vanilla replay.R my-records/ar1 my-ar1
```

## 可交换文件里有什么

- `events.jsonl` 沿用 Acycle 的 `init`、`fin` 和 `event` 记录。例子将 `graphics::abline` 的目标面板与参数写成可执行的结构化事件。
- `events.jsonl.params.mat` 保存实际传入 R 的数值表和显式参数。`events.jsonl.retval.mat` 保存作为核对基准的返回值。`ar1` 还含有调用前的 R 随机状态快照。MAT 文件均使用 v7.3 格式，顶层变量名为 `value`。
- `manifest.json` 是本次试验的补充约定，注明执行环境、R 包版本、公开函数名、列名、行名和设备参数。正式协议的字段仍待确定。

重放器根据输入重新调用 R 的公开函数，计算结束后才打开原返回值作比较。本例覆盖数值数据框、整数、浮点数、逻辑值、串行随机状态和一次原生图形叠加。它是用于检验协议边界的独立示例，现有 Acycle 的 MATLAB 分派器以及重放时创建新 journal 的功能仍需在正式集成时接入。
