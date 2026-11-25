**Acycle GUI + Harness 0.7.0 本地试用包**

先解压整个 ZIP，再操作其中的文件。GUI 和插件来自已通过 MATLAB R2024b 实窗验收的版本，本包另附启动入口、合成数据、环境安装器和本机检查命令。

**先试 GUI**

1. 打开 MATLAB，把 Current Folder 切换到含本说明和 `start_local_demo.m` 的解压目录。
2. 在 MATLAB 命令窗口运行下面一行。

```matlab
start_local_demo
```

会打开 Acycle 主窗口和 `series.csv` 的带通滤波预览，坐标单位设为米。可以调整频率、坐标范围，并用原来的 **Save Data** 按钮保存滤波结果。结果文件写入包内的 `study/`。

需要已安装且有许可的 MATLAB。示例使用 Signal Processing Toolbox、Statistics and Machine Learning Toolbox 和 Image Processing Toolbox。验收环境为 R2024b，运行完整版其他功能时还需相应工具箱。MATLAB Runtime-only 部署另需编译产物。

**再试 Harness 与窗口协作**

先安装 Python 3.10+ 和 Node.js 24.9+，然后在操作系统终端中进入解压目录。下面以 macOS / Linux 的 `python3` 为例，Windows PowerShell 中可以替换为 `py -3`。

```sh
python3 local_test.py prepare
python3 local_test.py check
python3 local_test.py filter
```

`prepare` 在包内的 `.test-env/` 建立 Python 环境，并安装发行包中的 wheel、插件和固定为 `0.2.2-rc.5` 的官方 Harness 工具执行器。首次安装 npm 依赖需要联网。`check` 读取正在运行的示例窗口。`filter` 将同一个窗口的频带改为 **0.035–0.055 cycles/m**，频谱横轴上限改为 **0.13 cycles/m**，随后再读取窗口以确认修改。终端显示 `PASS`，回执写到 `generated/local-filter.json`。

保持 MATLAB 主窗口打开。关闭后再次执行 `start_local_demo` 会生成新的连接配置。移动整个解压目录后，重新解压并安装本地测试环境。

图像剖面可以这样测试。

```sh
python3 local_test.py image
```

在新窗口中点选两个或更多顶点。可以点击 **Undo point** 撤销，完成后点击 **Finish profile**，然后回终端执行下面的命令。

```sh
python3 local_test.py events
```

返回的完成事件会带有顶点坐标、样本数量和 Analyzer ID。也可以在完成前关闭图像窗口，检查取消事件。上述检查命令直接通过官方 Harness 工具执行器调用插件。

**接入你已有的 Harness 聊天环境**

1. 在现有 Harness 的插件管理器中安装 `packages/dsh-acycle-0.7.0.tgz`。npm 部署可在对应项目中执行 `npm install /绝对路径/dsh-acycle-0.7.0.tgz`。
2. 运行下面的命令，打开生成的 `generated/harness-plugin.json`。

```sh
python3 local_test.py config
```

3. 将其中的 `python`、`workspace` 和 `guiSession` 填到现有 Acycle preset 的 `acycle-native` 插件配置中。使用 `0.2.2-rc.5` 宿主时，preset 应启用官方 native tool executor。模型和 API key 使用你本机 Harness 的设置。
4. 在聊天中输入“读取当前滤波窗口的频带与单位，然后把频率下限改为 0.04、上限改为 0.06 cycles/m”。也可以输入“打开 core.png，我来选择剖线”，点选后再要求助手读取完成事件。

GUI 连接在每次重新开启 MATLAB 主窗口后更新，届时重新运行 `config` 并更新 `guiSession`。这个包提供现有聊天宿主的插件和配置，工具执行器供本地命令验收使用。完整 DeepSeek Harness 聊天应用可使用你已有的安装。

**数据与范围**

`study/series.csv` 有 256 行，无表头。第一列为 0–255 米，第二列为周期 20 米的正弦与振幅 0.2、周期 5 米的余弦之和。`study/second.csv` 是周期 17 米的余弦，用于换数据试验。`study/core.png` 是合成灰度条带图，适合测试剖面选点。

本机协作演示覆盖带通滤波和图像剖面。去趋势、SWA 等功能可从 GUI 菜单试用，其实时 Harness 接口仍待扩展。事件由 `events` 命令或聊天工具查询。独立的菜单批处理插件接口使用完整迁移源码检出。[批处理配置说明](https://github.com/CinnabarCHU/Hypercinnabar/blob/acycle-harness-gui-poc/harness/README.zh-CN.md)

macOS、Windows 和 Linux 使用相同的 MATLAB 与 Python 入口。完整实窗验收已在 Ubuntu 24.04、MATLAB R2024b 完成，macOS / Windows 的实机运行仍需本地确认。

原 GUI、CLI 和 Core 的使用说明位于 `acycle/README.zh-CN.md`。发行包来源与构建信息见 `LOCAL_TEST_MANIFEST.json`，文件校验值见 `SHA256SUMS.txt`。

[已通过的 GUI 验收](https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45193226531) · [迁移源码](https://github.com/CinnabarCHU/Hypercinnabar/tree/acycle-harness-gui-poc)
