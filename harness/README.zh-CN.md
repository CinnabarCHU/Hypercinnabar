# Acycle 的 DeepSeek Harness 插件

这个分支把 Acycle 的菜单接口装进 DeepSeek Harness。Python 负责传递参数、保存每次运行和交付文件，科学计算和绘图仍由已有的 MATLAB 方法完成。GUI 和 CLI 可以独立调用同一组接口。

## 安装

需要 Git、Python 3.10+、Node.js 24.9+、本机有许可的 MATLAB 和所选方法使用的工具箱。下面从源码生成 Python wheel 和 Cordis 插件包。也可在本分支通过的 Actions 运行中下载同名的两件套，跳过构建。

```sh
git clone --branch acycle-harness-menu --recurse-submodules https://github.com/CinnabarCHU/Hypercinnabar.git
cd Hypercinnabar
export ACYCLE_MENU_ROOT="$PWD"
export ACYCLE_ROOT="$PWD/upstream/master"
python3 harness/build.py ../acycle-harness-src
python3 -m venv ../acycle-harness-env
. ../acycle-harness-env/bin/activate
python -m pip install build
mkdir -p ../acycle-harness-src/dist
python -m build --wheel --outdir ../acycle-harness-src/dist ../acycle-harness-src
(cd ../acycle-harness-src/plugin && npm pack --pack-destination ../dist)
python -m pip install ../acycle-harness-src/dist/acycle_deepseek-0.6.0-py3-none-any.whl
```

在 DeepSeek Harness 所在的 npm 项目中安装本地 `dsh-acycle-0.6.0.tgz`，然后把下面条目加入现有 Agent preset 的插件列表。请将四个绝对路径换成本机的值。原 Web 部署脚本继续使用它固定的 `0.2.1-rc.3` 组合，支持 `--menu-root`。在 `0.2.2-rc.5` 的宿主中，使用已启用官方 native tool executor 的 preset。

```json
{
  "id": "acycle-native",
  "name": "dsh-acycle",
  "config": {
    "python": "/absolute/path/acycle-harness-env/bin/python",
    "workspace": "/absolute/path/study",
    "menuRoot": "/absolute/path/Hypercinnabar",
    "acycleRoot": "/absolute/path/Hypercinnabar/upstream/master",
    "matlabExecutable": "matlab",
    "backend": "local"
  }
}
```

`menuRoot` 指向含 `setup_migration.m` 的检出目录，`acycleRoot` 供原有工具和原生源码接口使用。插件离线携带菜单索引，执行菜单时会复核检出目录内的索引哈希。源码组合见本分支三个固定的公开子模块。原生目录有 337 个源码入口，菜单索引含两版的 136 个菜单标签，其中 118 项有角色入口。同一方法可以挂在多个菜单下。

## 从文件到可重放的结果

| Harness 工具 | 输入与返回 |
| --- | --- |
| `acycle_menu_catalog` | 用 `query` 查菜单，用 `menu` 枚举该菜单的版本和方法，用 `menu` 加 `operation` 查询所需字段和上游角色。 |
| `acycle_menu_helper` | 接受 `input` 和可选的 `override.params`、`override.plt`。完整的 `params`、`plt`、`dat` 随返回的 `run_id` 保存在 MATLAB 日志中。 |
| `acycle_menu_analyzer` | 传同一菜单的 `helper_run_id`，或显式传入完整 `params`。必需参数缺失时报告错误。 |
| `acycle_menu_plotter` | 可传 `helper_run_id` 与 `analyzer_run_id`，也可传完整的 `plt`、`dat`、`params`、`res` 分支。按需选 `target` 为 `original`、`figure` 或 `axes`。已渲染的图作为 PNG 交付。 |
| `acycle_menu_replay` | 用已有的 `run_id` 重放该次角色调用，使用日志保存的输入和初始随机状态，返回新的 `run_id`。 |

例如，对工作区的两列数据 `series.csv` 做等距插值，先调用 `acycle_menu_helper`。

```json
{"menu":"menu_interp","input_path":"series.csv","input":{"operation":"RegularInterpolation","samplingInterval":1}}
```

再调用 `acycle_menu_analyzer`。这里的字符串换成前一步返回的实际 ID。

```json
{"menu":"menu_interp","helper_run_id":"<helper run_id>"}
```

若要对照 GUIDE，在查询结果中选择带 `_legacy` 的选择符，例如在 `menu_rgb2gray` 下选择 `RGBToGray_legacy`。同名菜单的两组运行各有独立记录。数值矩阵可用 CSV/TXT/DAT/TSV，图像使用 `input_kind: "image"` 以保留像素类型，接收文件名的方法使用 `input_kind: "path"` 并指定 `input_field`。输入文件会复制到该次运行并计算 SHA-256。读取额外文件或目录的方法重放时仍需要对应资源可用。

工具返回的摘要展示 MATLAB 类型、尺寸和数值预览，也能看到嵌套在 options 中的推荐参数。较大的结构体会标记省略的字段数。完整输入、结果和随机状态可在 `.acycle/runs/<run_id>/outputs/acycle-journal.zip` 中取得。该 ZIP 包含 journal 和相邻 MAT 引用文件，可解压后在相应检出目录设置 MATLAB 路径，调用 `aclog.replay` 重放。出错时可用原有的 `acycle_get_run` 取回诊断和已落盘的日志。菜单执行和按 ID 重放使用本地 MATLAB 后端。两版科学方法的差异、可用绘图角色、桌面交互和工具箱要求由菜单和原方法决定。桌面启动器仍可查询；需要桌面或人工交互的功能应在具备相应上下文的宿主运行。

原有的 `acycle_analyze`、`acycle_swa`、`acycle_coco` 等快捷工具，以及 `acycle_catalog`、`acycle_native` 均可继续使用。为已有原生 Harness 安装升级时，应同时替换插件和 Python wheel。科研计算仍按本机 MATLAB 许可执行。

## 验证

本分支的工作流从实际打出的 wheel 和 npm 包安装，分别在两个官方 DeepSeek Harness 工具运行时调用插件。端到端部分把同一张 RGB 图走完 master 和 GUIDE 的 helper、analyzer、plotter 和 replay，核对六个像素灰度以及 PNG 和 journal，并用独立的数值序列核对等距插值和缺参诊断。Actions 另附这些运行留下的原始记录。[验证工作流](../.github/workflows/acycle-harness-menu.yml)
