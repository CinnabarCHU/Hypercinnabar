"""Retain sanitized test evidence, remove all per-machine test state, then ship."""
import json
import os
from pathlib import Path
import shutil
import sys

root=Path(sys.argv[1]).resolve()
evidence=root/'Validation'
evidence.mkdir()
smoke=json.loads((root/'State/logs/app-smoke.json').read_text())
gui=json.loads((root/'Workspace/generated/local-tests-done.json').read_text())
assert smoke['status']=='passed' and gui['status']=='passed'
for source in [root/'State/logs/app-smoke.json',root/'State/logs/harness-window.png',
               root/'Workspace/generated/local-tests-done.json',
               root/'Acycle Harness.app/Contents/Resources/native-build/macos-minimums.json',
               root/'Acycle Harness.app/Contents/Resources/native-build/provenance.json']:
    shutil.copy2(source,evidence/source.name)
(root/'VALIDATION.md').write_text('''**0.7.1 验收范围**

- 在 GitHub macOS 15 Apple Silicon runner 上构建，包含 arm64 Electron、Node 与 Python。
- 实际启动打包后的 `.app`，加载官方 DeepSeek Harness 0.2.2-rc.5 聊天界面；截图和回执在 `Validation`。
- 内部 Node 加载器固定到上游允许的 0.1.9，从公开的对应源码重新编译为 macOS 13.5；包内全部 arm64 Mach-O 文件通过最低系统版本检查。未启用的实验性离线语音与通用电脑操作组件不随包分发；Acycle 使用自己的 MATLAB GUI 协议。
- MATLAB R2024a 实窗运行：使用包内 Python/Node 调用官方工具执行器，检查 24 个 Acycle 工具，执行窗口读取、同窗频带修改、图像剖面打开与事件查询。
- MATLAB 检查修改后的数值结果与 replay 一致，并与原始 gaussfilter 结果一致；关闭 GUI 后会话目录消失。
- 没有在本轮调用付费模型 API。聊天选用工具的先前 PoC 验收不替代本机 API 配置检查。
- Ventura 13.5+ 是目标系统；此处没有 Ventura 实机，最终仍需在用户电脑验收。

构建运行：'''+f'https://github.com/{os.environ.get("GITHUB_REPOSITORY","CinnabarCHU/Hypercinnabar")}/actions/runs/{os.environ.get("GITHUB_RUN_ID","")}\n',encoding='utf-8')
shutil.rmtree(root/'State')
shutil.rmtree(root/'Workspace/generated')
for pycache in root.rglob('__pycache__'):
    # Python-generated caches outside the signed app only. Signed resources stay byte-exact.
    if 'Acycle Harness.app' not in pycache.parts:
        shutil.rmtree(pycache)
print('Clean portable payload ready:',root)
