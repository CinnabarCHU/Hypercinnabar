"""Export only final user-visible answers from this public-fixture study, with workspace paths shortened."""
import json,re,sys
from pathlib import Path
root,out=map(Path,sys.argv[1:3]); sections=['# 模型最终答复（供抽查）','这里只保留官方 SDK 的最终可见回答，不含推理、工具原始消息或凭据。模型说法不构成验收结论；输出位置已替换为 study 占位路径。']
for case in ('insolation','etp','wayao','etp-wavelet','wayao-next'):
    record=json.loads((root/case/'primary.json').read_text())
    text=record['turns'][0].get('final_response') or '（该会话没有最终答复。）'
    assert not re.search(r'(?i)sk-[0-9a-z]{16,}|Bearer [\w.-]{16,}',text)
    text=text.replace(str(root),'STUDY').replace('/workspace/scratch/582c5a5c1c7f/acycle-harness-menu','REPO')
    sections.extend(['## '+case,'SDK: `'+record['status']+'`',text])
out.write_text('\n\n'.join(sections)+'\n')
