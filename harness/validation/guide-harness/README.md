# 用真正的 Acycle Harness 验收 User Guide

测试对象是 `acycle-harness-menu` 上的 Acycle Harness 0.6.0。指南和 3 个输入文件由[固定清单](../../../tests/user_guide/manifest.json)锁定。所有科学结果均为本次新算的 MATLAB R2024b 产物。以下三层证据各自回答不同的问题。

| 层级 | 实际入口 | 结论 |
|---|---|---|
| 用户用自然语言要求做谱分析 | 官方 DeepSeek Harness SDK、真实 `deepseek-flash`、附件、已注册插件、Python、真实 MATLAB | 三组原始附件都得到可复核的谱；包含错误调用、自行修正、额外重算和科学偏差。 |
| 用户要求完成后续菜单操作 | 同一官方 SDK，新会话，附件是上一步实算的 CSV | 单独记录 ETP 小波、瓦窑建模与调谐尝试；菜单查到、Helper 返回，均不自动记为科学完成。 |
| 固定步骤精确复现整章 | 发布包、官方 Cordis 工具注册表和 native executor、插件、Python、独立 MATLAB 进程 | 20 + 23 + 47 = 90 次注册工具调用和日志均成功；85 项不同的检查中 82 项通过。包含 MTM 重放、ETP 小波、传统 COCO/eCOCO、405 kyr 建模和原 GR 调谐。 |

**固定步骤**：[Actions 作业与完整产物](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45193653824)，[每次的工具名、运行编号、来源、图数和日志哈希](evidence/installed-guide.json)。日照量 17/18，ETP 26/28，瓦窑 39/39。3 个失败是截图 NFFT=N 设置下的日照量 22.4 kyr 和 ETP 41、22.4 kyr，报告保留了它们，所以前两个作业按设计为红色。原桥接报告把瓦窑 6 个双图检查各序列化了两条；按检查名称和布尔值去重后，两轮全部一致。固定客户端把一个菜单的完整输出传给下一个菜单；这不能证明自然语言 Agent 能自己选对菜单、传好数据。

**对话验收**：[五次高层数值计算及独立评分](evidence/live-spectra.json)，[后续菜单调用](evidence/live-followups.json)。每个公开 run 含原始输入 SHA-256、工作流或上游引用。[模型最终答复](evidence/model-answers.md)单列，仅供抽查；完整会话和隐藏模型内容不在仓库中。科学比较读取返回的数值文件，无须相信模型自述。

| 案例 | 清理、插值、去趋势 | 功率和图件 |
|---|---|---|
| 日照量 | 与 GUIDE 残差逐点相同 | 同 NFFT=10005，功率最大差 / 参考谱最大功率为 3.7×10⁻¹⁵。独立在完整谱读出 23.709、22.383、18.985 kyr。|
| ETP | 与 GUIDE 残差逐点相同 | 同 NFFT=10005，上述误差为 2.7×10⁻¹⁵。400.20、125.06、95.29、41.00 kyr 等峰复现。|
| 瓦窑 GR | 534 行，首轮与参考的深度/残差最大绝对差约 1.2×10⁻¹² | 五个目标峰均在同一频点；整谱最大差 / 参考谱最大功率为 2.31%。高斯带通曲线相关 0.9946，最大绝对差约 23.07 GR 单位。|

日照量、ETP 主会话的严格状态均为 `execution_failed`：前者曾提交无有效入口的 native 请求，后者第一次提交了不存在的 `method` 参数；随后确实算出正确的 MTM 数组。瓦窑主会话严格通过；首次省略 20% 中值平滑、采用 25% 默认值，模型随后主动改用 20%。95% 背景线上按参考曲线最大值归一化的最大差由 12.19% 降至 0.70%，峰位和整体功率差没有因此消失。三组均使用显式 5 倍零填充，不能借此将 NFFT=N 的手册检查改判通过。

两组 1 kyr 序列里，高层工具把 3.2 kyr 请求舍入为 3 个样点，并回报 3 kyr。高层摘要只返回功率排序前 10 个峰，表中对指南周期的核对使用完整谱的局部峰，不表示模型在摘要里自动找到了每一峰。GUIDE [PowerSpectrum Helper](../../../matlab/+acmethods/+PowerSpectrum/helper.m) 会在 LOWESS 后再次减均值；[高层实现](../../overlay/matlab/acycle_batch.m)直接送 LOWESS 残差进入谱计算。瓦窑这组残差均值为 −7.005 GR 单位。这是一个可定位的输入差异；并未把滤波的全部差异归因于它。

**后续会话没有通过。** 两个新的真实模型会话都从前一轮实际产物的 SHA 开始，未给模型预期数值。ETP 最终确实调用了旧版小波 Analyzer，但 `dss=1`、`method_sel="FFT"` 被带入计算，返回 **10 × 2001** 的功率矩阵；固定旧版配置 `dss=0.1, method_sel=3` 得到 **91 × 2001**。在完成要求的图件前耗尽了 10 次科学调用额度。瓦窑先误选了应用年龄模型的菜单，又把 `filtered.csv` 的文件名作为数值 `data`，并给选峰参数传入字符串。建模 Helper 虽返回 done，日志实为 **1 × 72 char**；Analyzer 失败，38 次工具调用额度用尽，未产出调谐结果。固定步骤中的瓦窑 COCO/eCOCO 和调谐成功不能计入这两个模型会话。公开工具说明已澄清 matrix/path；接下来更有价值的是在各方法边界校验数据类型与枚举，并支持跨菜单传递有类型的输出字段。

**测试版本。** 实例使用 `d7d0a608` 的插件逻辑；整章通过安装包执行的驱动提交为 `54219e9d`。随后在 `1743c298` 补足了工具参数说明：`matrix` 读取数值，`path` 只传文件名，同时让无 MATLAB 时的错误明确说明 Runtime 限制。上面的模型成绩属于修改前，不能当作新提示已经有效的证据。

**MATLAB Runtime 部署。** [无 MATLAB 可执行文件时的公开注册工具探针](evidence/runtime-probe.json)能列出菜单，科学 Helper 则失败。这个探针没有安装 MCR。判定部署不可行还来自[生产启动代码](../../overlay/src/acycle_deepseek/tools.py)：它调用 `matlab -batch`、挂接源码并执行 JSON 桥接；发布物没有为此编译的 standalone 或 CTF。MathWorks 所说的 [MATLAB Runtime](https://www.mathworks.com/help/compiler/about-the-matlab-runtime.html) 是执行已编译产物所需的运行库，不能提供上述解释器。部分高层调用可以在已配置的 GitHub 后端计算；[菜单](../../overlay/src/acycle_deepseek/menu.py)与 native 仍要求本地后端。本次云端 MATLAB relay 仅供验收。

若要支持 Runtime-only，建议单独交付 `acycle-worker request.json response.json`。开发端用 MATLAB Compiler 固化注册表、动态分派到的算法和科学资源，保持当前科学接口和日志格式；用户端启动这个程序，匹配相同 release、同级或更高更新的 Runtime。发布验收应使用没有完整 MATLAB 的干净机器，重跑同一组谱、图、日志和重放检查。没有必要在这一阶段改写 Helper/Analyzer/Plotter。

**复跑：**

1. 整章：运行本分支的 `User Guide through installed Acycle Harness tools` 工作流。三个包中的 `graded/<序号-步骤>/public-*` 对应各步骤，`ws/.acycle/runs` 中是原生日志及 MAT 引用。使用 `grade_installed.py ARTIFACT_DIR harness/validation/user-guide OUT.json`，三个下载的 ZIP 分别命名为 `insolation.zip`、`etp.zip`、`wayao.zip`。
2. 对话：从 `python harness/build.py DEST` 装好插件与 Python 包，按插件说明配置官方 DSH SDK 和 MATLAB。用 `make_scenarios.py REPO scenarios.json` 固定提示和 SHA。运行 `DEST/scripts/harness_conversation.mjs --runtime SDK_DIR --scenarios scenarios.json --case etp --workspace FRESH_DIR --plugin DEST/plugin/index.mjs --mode live --acycle-only --model deepseek-flash --output receipt.json`，其他案例替换 case 并使用新的 workspace。在受信的本地运行环境提供凭据；任务文件、数值进程和 GitHub 工作流都不需要模型密钥。
3. 本次分离部署的纯数值工作器只接受这些公开样本的哈希、已经验证来源的产物引用和科学参数。返回的每个归档与新的 run/commit 核对后，才交还正在等待的 Harness。运行 `grade_live.py STUDY REPO OUT.json` 可重新核对首轮完整数组及运行产物哈希；`grade_followups.py STUDY OUT.json` 可从 SDK 记录和新产物重建后续调用清单。
