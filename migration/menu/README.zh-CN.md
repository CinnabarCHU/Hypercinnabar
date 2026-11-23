# Acycle 菜单接口初步归并版

这份实现在同一组 MATLAB 函数中提供 master 与 GUIDE 两版的选择。按 Acycle 3.1.1 主窗口查功能，选定菜单后，`params.operation` 决定运行哪个实现。参考快照为 [master dcba427](https://github.com/mingsongli/acycle/tree/dcba4279168745b563e0535b954297023dd62fc7) 和 [GUIDE b52ea9f](https://github.com/mingsongli/acycle/tree/b52ea9f510f3be00bde9a0238b9898a1e2315b74)。[完整菜单与选择值](MENUS.md) · [机器清单](../../code/interface/catalogue.json) · [两版逐菜单差异](../master/menus.tsv)

## 查菜单、选版本

```matlab
setup_migration
m = acMenuCatalog('menu_filter');
disp(m.choices)
catalog = acMenuCatalog();
engine = catalog.engines(strcmp({catalog.engines.operation},'Bandpass_legacy'));
disp(engine.roles)
disp(engine.required)
```

公开文件放在 `code/interface/<主菜单>/<子菜单>/`，例如 `acMenuFilter_helper.m`。同一菜单的两版共用函数名。master 如 `Bandpass`，GUIDE 如 `Bandpass_legacy`。每个菜单有一个写明的推荐选择，只有 helper 使用它。analyzer 接收的结构必须已经指定操作。若选中的快照不提供所需角色，会报出对应错误。可在清单中查看各操作的角色和参数。旧 journal 仍按原先登记的操作与版本重放。

原始清单中有 135 个菜单标签，128 个在固定的 master 中有声明，7 个只出现在 GUIDE。另外收录两版的工具栏按钮 Mini-Robot。保留子菜单标题及隐藏状态供前端重建导航。所有 388 个 GUIDE 角色和 401 个 master 角色可在现有菜单层定位。两个快照的 MATLAB 包保留为具体实现和老入口兼容层。新增的公共接口与适配函数均有唯一的项目级文件名。[旧角色和源码索引](../../audit/modules/roles.tsv)

| GUI 中的实际位置 | 此版如何调用 |
|---|---|
| Math → Interpolation / Interpolation Pro | 保留主窗口的两个入口。普通插值默认 `interpolate`，GUIDE 为 `interpolate_legacy`。同一菜单的 `RegularInterpolation` 允许多列输入，可设置采样网格上限，结果附带网格元数据。 |
| Math → Data Transformations | 同一接口内，`params.operation` 选快照或独立变换，`params.j` 等字段保持原变换的含义。 |
| Timeseries → Spectral Analysis / Filter | 前者在同一版 `PowerSpectrum` 下传估计器和背景模型选择，后者保留 `Bandpass`、`PassFilter` 及相关核函数。[两版谱差异](../master/README.zh-CN.md) |
| Univariate / Bivariate | 跟随 master 的菜单位置。单样本 t、双样本、正态性、卡方、ANOVA、相关、协方差和回归可以分别定位。 |
| Math → Image、Plot Digitizer | 显示、颜色变换、图像剖面和数字化保留各自菜单。追踪用 `DigitizeTrace` 或 `DigitizeTrace_legacy`。后者保持历史对缺失追踪依赖的处理。 |
| Timeseries → Bispectral Analysis、Correlation Coefficient (COCO/eCOCO) | 三个双谱和六个 COCO 验证或发表脚本按名选择；常规分析的默认选择分别是 `Bispectral`、`ecoco`。 |
| GUIDE 保留项 | TimeOpt、eTimeOpt、Lyapunov 等项保有原角色及 `_legacy` 选择。撤掉的 DYNOT v2 和 Lag-1 v2 项保有原菜单标签，在现有相关菜单下也可查到其科学实现。 |
| 桌面操作与 Mini-Robot | `Desktop` / `Desktop_legacy` 调用已打开的相应版本主窗口。Mini-Robot 保留为工具栏按钮，由 `Robot` / `Robot_legacy` 进入原工作流。选文件、点选和批处理暂停仍依赖实际桌面状态。 |

## 三个公开角色

| 入口 | 参数、返回和重放 |
|---|---|
| `h = …_helper('input',input,'override',override,'id',id)` | `input` 接受单个结构，也可作为首个位置参数。没有原始输入的资料入口可省略。仅此角色接受部分 `override.params` 和 `override.plt`。可在 `input.operation` 或 `override.params.operation` 选择版本。返回且仅返回三个同层字段 `h.params`、`h.plt`、`h.dat`。 |
| `res = …_analyzer(params,id)` | `id` 可省略。必填字段及激活分支的参数在计算前检查；未提供时直接报错并结案。提供所选版本原本的科学返回值，保留部分完成时的状态。 |
| `p = …_plotter('plt',plt,'dat',dat,'res',res,'params',params,'target',ax,'id',id)` | `plt` 可作首个位置参数。按图件需要传入解析过的配置、绘图数据、已有结果或计算参数。运算数据和配置可分别保管。返回原绘图入口的成果；许多 Acycle 图件原本返回空。 |

`dat` 存随输入或 helper 生成的绘图数据，`plt` 存配置。数值计算需要的数据保留在 `params`。有的旧绘图入口还要求提供额外的数据或设置，例如文件名及物理单位；机器清单的 `plotFields` 展示该实现直接读取的字段。无原生推荐函数的操作，helper 从给定的输入分配字段，调用方仍须提供相应原始数据和配置。直接把一版的完整字段改个后缀喂给另一版，可能因两版选项不同而失败。从同一原始输入分别运行 helper，可以得到两版各自适用的结构。

```matlab
t = (0:255)';
input = struct('data',[t,sin(2*pi*t/20)+0.2*cos(2*pi*t/5)]);
h = acMenuFilter_helper('input',input,'override',struct('params',struct('operation','Bandpass')));
id = acMenuNewId();
res = acMenuFilter_analyzer(h.params,id);
assert(isequaln(res,aclog.replay(id)))
acMenuFilter_plotter(h.plt,'dat',h.dat,'params',h.params,'res',res);

old = acMenuFilter_helper('input',input,'override',struct('params',struct('operation','Bandpass_legacy')));
r0 = acMenuFilter_analyzer(old.params);
```

传入一个已有的 axes 时，单面板图使用该轴。多面板图可指定 `plt.panel`（从 1 开始，由上到下、同排从左到右，或唯一的原始 Tag）。给 figure 则可放入原图布局，多个来源窗口可用 `plt.figureIndex` 选择。原始绘图代码负责选线、统计量、配色和坐标轴。嵌入时先让原实现画图，再复制到指定目标。主窗口菜单、文件导出和播放等有独立副作用的操作须使用相应入口。桌面控件的回调和外部宿主状态不随科学图件持久化。

```matlab
im = uint8(randi(255,24,32,3));
h = acMenuRgb2lab_helper(struct('im_name',im));
r = acMenuRgb2lab_analyzer(h.params);
ax = axes('Parent',figure);
h.plt.panel = 2;
acMenuRgb2lab_plotter(h.plt,'res',r,'target',ax);
```

两版信号生成器的红噪声分支和独立 `redmark` 都在原函数内按时钟重设正态随机数发生器。菜单 helper 记录原来的时钟种子表达式并返回 `params.seed`，也接受显式种子。analyzer 使用相同的旧式随机数发生器和原版一阶滤波公式，在返回时恢复调用方的随机状态。这样，重放可以逐样本重建同一条红噪声序列。[数值适配及出处](../../code/method/acMenuRedNoise.m)

## 日志与导出

每次公开调用使用独立 id，可用 `acMenuNewId()` 预留正整数。省略、置空或传入未登记的 id 时，logger 为这次调用分配临时记录，在命令行输出带日志位置的 JSON，首次提示一次。错误以 `error` 和 `fin.status='cancelled'` 结案。旧入口报告的 `incomplete` 在归并后继续传出。文件夹中保存输入、结果和初始随机状态；图形目标仅保存类型和面板选择。重放会新建图形目标，保留原宿主窗口。原生桌面命令的日志可重放命令本身；结果仍取决于窗口当时打开的文件、已有选区和交互决定。

```sh
python migration/menu/build.py
python migration/export_method.py --revision menu menu_sound menu_imshow --output ../acycle-menu-methods
```

在导出目录运行 `setup_method`。其中仅登记所选菜单及其操作；含桌面回调的导出同时携带相应固定快照的源码与资源，以支持按名称和工作区查找的旧代码。只需要传统数值包时仍可单独导出 GUIDE 或 master 包。代码生成器对账每个旧角色、源文件及新菜单入口；原生 MATLAB 测试覆盖双版本数值、缺项错误、快照重放、外部坐标轴和独立导出。[测试入口](../../tests/test_menu_interfaces.m) · [自动化工作流](../../.github/workflows/guide-methods.yml)
