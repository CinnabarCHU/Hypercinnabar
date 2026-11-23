# 在 DeepSeek Harness 中协作操作 Acycle 桌面

本测试版组合了 Acycle 代码式 GUI、`acycle-deepseek` Python wheel 和 `dsh-acycle` 插件 0.7.0。当前可编辑窗口是旧版带通预览。图像剖面另有一扇供用户非阻塞点选的窗口。批处理入口依然可以独立运行。

## 安装与连接

1. 解压 GUI，在 MATLAB 中切到含 `ac.m` 的目录，运行 `ac`。选择 **Help → Connect to Acycle Harness…**，复制对话框给出的本机会话目录。也可以在同一 MATLAB 命令窗口执行 `acgui.share()` 得到相同路径。
2. 在 Harness 使用的 Python 环境安装包内的 wheel，例如 `python -m pip install acycle_deepseek-0.7.0-py3-none-any.whl`。桌面通过限于本机的临时目录接收四类 JSON 请求，用户继续在原来的 MATLAB 窗口工作。
3. 在已有 DeepSeek Harness 的 npm 项目中执行 `npm install /absolute/path/dsh-acycle-0.7.0.tgz`，在已有 Acycle 插件配置中设定下面三项。保留已有批处理配置。0.2.2-rc.5 preset 需要官方 native tool executor。桌面与插件的 Python 连接器运行在同一台机器上。

```json
{
  "id": "acycle-native",
  "name": "dsh-acycle",
  "config": {
    "python": "/absolute/path/to/python",
    "workspace": "/absolute/path/to/study",
    "guiSession": "/absolute/path/copied/from/Acycle"
  }
}
```

用户自己在 Acycle 打开滤波窗后，可以在聊天中问“这条曲线当前的频带和单位是什么？”或者“将带通频率改为每单位 0.04 到 0.06，再把图的横轴上限改为 0.17”。文件打开操作接受 Harness 工作区内的数值序列，或 Core 用 `accore.io('save',file,s)` 保存的 `Bandpass_legacy` MAT 交换文件。MAT 恢复使用已保存的数值结果与实际参数。换入不同输入时，现有滤波单例要求提交其窗口 ID 和最近修订号。

## 桌面工具

| 工具 | 输入 | 返回 |
| --- | --- | --- |
| `acycle_gui_inspect` | 可选 `window_id` | 当前协作窗口，或指定窗的序列、单位、参数、面板、可编辑字段、修订号与 Core 记录 ID |
| `acycle_gui_open` | `feature` 取 `filter` 或 `image_profile`，另给 `input_path` | 用户可见窗口的状态。灰度和 RGB 栅格图像可用于点选剖线 |
| `acycle_gui_update` | `window_id`、`expected_revision`，以及部分 `params` 或 `plt` | 带通支持 `flow/fhigh` 与两个面板共有的 `x_1/x_2/y_1/y_2`。频带编辑更新保存按钮使用的数据。仅改显示范围复用同一个 Analyzer |
| `acycle_gui_events` | 可选 `after` 与 `window_id` | 自游标以来的提交、关闭、剖线完成或取消事件。最近 256 个事件保存在该 MATLAB 会话中，过期游标返回 `resync` |

共享会话的生命周期由用户控制。关闭 Acycle 主窗口会撤销共享，重开后复制新的会话目录。窗口 ID 只在当前 MATLAB 会话中有意义。Core 分析 ID 用来重放数值工作，批处理的 Harness `run_id` 用来查其独立运行记录。参数冲突返回 `conflict` 和最新状态。窗口关闭返回 `closed`。读取事件是一次立即返回的查询，用户可以在完成点选后让助手继续。

## 图像剖面

告诉 Harness “打开 core.png，我来标剖线”。在图像窗口中按顺序点选顶点，使用 **Undo point** 撤销最后一个点，再点击 **Finish profile**。回到聊天要求读取结果。完成事件包含源图像、有序像素坐标、样本数及 Analyzer id。未完成时直接关闭窗口会产生取消事件。
