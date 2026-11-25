**Acycle Harness 0.7.1 便携试用版 — Apple Silicon**

目标：macOS Ventura 13.5 或更新版本，M1/M2/M3 等 Apple Silicon，已安装并可启动的 MATLAB R2024a。包中包含完整 DeepSeek Harness Web 聊天程序、自有 Electron 窗口、Node、Python、Acycle 插件与 0.7.0 GUI 示例。MATLAB、许可证和 MATLAB 所需 Java 使用已有安装。

MATLAB 示例验收使用 Signal Processing Toolbox、Statistics and Machine Learning Toolbox 和 Image Processing Toolbox。请确认已有 MATLAB 安装包含这些工具箱；本包不替你安装或授权 MATLAB 产品。

1. 解压整个 ZIP，把整个 `Acycle_Harness_Portable_0.7.1_arm64` 文件夹放到桌面或其他可写目录。保持 `.app`、`Workspace`、`portable.json` 在一起。
2. 双击 `Acycle Harness.app`。首次找不到 MATLAB 时选择 `/Applications/MATLAB_R2024a.app`。程序会启动专用于此次试用的 MATLAB 进程，打开 Acycle 和滤波预览，再打开 Harness 聊天界面。
3. 首次看到 Harness 的 Preview Notice 时点击 Continue，然后在模型设置或首次凭据提示中填入自己的 DeepSeek API key，选择 DeepSeek 官方模型。包中没有 API key；启动和检查窗口无需调用模型，聊天按自己的 API 账户计费。保存的凭据在本包的 `State/harness` 中。
4. 新建 Acycle MATLAB 会话，输入：**读取当前滤波窗口的频带与单位，然后将频率下限改为 0.04、上限改为 0.06 cycles/m。** 应先看到窗口检查，再看到同一 MATLAB 图窗更新。
5. 输入：**打开 core.png，我来选择剖线。** 在 MATLAB 图像窗口点选后点击 **Finish profile**，回到聊天输入 **我画好了，请读取完成事件**。这一版由下一条消息查询事件。

试用菜单提供重新连接、打开工作区和打开日志。分析数据保存在 `Workspace/study`，Core 日志在 `Workspace/generated/journals`，Harness 和桌面缓存集中在 `State`。请先复制需要保留的结果，再退出应用并删除整个文件夹；只删除 `.app` 会留下同级工作区和会话。

应用退出会请求关闭本次启动的专用 MATLAB 进程；不会结束你事先打开的其他 MATLAB。若 MATLAB 正在执行很长的计算，它可能延后处理退出请求，请等本次 MATLAB 窗口关闭再删除目录。操作系统自身的最近使用记录、诊断，以及 MATLAB 的许可服务记录不属于本应用控制的文件，因此不能承诺系统层面完全零痕迹。

本版不注册命令、不修改 shell 配置、不安装 Homebrew/Conda、不执行 MATLAB savepath，也不设置登录启动。所有脚本依赖已随包提供，首次启动无需 npm/pip 下载。模型对话需要联网。固定 Harness 0.2.2-rc.5，便携壳不会自动升级运行时。

该试验包使用本地 ad-hoc 签名，未做 Apple Developer ID 公证。首次如被 macOS 阻止，在系统设置“隐私与安全性”中对该应用选择“仍要打开”，或用 Finder 的“打开”操作确认。无需关闭系统的全局安全设置。若 macOS 隔离了应用导致无法找到同级工作区，请按弹窗选择解压后的完整文件夹。

当前实时工具覆盖滤波与图像剖面；其他功能可从 Acycle GUI 菜单使用。其完整实时接口仍在迁移中。GUI 原始验收是 Linux/R2024b；本包的新增构建与检查以随附 `VALIDATION.md` 为准，不能把其他系统的检查等同于 Ventura 实机验收。

运行包和原始源代码：
https://github.com/CinnabarCHU/Hypercinnabar/tree/acycle-portable-macos-0.7.1

DeepSeek Harness 为 DeepSeek AI 的开源项目。本便携封装属于 Acycle 试验交付，包含的许可证保留在各包内。
