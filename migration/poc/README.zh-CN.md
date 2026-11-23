# Acycle 代码式桌面 PoC

发行包解压后，在 MATLAB 中进入解压目录，运行 `ac`。用 `ac('/path/to/data')` 可以直接打开某个数据目录。命令行脚本先运行 `setup_acycle`。桌面和科学函数的参考版本分别是移除 GUIDE 前的 `b52ea9f` 和 master 的 `dcba427`。

从迁移仓库构建需要 Python、NumPy、SciPy 和两个已初始化的子模块。构建器输出独立目录。将其复制到另一台安装了 MATLAB 及对应工具箱的计算机后即可使用。

使用外置轨道参考表时，在 `setup_acycle` 或 `ac` 之前设置 `ACYCLE_REFERENCE_DATA`。原有参考表目录可以继续使用。

```sh
git submodule update --init
python -m pip install numpy scipy
python migration/poc/build.py --output .acycle-runtime
```

## 桌面与版本

主窗口和 32 个子窗口的控件以 MATLAB 代码创建。控件位置、显示状态、标签、菜单层级和快捷键取自旧版。保留旧版的单位、排序、语言、数据点选、专用窗口和 Mini-Robot。新双谱和设置采用 master 的窗口。用户保存和打开的结果图仍支持 MATLAB 的 FIG 格式。两份固定上游源码仅用于构建，发行包的布局和启动均无需 GUIDE。

首次打开主窗口时，如果旧版按显示器尺寸计算的位置超出了屏幕，桌面会将窗口移回可见区域。

`accore.register()` 列出菜单、默认操作和角色。两个版本都提供的操作在原有菜单下优先选 `_legacy`。更改 `Operation` 可以选具体实现。GUI 通过 Core 获取文件目录、读入序列并分派菜单。带通、去趋势、SWA、图像剖面和新增双谱的科学计算均有独立记录。其他专用窗口保留迁移后的交互回调，其中仍有直接计算；窗口操作记录及独立科学调用记录的粒度不同。

## MATLAB CLI

```matlab
setup_acycle
t = (0:255)';
x = [t, sin(2*pi*t/20) + .2*cos(2*pi*t/5)];
s = accli.filter(x);
m = accli.filter(x,'Operation','Bandpass');
s2 = accli.rerun(s,struct('flow',.04,'fhigh',.06));
ax = axes('Parent',figure);
s2 = accli.replot(s2,struct('panel','fft'),ax);
s3 = accli.apply(s2,[t,cos(2*pi*t/21)]);
s3 = accli.restyle(s2,s3,ax);
res = accore.replay(s2.ids.analyzer);
accore.io('save','analysis.mat',s2);
s2 = accore.io('load','analysis.mat');
res = accore.replay('analysis.mat','analyzer');
```

每个菜单提供一个具名 CLI 包装函数，例如 `accli.filter`、`accli.prewhiten`、`accli.bispectral`。显式输入结构适用于多序列、图像及标定点。可用 `accli.run(tag,input,...)` 按菜单执行。有 Analyzer 时默认只取结果，传入 `'Plot',true` 或目标轴即可出图。只有 Plotter 的入口默认执行其绘图或桌面动作。旧式纯桌面操作需要打开主窗口。仍依赖外部数据库或工具箱的方法沿用原有运行条件。

### Mini-Robot

工具栏对选中的每个文件打开一个独立设置窗。运行按钮与 `accli.miniRobot` 执行同一个单序列流程。准备、插值、去趋势、全段谱、演化谱、小波依次按设置运行。旧版只在间距不均时插值，master 在请求改变目标间距时也会插值。CLI 默认隐藏过程图并返回各阶段的数值结果。保存和绘图可分别开启。

```matlab
opts = struct('trend','linear','spectrum',false,'evolutionary',false,'wavelet',true);
r = accli.miniRobot(x,'Settings',opts,'Unit','m','UnitType',1);
r2 = accli.miniRobot(x,'Operation','Robot','Settings',opts);
again = accore.replay(r.id);
```

两个固定版本的 RobotGUI 都调用了发行时缺失的 `waveletML`。PoC 恢复上游最后一次删除前的同名函数，保留其 Morlet、AR(1) 显著性及失败后将最大周期减半再试的约定。构建时校验原始 Git blob。[上游历史源码](https://github.com/mingsongli/acycle/blob/aacef8571055b14cbc77ec61efb0e8f7875810dd/code/package/wavelet/waveletML.m)

交互窗口可用 `getappdata(window,'AcycleAnalysis')` 取得上次成功的分析。CLI 可从这份数据改参数或只改图。带通的 `fft` 面板在两版都有，旧版的第二个面板为 `mtm`，master 对应位置展示 `filtered`。可交换 MAT 文件包含实参、数据、结果、显式设置和本次各角色的日志与快照。换到新的日志目录后，用 `accore.replay('analysis.mat','analyzer')` 可从包内恢复原始参数和随机状态。Mini-Robot 对应的角色名为 `workflow`。
