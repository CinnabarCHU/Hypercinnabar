# Acycle 代码式桌面 PoC

发行包解压后，在 MATLAB 中进入解压目录，运行 `ac`。用 `ac('/path/to/data')` 可以直接打开某个数据目录。命令行脚本先运行 `setup_acycle`。桌面和科学函数的参考版本分别是移除 GUIDE 前的 `b52ea9f` 和 master 的 `dcba427`。

从迁移仓库构建需要 Python、NumPy、SciPy 和两个已初始化的子模块。构建器输出独立目录。将其复制到另一台安装了 MATLAB 及对应工具箱的计算机后即可使用。

```sh
git submodule update --init
python -m pip install numpy scipy
python migration/poc/build.py --output .acycle-runtime
```

## 桌面与版本

主窗口和 32 个子窗口的控件以 MATLAB 代码创建。控件位置、显示状态、标签、菜单层级和快捷键取自旧版。保留旧版的单位、排序、语言、数据点选、专用窗口和 Mini-Robot。新双谱和设置采用 master 的窗口。用户保存和打开的结果图仍支持 MATLAB 的 FIG 格式。两份固定上游源码仅用于构建，发行包的布局和启动均无需 GUIDE。

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
s2 = accli.replot(s2,struct('panel',1),ax);
s3 = accli.apply(s2,[t,cos(2*pi*t/21)]);
s3 = accli.restyle(s2,s3,ax);
res = accore.replay(s2.ids.analyzer);
accore.io('save','analysis.mat',s2);
s2 = accore.io('load','analysis.mat');
```

每个菜单提供一个具名 CLI 包装函数，例如 `accli.filter`、`accli.prewhiten`、`accli.bispectral`。显式输入结构适用于多序列、图像及标定点。可用 `accli.run(tag,input,...)` 按菜单执行。运行默认只取结果，传入 `'Plot',true` 或目标轴即可出图。旧式纯桌面操作需要打开主窗口。仍依赖外部数据库或工具箱的方法沿用原有运行条件。

交互窗口可用 `getappdata(window,'AcycleAnalysis')` 取得上次成功的分析。CLI 可从这份数据改参数或只改图。可交换 MAT 文件包含实参、数据、分析结果及显式设置。按 id 精确重放还需要相应的日志和快照。
