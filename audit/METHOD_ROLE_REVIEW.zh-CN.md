# 方法接口评审与归并边界

评审对象是 Hypercinnabar 中封装 GUIDE 最后快照 `b52ea9f` 与 Acycle 3.1.1 快照 `dcba427` 的 MATLAB 文件。归并的判断单位是一次调用需要的输入、用户希望保存的结果，以及再次绘图是否需要重算。维护目录可以覆盖多个操作。只在不同选项仍能解释同一份输入和结果时，才由一个接口按 `params` 分派。[逐项方案](MODULE_CONSOLIDATION.zh-CN.md) · [菜单和包名反查](modules/consolidation_index.tsv) · [每个角色的来源](modules/roles.tsv)

## 当前接口做到了哪一步

| 接口 | 现有代码与可复查的行为 | 新接口的验收条件 |
| --- | --- | --- |
| `helper` | 3.1.1 等距插值接受只给 `options.MaximumPoints` 的结构，保留该值并补 `MaximumElements`。功率谱能补齐 `models` 中缺失的开关，但将 `nfft` 直接设为行数。数字化追踪先执行 `r=p`，之后无条件把 `mode` 设为 `Loose`、把 `existingPixels` 清空。 | 从最小必要输入出发，先解析选择，再补激活分支中遗漏的字段，包括嵌套结构。合法的显式值应保留，包括 false、0 和有科学含义的空值。缺必需数据、冲突的显式选择要报错。把已解析输入再交一次，应保留设置和已完成的数据处理；例如不要再次中心化或丢掉已有追踪点。[等距插值](../matlab/+acmaster/+RegularInterpolation/helper.m) · [功率谱](../matlab/+acmaster/+PowerSpectrum/helper.m#L37) · [追踪](../matlab/+acmaster/+DigitizeTrace/helper.m#L8) |
| `analyzer` | 3.1.1 等距插值在调用原函数前检查两项上限，缺项写 `error` 并以 `cancelled` 结束。GUIDE 功率谱省掉 `noise` 会直接返回不含背景模型的谱。3.1.1 功率谱检查六个标志，但 robust 模型读取 `fitModel` 位于模型计算的 try/catch 内；删掉此项，主谱仍返回，该调用被记为 `incomplete`。 | 全部激活分支的输入先验完，再开始数值计算，并给既有原函数显式全参，含有意义的关图开关。缺参立即报错；参数齐全、运行后某项确实算不出时才保留部分结果。原函数可单独保留旧缺省调用方式。[严格插值](../matlab/+acmaster/+RegularInterpolation/analyzer.m#L8) · [GUIDE 功率谱](../matlab/+acmethods/+PowerSpectrum/analyzer.m#L60) · [3.1.1 模型入口](../matlab/+acmaster/+PowerSpectrum/analyzer.m#L46) · [读取 robust 参数](../matlab/+acmaster/+PowerSpectrum/analyzer.m#L192) |
| `plotter` | `ShowImage` 自建 figure 并返回空，`DataDistribution` 自建窗口后调用 histfit。SWA 还会按名称找旧图、清窗、选择当前坐标轴；把这类函数直接嵌进 GUI 可能清掉调用方的图。双谱原函数已返回命名图形句柄，仍自己创建窗口。[ShowImage](../matlab/+acmethods/+ShowImage/plotter.m) · [SWA](../matlab/+acmethods/+SWA/plotter.m#L48) · [双谱原函数](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralPlot.m#L97) | 预览可以从 Helper 的 `plt.dat` 画原始或整理后的数据，`plt.res` 初始为空，得到 Analyzer 的 `retval` 后再填入。绘图配置与两者同层。纯展示操作允许 `res` 一直为空。整图负责布局，能单独画的面板接收明确目标轴，重要对象可用稳定名称定位。改变样式时用原结果重画。 |
| 调用记录与重放 | 789 个旧入口均采用 `[retval,id] = 角色(params,id)`，省略或传空 id 会另建记录。已有非空日志的 id 再调用会报错。`aclog.replay` 恢复原版本、原参数和初始随机状态，生成新调用记录。 | 新接口可由调用方先分配 id，再取唯一的科学返回值。是否仍提供第二个返回值留作 ABI 决定。一次公开调用占一条记录，工作流可关联各步骤的 id。把 `override` 放在 rerun 等重放入口，科学参数改动重算，纯图形参数改动重画。当前 replay 只接收 id。[调用记录](../matlab/+aclog/invoke.m) · [重放](../matlab/+aclog/replay.m) |

上表的 `plt.dat`、`plt.res` 和 override 的位置反映正在讨论的方向。顶层返回结构的精确形状、plotter 如何接收目标、返回瞬时句柄还是可保存的成果引用，都还可以调整。回放文件只需要能重建目标面板的说明、输入及展示配置。MATLAB axes 和 figure 句柄只在本次进程使用；目前 Logger 会将整个入参保存成 MAT，直接给旧接口塞句柄会把 GUI 状态一起带进记录。[引用持久化](../matlab/+aclog/store.m)

两版现有角色分布如下。最后两列为移植时的定位线索，按忽略全行注释后的源码逐文件搜索独立词 `gca` 或 `gcf`，不分析间接调用或字符串的语义。

| 快照 | helper | analyzer | plotter | 直接出现 gca 或 gcf 的 plotter | helper 中直接出现 .plt |
| --- | ---: | ---: | ---: | ---: | ---: |
| GUIDE | 89 | 218 | 81 | 44 | 0 |
| 3.1.1 | 71 | 266 | 64 | 26 | 0 |

[原生 MATLAB 契约探针](tests/probeMethodRoleContracts.m) 走真实公开入口，覆盖部分插值参数、严格缺项及日志、谱的两类缺项、显式 nfft、当前坐标轴及空图形返回值。它抽查代表性契约。全量对账核对 789 条版本化标识、角色和源码去向。数值等价性仍按操作分别验收。[CI 工作流](../.github/workflows/guide-methods.yml)

两个具体接口说明怎样减薄封装。3.1.1 的 `RegularInterpolation.analyzer` 校验参数、直接调用原函数、交还原结果和元数据，适合作为已有独立函数的范例。`TwoSampleTests.analyzer` 则把原 GUI 回调第 96–342 行作为一个照抄块放进公开入口，最后只导出格式化的 `multilineText`。归并时可让入口按已解析的检验名选择实现，各分支仍调用现有的 `ttest2`、`vartest2`、`ranksum` 等，并将需要保留的报告代码放进 `code/method/`，用 `%%` 标明原行段。如果要增加可机读的统计量，应给新结果明确定义，旧报告可逐行核对。角色的版本化登记只应指向已验收的操作；第一轮 `roles.tsv` 的 `proposed_route` 是历史提议，`op` 与 `wrapper_path` 仍可用于定位兼容实现。[等距插值原函数调用](../matlab/+acmaster/+RegularInterpolation/analyzer.m#L9) · [双样本长回调](../matlab/+acmethods/+TwoSampleTests/analyzer.m#L11) · [新版对应](modules/consolidation_index.tsv)

## 哪些功能应拆开

**统计。** 建议从旧的描述统计、假设检验、相关与协方差、回归四项得到九个操作。将原列在“序列与数学”的 PCA 归入多变量统计，共十个。五个检验各有原入口。保留单样本 t、双样本检验、指定分布的卡方拟合优度、综合正态性、单因素 ANOVA。双样本原窗口用五个 tab 选择 t、F、Mann–Whitney、双样本 KS、Anderson–Darling；保存选择后可以共用入口。相关分析同时计算 Pearson、Spearman、Kendall，旧接口把数字格式化进 `stats`。协方差另返回矩阵和 Bootstrap 区间并消耗随机数。将来给相关系数增加原精度数值字段，应登记新的结果契约。GUIDE 线性回归的 fitlm 来自发行包恢复候选，master 的 polyfit 是另一实现。[双样本](../matlab/+acmethods/+TwoSampleTests/analyzer.m) · [相关](../matlab/+acmethods/+Correlation/analyzer.m) · [协方差](../matlab/+acmaster/+Covariance/analyzer.m) · [回归恢复来源](../matlab/+acmethods/+LinearRegression/analyzer.m#L11)

**图像与展示。** 序列图、分布图和显示图像各保留可重画视图；分布图原来调用 `histfit(...,'kernel')` 并标注统计量，接口未返回密度估计。采样间距本身是数值结果，等距判断是多处复用的原函数。声音转换的结果是 `y,Fs`，播放属于设备。颜色转换返回像素矩阵，可委托图像视图展示。沿折线的图像剖面返回采样点、距离或通道值。数字化分两个入口，给定标定信息把像素映射到数据坐标，以及从种子追踪一段曲线。鼠标取点、缩放和拖拽属于 GUI，点击得到的坐标和种子应成为可保存的输入。GUIDE 的追踪依赖缺口、替代引擎及 3.1.1 的 Strict/Loose 路径继续区分。[分布图](../matlab/+acmethods/+DataDistribution/plotter.m) · [声音](../matlab/+acmethods/+SeriesSound/analyzer.m) · [剖面](../matlab/+acmaster/+ImageTransect/analyzer.m) · [像素标定](../matlab/+acmethods/+Digitize/analyzer.m) · [3.1.1 追踪](../matlab/+acmaster/+DigitizeTrace/analyzer.m)

**Mini-Robot。** 两版主窗按钮都先枚举选中的文件，再为每个输入打开一个 RobotGUI。每个窗口接收一条 `data_filterout` 和单位，处理顺序为清理与初图、可选插值、去趋势、全段谱、演化 FFT、小波，中间夹有暂停和可选写文件。GUIDE 只在间距不齐的条件下进入插值，3.1.1 还检查用户选择的目标步长是否变化，并在重采样后更新谱上限和小波最短周期。小波失败时原代码会以一半的最长周期再试一次。工作流要能说明实际执行的参数、重试和跳过的步骤。从 GUI 中抽出每条序列的一份版本化配方即可供 Harness 和将来的节点编辑器调用。多文件选择和显示进度由前端管理，每个文件和执行步骤的调用记录可关联；旧窗口和配方可并行保留。当前清单中两版的 Robot 均没有独立的可重放角色。[GUIDE 主窗](https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L1053) · [3.1.1 主窗](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m#L2018) · [GUIDE 插值](https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/RobotGUI.m#L453) · [3.1.1 固定流程](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/RobotGUI.m#L268)

**验证工具。** 旧归属的九个 master 入口可逐项反查。一个双谱确定性自测归方法测试，两个双谱案例验证分别覆盖五组示例和 LR04/CENOGRID 实测资料。五个 COCO/eCOCO `run*` 是研究配方，保留数据清单、随机设置、检查点和输出位置。余下的 `validateCocoPublicationValidation` 读取已有成果，复核保存的零分布、模拟数、种子及 manifest；可在不重新计算谱的情况下单独运行。让 Harness 按名选择案例或发表配方，使一次普通分析的成本和产物保持明确。[九项逐一对应](MODULE_CONSOLIDATION.zh-CN.md#验证与诊断) · [原始引入记录](MODULE_BOUNDARIES.zh-CN.md#九个验证工具何时加入) · [只读成果复核](https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/validateCocoPublicationValidation.m#L1)

## 实施顺序

1. 用等距插值走通“传部分参数 → 保留显式值并补全 → 全参计算 → 保存并重放”。用协方差验证随机状态，减去一个激活字段验证直接调用和 GUI 调用一致报错。
2. 用图像转换与剖面走通“在已有轴预览 → 返回数值 → 替换样式只重画”。同一测试中放两个面板，确认重画一个不会清掉另一个。
3. 用全段谱验收多分支输入；逐项比较两版结果和不完整原因。独立 SWA 的 master 专用 analyzer 尚缺，Undatable 的 master 包目前只有 plotter，保留两版角色清单中的差异。
4. 在这些子操作可独立运行后，以 Mini-Robot 验收顺序、跨步骤设置和部分成功，再接案例工作流与节点编辑器。抽出的实现放在普通目录 `code/method/`；按模块归位时可保留全局唯一函数名与调用标识。历史角色按其版本回放。[目录约定](../code/method/README.md) · [角色覆盖](modules/package_to_modules.tsv)
