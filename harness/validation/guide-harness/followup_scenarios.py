"""Start fresh follow-up conversations on unmodified outputs of the first real sessions."""
import hashlib,json,shutil,sys
from pathlib import Path
from guide_transport import FILES
def create(root,repo):
    n=[('etp-wavelet','etp','processed_csv','ETP-processed.csv',
        '这是刚才指南 6.2 的真实输出：三列依次为 kyr BP、已去均值的 ETP、移除的趋势。本回合请用 Acycle GUIDE 旧版本菜单完成小波变换和绘图（使用前两列）；这是同一个案例的下一阶段。采用未修正的 Torrence–Compo Morlet，ω0=6、填充、尺度间隔 0.1，周期 10–700 kyr，不再标准化。请实际完成参数准备、计算、绘图，报告矩阵大小和图件。通过 Acycle 菜单接口，先查操作目录。矩阵须从附件导入；不要把长数组写进对话。'),
       ('wayao-next','wayao','filtered_csv','Wayao-filtered.csv',
        '这是刚才指南 6.3 瓦窑计算的带通结果：深度 m、0.022–0.034 cycles/m 的滤波值、包络。请用 GUIDE 旧版 Acycle 菜单依据滤波峰建立 405 kyr 年龄模型（选峰、非谷），绘制年龄模型，再把这些真实控制点用于原始伽马曲线，完成调谐和绘图。原始输入以原始字节另存于这个工作区的 Wayao-original.txt；原 GR 的单位和次序均不可改变。先查菜单，说明实际控制点数、年龄范围、是否覆盖或外推端部。如果接口不能传递返回值，请准确指出卡住的一步。这个回合不重做频谱，也不以其他 COCO 变体代替指南。')]
    items=[]
    for session,case,key,name,prompt in n:
        runs=root/case/'workspace/.acycle/runs'
        results=[json.loads(i.read_text()) for i in sorted(runs.glob('*/result.json'))]
        source=next(s for s in reversed(results) if s.get('status')=='completed' and key in s['artifacts'])
        f=Path(source['artifacts'][key]);h=hashlib.sha256(f.read_bytes()).hexdigest();assert h==source['artifact_sha256'][key]
        ws=root/session/'workspace';ws.mkdir(parents=True,exist_ok=True)
        if case=='wayao':
            original=repo/'upstream/acycle/data/Examples'/FILES[case][0];shutil.copyfile(original,ws/'Wayao-original.txt')
        items.append({'id':session,'derived_from':{'actual_run':source['run_id'],'artifact':key},'attachment':{'root':'scenario','path':str(f),'name':name,'sha256':h},
                      'turns':[{'id':'next','user_prompt':prompt,'execution_policy':{'kind':'scientific','min_completed_scientific_runs':3 if case=='etp' else 6,'max_scientific_calls':10,'max_tool_calls':38}}]})
    (root/'followup.json').write_text(json.dumps({'cases':items},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':create(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
