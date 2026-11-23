"""Construct public Harness conversations; graders and expected results are not model inputs."""
import json
from pathlib import Path

CASES = {
'insolation': ('Example-Insol-t-0-2000ka-day-80-lat-65-meandaily-La04.txt',
'附件是指南 6.1 的日照量示例，第一列是 kyr BP，第二列是日照量。请通过 Acycle Harness 实际分析并报告主要谱峰、单位、实际演化谱步长和可查看的产物。排序、去均值，1 kyr 等间隔，2π MTM (NW=2)，这次取 5 倍零填充 NFFT=10005，与指南结果图对照；演化谱采用 LAH FFT、400 kyr 窗口、请求步长 3.2 kyr、图上频率上限 0.06 cycles/kyr。可用高层一次完成；如果其选项和指南有差别，请明确指出。'),
'etp': ('Example-La2004-1E.5T-1P-0-2000.txt',
'附件是指南 6.2 自带的 La2004 ETP 示例，第一列 kyr BP，第二列为 ETP。请先通过 Acycle Harness 完成去均值、2π MTM (NW=2)、5 倍零填充 NFFT=10005、LAH 演化谱；采样为 1 kyr，窗 400 kyr，请求步长 3.2 kyr，图上频率上限 0.1 cycles/kyr。可用高层一次完成。报告实际算出的周期和实际步长、运行编号。这个回合先做这些，小波另做。'),
'wayao': ('Example-WayaoCarnianGR0.txt',
'附件是指南 6.3 瓦窑剖面自然伽马，第一列深度 m，第二列 GR。请通过 Acycle Harness 实际完成预处理、谱分析、演化谱和滤波并交付产物：排序去重、线性插值 0.33 m、80 m LOWESS 去趋势（均匀网格跨度 175.89 m，比例取 80/175.89），2π MTM (NW=2)，5 倍零填充 NFFT=2670，拟合稳健 AR1、对数功率、20% 中值平滑；谱分析图频率上限 1 cycle/m。LAH 演化谱窗口 40 m、步长 0.33 m；高斯带通 0.022–0.034 cycles/m。可用高层一次完成。请说明实际主要周期、运行号、哪些设置不能独立控制。这个回合先不做 COCO 和调谐。'),
}
def write(repo,dest):
    files=json.loads((repo/'tests/user_guide/manifest.json').read_text())['files']
    root=repo/'upstream/acycle/data/Examples'
    items=[]
    for name,(file,prompt) in CASES.items():
        items.append({'id':name,'attachment':{'root':'scenario','path':str((root/file).resolve()),
                     'name':file,'sha256':files['data/Examples/'+file]['sha256']},
                     'turns':[{'id':'spectra','user_prompt':prompt,
                     'execution_policy':{'kind':'scientific','min_completed_scientific_runs':1,'max_scientific_calls':8,'max_tool_calls':26}}]})
    dest.write_text(json.dumps({'cases':items},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':
    import sys
    write(Path(sys.argv[1]).resolve(),Path(sys.argv[2]))
