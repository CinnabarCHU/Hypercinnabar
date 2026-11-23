# 真实 DeepSeek Harness / Acycle 验证 — 2026-11-23

状态：通过。官方 DeepSeek Harness SDK / AgentLoop 0.2.1-rc.3 使用真实 `deepseek-flash`，在同一个会话的三轮对话中执行 18 次工具调用；其中 7 次通过 MATLAB R2024b 完成。20 个 Acycle 工具和 10 项技能出现在模型可见目录中。这些注册数不表示每个工具或科学方法均已验证。

## 结果

- 当前版 `RGBToGray` 的 helper、analyzer、plotter 均完成。
- 第二轮从原 analyzer 日志重放，生成新 run_id，父记录正确，结果的类型、尺寸和每个数值一致。
- 第三轮通过 `RGBToGray_legacy` 选择 GUIDE 版本，三个接口均完成，输出与当前版一致。
- 预期且实际输出均为 `uint8([76 150 29; 0 255 128])`。输入是本目录的 81 字节、3 列 × 2 行标准 RGB 色块。
- 每次调用都有闭合的 init/fin 记录、参数快照和 RNG 快照；非空返回值有 MAT 快照。plotter 返回空值并导出 PNG。原始小图产生的 PNG 为 10×9 像素，未修改原方法来放大它。

| 版本选择 | 调用 | MATLAB 执行记录 | 状态 |
|---|---|---|---|
| RGBToGray | helper | [20261123T115727Z-7f4853b8b4c1](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45169867343) | done |
| RGBToGray | analyzer | [20261123T120137Z-d22f016503d9](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45170482865) | done |
| RGBToGray | plotter | [20261123T120354Z-7269282e94e2](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45170820634) | done |
| RGBToGray | replay | [20261123T120620Z-97b928c26dc6](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45171189902) | done |
| RGBToGray_legacy | helper | [20261123T120900Z-6fda234c2a6c](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45171609814) | done |
| RGBToGray_legacy | analyzer | [20261123T121101Z-a22d5eb98355](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45171922992) | done |
| RGBToGray_legacy | plotter | [20261123T121257Z-60b2e2bb99c2](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45172230648) | done |

源代码固定在 [6cc8b78](https://github.com/CinnabarCHU/Hypercinnabar/commit/6cc8b78e3cabb99a9fd802c06eb915235953455c)。每个 worker 提交仅增加/替换验证请求，计算代码保持不变。

## 本次发现与修复

1. 原生插件原本会将模型密钥环境变量继承给 Python/MATLAB。现在在子进程启动前移除，配置覆盖也不能重新注入；正常和失败返回均有脱敏处理。新增回归测试通过。
2. 菜单搜索是英文子串匹配，旧说明未明确；已澄清。图像不能送到文本检查器，intake 和工具说明已修正。
3. 菜单 wrapper 名称无需在原生函数目录中再次查询，相关说明已澄清。
4. 验证器现在将四种菜单执行调用及 native 调用纳入执行预算，并提供 `--acycle-only` 关闭本次测试不需要的 shell 工具。

前两次发现阶段被预算检查器停止，并非成功的科学验证。详见 [earlier-attempts.json](earlier-attempts.json)。修改说明后重新开始一个会话；最终三轮均通过。没有改动 Acycle 数值函数。

## 证据与可交换文件

- [summary.json](summary.json)：软件版本、数值断言、run_id、父子关系和执行链接。
- [tool-trace.json](tool-trace.json)：实际模型工具调用及每轮结果统计；路径已规范化。
- `responses/`：实际模型最终回答，仅改写了本地文件链接。模型回答中的额外解释与这里的独立验收结论分开保留。
- `runs/<run_id>/acycle-journal.zip`：原样保存的可交换日志和 MAT 快照。
- [exchange-records.zip](exchange-records.zip)：全部 7 次调用的记录、结果摘要和两张 PNG。
- [CI](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45169742055)：260 项 Python 测试、15 项插件测试、两个官方运行时各 11 项附件测试均通过。另有 13 次真实 MATLAB 调用，覆盖当前/旧版灰度、helper/analyzer/plotter 重放、插值及缺少必填参数时的失败记录。

在匹配的迁移代码 checkout 执行 `setup_migration`，将任一 journal ZIP 解压到独立目录，然后在 MATLAB 中调用：

```matlab
[value, newJournal] = aclog.replay('/path/to/extracted/events.jsonl');
```

如需重跑真实模型测试，安装 Harness 后使用 `scripts/harness_conversation.mjs`，指定本目录的 `scenarios.json`、`--case menu-live`、`--mode live`、`--acycle-only`、独立 workspace 和输出文件。后续轮通过 `--continue` 指向上一轮 receipt。凭证只通过运行时注入，不写入场景、配置或仓库。

## 范围

本次是 SDK/AgentLoop 的真实功能烟测，模型在云端，MATLAB 在独立 GitHub Actions worker。测试专用传输仅搬运请求与文件，保留校验值；没有替模型选方法、填参数或生成数值结果。它不代表已交付通用云端 MATLAB 服务，也没有完成浏览器/桌面 GUI 的显示验收。

小型确定性图像验证不能推出所有科学算法、随机算法或其他图像类型正确。广泛科学验收仍由独立 benchmark 覆盖。密钥扫描与进程关闭结果见 `security-check.json`。
