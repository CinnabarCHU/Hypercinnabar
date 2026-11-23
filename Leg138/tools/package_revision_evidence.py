"""Copy available editorial recipes and locally generated ledgers into a paired edition.

Run after building the books and before regenerating SHA256SUMS. The full
research archive carries private SP/PR transcriptions and OCR comparisons when
generated locally. A public checkout may only contain the recipes and indexes.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

def collect(root,output):
    target=output/'revision_evidence'
    target.mkdir(parents=True,exist_ok=True)
    records=[]
    for source in sorted((root/'revision').rglob('*')):
        rel=source.relative_to(root/'revision')
        if not source.is_file() or '__pycache__' in rel.parts or rel.name in ('index.html','build_index.py','verify_release.py','README.md') and len(rel.parts)==1:
            continue
        dest=target/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest)
        with dest.open('rb') as stream:
            records.append(dict(path=rel.as_posix(),bytes=dest.stat().st_size,sha256=hashlib.file_digest(stream,'sha256').hexdigest()))
    catalog=target/'catalog'
    catalog.mkdir(exist_ok=True)
    for name in ('figure_reproduction.csv','figure_reproduction_checks.json','paired_pdf_reproduction.json'):
        source=root/'data'/name
        if source.is_file():
            dest=catalog/name
            shutil.copyfile(source,dest)
            with dest.open('rb') as stream:
                records.append(dict(path='catalog/'+name,bytes=dest.stat().st_size,
                                    sha256=hashlib.file_digest(stream,'sha256').hexdigest()))
    (target/'inventory.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    (target/'README.md').write_text(
        '# Editorial evidence\n\nThe directories contain page-addressed transcriptions, variants, plot recipes and local audit ledgers. '
        'Use the chapter links in ../index.html to read the actual typeset books and the original witness leaves. '
        'Open IR_Chemistry_Comparison_Atlas.pdf, Sedimentation_Rate_Comparison.pdf, IR11_F07_Comparison.pdf and comparison.pdf in the figure folders for side-by-side checks. '
        'For rebuilding the figures, copy the desired research folder back under Leg138/revision in the project and fetch the source files named in its manifest. '
        'Original reports retain their publication notices.\n\n'
        '全航次 1,206 个编号图的原页、数据来源和重绘范围见 [逐图登记](catalog/figure_reproduction.csv)。'
        '本版正文与具名图页的交叉核验见 [版本核验](verification.json)。'
        '所有逐行 OCR 分歧可从 [按章索引](triage/corpus_index.csv) 定位。\n',encoding='utf8')
    atlas_links=[
        ('figures_carbon/IR_Chemistry_Comparison_Atlas.pdf','44 幅孔隙水与沉积物碳含量图'),
        ('figures_depth/Sedimentation_Rate_Comparison.pdf','22 幅沉积速率图'),
        ('figures_composite/IR11_F07_Comparison.pdf','Site 846 综合地层图'),
        ('figures_sr/comparison.pdf','18 幅岸上研究图')]
    links=[f'<a href="revision_evidence/{file}">{title}</a>' for file,title in atlas_links if (target/file).exists()]
    if links:
        idx=output/'index.html'
        text=idx.read_text(encoding='utf8')
        marker='<nav id="revision-evidence">'
        if marker not in text:
            insert=marker+' · '.join(links+['<a href="revision_evidence/catalog/figure_reproduction.csv">全航次逐图清单</a>', '<a href="revision_evidence/inventory.json">本轮校读材料</a>'])+'</nav>'
            idx.write_text(text.replace('</header>',insert+'</header>',1),encoding='utf8')
    return len(records)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();print(collect(a.root,a.output),'editorial files')
