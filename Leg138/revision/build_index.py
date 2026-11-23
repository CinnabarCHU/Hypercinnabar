"""Build a Chinese file:// index for the Leg 138 collation and figure revisions."""
import csv
import gzip
import json
import re
from collections import Counter, defaultdict
from html import escape
from pathlib import Path
from urllib.parse import urldefrag

HERE = Path(__file__).resolve().parent
LEG = HERE.parent
FAMILIES = {
    "figures_carbon": "沉积物碳",
    "figures_composite": "复合地层柱",
    "figures_depth": "线性沉积速率",
    "figures_ir": "孔隙水化学",
    "figures_sr": "岸上研究",
}
SR_NAMES = {
    (15,1):"底栖有孔虫 δ¹⁸O 与修订复合深度",(15,2):"底栖有孔虫 δ¹³C 与修订复合深度",
    (15,5):"底栖有孔虫 δ¹⁸O 与年龄",(15,6):"底栖有孔虫 δ¹³C 与年龄",
    (35,2):"三家实验室的蛋白石质量分数",(35,5):"钙质超微化石丰度",(35,6):"钙质超微化石保存状况",
    (35,7):"钙质超微化石蚀刻程度",(35,8):"钙质超微化石次生加大",(35,9):"碳酸钙质量分数",
    (35,10):"蛋白石质量分数",(35,11):"估计陆源组分质量分数",(35,12):"碳酸钙质量累积率",
    (35,13):"蛋白石质量累积率",(35,14):"陆源组分质量累积率",(35,15):"碳酸盐骤降的四站对比",
    (35,26):"蛋白石累积率与百万年分箱",(35,27):"两站沉积速率、组分、密度与累积率",
}
FIELD_NAMES = dict(sodium="钠",chloride="氯",alkalinity="碱度",sulfate="硫酸根",magnesium="镁",
                   calcium="钙",potassium="钾",silica="溶解硅",lithium="锂",strontium="锶",
                   ammonium="铵",phosphate="磷酸根")


def read_csv(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))


def json_file(path):
    return json.loads(path.read_text())


def anchor(href, label, attrs=""):
    return f'<a href="{escape(str(href), quote=True)}"{attrs}>{escape(str(label))}</a>'


def local(leg_path, label):
    return anchor("../"+str(leg_path),label)


def physical(url, number, text=None):
    return anchor(f"{urldefrag(url).url}#page={number}",text or f"PDF {number}")


def join_ranges(numbers):
    if not numbers:
        return []
    runs=[]
    for n in sorted(set(map(int,numbers))):
        if not runs or n!=runs[-1][-1]+1:runs.append([])
        runs[-1].append(n)
    return runs


def range_text(nums):
    return "、".join(str(a[0]) if len(a)==1 else f"{a[0]}–{a[-1]}" for a in join_ranges(nums))


def witnesses(doc,page_numbers):
    return "、".join(physical(doc["url"],r[0],range_text(r)) for r in join_ranges(page_numbers))


def proof(documents):
    entries=defaultdict(lambda: {"pages":[], "lines":0, "kind":Counter(), "holes":[], "hp":set(), "hl":0})
    sp = json_file(HERE/"text_sp/verification.json")
    for doc,r in sp.items():
        entries[doc].update(pages=r["source_pages"], lines=r["printed_lines"])
    for folder in ("text_ir","text_sr"):
        reports={r["doc_id"]+"."+str(r["source_page"]):r for r in read_csv(HERE/folder/"pages.csv")}
        with (HERE/folder/"pages.jsonl").open() as handle:
            for line in handle:
                r=json.loads(line)
                doc,p=r["doc_id"],r["source_page"]
                e=entries[doc];e["pages"].append(p)
                e["lines"]+=int(reports[doc+"."+str(p)]["source_lines"])
                e["kind"][r.get("coverage_kind") or ("overlay" if r.get("overlay_only") else "article")]+=1
    for r in read_csv(HERE/"hole_headers/readings.csv"):
        e=entries[r["doc_id"]];e["holes"].append(r["hole"]);e["hp"].add(int(r["source_page"]));e["hl"]+=1
    order={"SP":0,"PR":1,"IR":2,"SR":3}
    rows=[]
    for key,e in sorted(entries.items(),key=lambda kv:(order[documents[kv[0]]["series"]],kv[0])):
        doc=documents[key];family=doc["series"];parts=[]
        if e["pages"]:
            link=witnesses(doc,e["pages"])
            parts.append(f'PDF {link}，共 {len(e["pages"])} 页，{e["lines"]:,} 个定位行段。')
            if family=="IR" and "all_printed_text" in e["kind"]:
                n=e["kind"]["all_printed_text"]; m=e["kind"]["all_narrative_and_captions"]
                parts.append(f"其中 {n} 页覆盖全部印字，{m} 页覆盖叙述、图注等；图表内部的校读范围逐页记录。")
            if family=="SR" and e["kind"]["overlay"]:
                parts.append(f'其中 {e["kind"]["overlay"]} 页以校读片段叠加在原有阅读层，表体或图内文字的取舍见逐页范围。')
            elif key=="SR.C30":
                parts.append("正文、图注、参考文献、运行页眉和脚注均有底本定位，图内标签另有登记。")
        if e["holes"]:
            parts.append(f'孔位栏另录 {len(set(e["holes"]))} 个孔、{e["hl"]} 个字段行，见 PDF {witnesses(doc,e["hp"])}。')
        links=[local("publication/chapters/"+key+".pdf","原公开阅读版" if family in ("SP","PR") else "章节 PDF")]
        if family in ("SP","PR"):links.append(anchor("text_sp/README.md","本地制作说明"))
        if e["pages"] and family=="IR":links.append(anchor("text_ir/pages.csv","逐页范围"))
        if e["pages"] and family=="SR":links.append(anchor("text_sr/pages.csv","逐页范围"))
        if e["holes"]:links.append(anchor("hole_headers/readings.csv","孔位校记"))
        title="Site "+doc["site"] if family=="IR" and doc["site"] else doc["title"]
        rows.append(f'<tr><th scope="row"><code>{escape(key)}</code><span>{escape(title)}</span></th><td>{" ".join(parts)}</td><td class="links">{" ".join(links)}</td></tr>')
    unique={(key,p) for key,e in entries.items() for p in set(e["pages"])|set(e["hp"])}
    return entries,len(unique),"".join(rows)


def figure_site(ch,n):
    if ch==15:return [846]
    if ch==35:
        if n==2:return [847]
        if n==15:return [844,845,846,849]
        if n in [26,27]:return [846,850]
        if 5<=n<=14:return list(range(844,855))
    return []


def label_for(row,canon,folder):
    if folder=="figures_sr":
        ch,n=map(int,re.search(r"C(\d+)\.FIGURE(\d+)",row["item_id"]).groups())
        return SR_NAMES.get((ch,n),canon["title_or_caption"]),figure_site(ch,n)
    site=int(canon["site"])
    if folder=="figures_depth":
        title="线性沉积速率与年龄" if "vs. age" in canon["title_or_caption"].lower() else "线性沉积速率与深度"
    elif folder=="figures_carbon":
        title="碳酸钙含量剖面" if site==854 else "碳酸钙及有机碳含量剖面"
    elif folder=="figures_ir":
        title="孔隙水 · "+"、".join(FIELD_NAMES.get(field,field) for field in row["fields"].split("|"))
    else:
        title="复合地层柱 · GRAPE 密度与磁化率"
    return title,[site]


def numerical_links(r, family, sources):
    links=[]
    if family=="figures_sr":
        links+=[anchor(sources[path],ident) for path,ident in zip(r["inputs"].split("|"),r["table_ids"].split("|"),strict=True)]
        links.append(local("sr/core/records.jsonl.gz","离线数值库"))
    elif family=="figures_depth":
        links=[anchor(r["native_url"],r["table_ids"]),anchor("figures_depth/intervals.csv","离线区间值")]
    elif family in ("figures_ir","figures_carbon"):
        raw=[p for p in r["inputs"].split("|") if p.startswith("ir/primary/")]
        for p in raw:links.append(anchor(sources[p],r["table_ids"]))
        if family=="figures_carbon":
            links.append(local("data/carbon_reported.csv","离线碳数据"))
        else:
            cd=[p for p in r["inputs"].split("|") if p.startswith("disc/primary/")]
            links.extend(anchor(sources[p],"CHEM 数码表") for p in cd)
            links.append(local("disc/core/edition2/water.csv.gz","离线孔隙水表"))
        if not raw:
            # A print-only IR table has an authoritative witness page in the catalogue.
            matches=[p for p in (LEG/"ir/core/edition2_print").rglob("*.csv") if p.stem==r["table_ids"].replace(".","_")]
            if matches:links.append(local(matches[0].relative_to(LEG),r["table_ids"]))
    else:
        for p in r["inputs"].split("|"):
            if p in sources:links.append(anchor(sources[p],Path(p).name))
        links.append(anchor("figures_composite/source_tracks.csv","输入索引"))
    assert links,r["item_id"]
    return " ".join(links)


def figure_groups(figures, sources, docs):
    groups=defaultdict(list);total=Counter()
    for family in FAMILIES:
        for r in read_csv(HERE/family/"manifest.csv"):
            ident=r["item_id"];canon=figures[ident];doc=docs[canon["doc_id"]]
            name,sites=label_for(r,canon,family)
            series=canon["series"]
            number=int(re.search(r'(?:FIGURE|F)(\d+)$',ident).group(1))
            site_str="、".join(map(str,sites)) if len(sites)<11 else "844–854 全站"
            group=(0,int(doc["site"])) if series=="IR" else (1,int(doc["chapter"]))
            pnums=[int(p) for p in (r.get("source_pages") or r["source_page"]).split("|")]
            links=" · ".join(physical(doc["url"],p) for p in pnums)
            if canon["printed_pages"]:links+=f'<small>印刷页 {escape(canon["printed_pages"].replace("|","、"))}</small>'
            qualification=r["qualification"]
            state="仅两条定量轨道" if family=="figures_composite" else "滤波线独立复算" if "independent_filter" in r["redraw_extent"] else ""
            if state:name+=f'（{state}）'
            line=f'''<tr class="figrow" id="{escape(ident)}" data-series="{series}" data-sites="{" ".join(map(str,sites))}" data-family="{family}"><th scope="row"><code>{escape(ident)}</code><span>{escape(name)}</span><small>Site {escape(site_str)}</small></th>
<td class="links">{numerical_links(r,family,sources)}</td><td class="links">{local(r["output"],"矢量 PDF")} {local(r["renderer"],"绘图代码")}</td><td class="links">{links}</td>
<td><details><summary>校记</summary><p lang="en">{escape(qualification)}</p></details></td></tr>'''
            groups[group].append((number,line));total[family]+=1
    parts=[]
    for group,rows in sorted(groups.items()):
        name=f"IR · Site {group[1]}" if group[0]==0 else f"SR · 第 {group[1]} 章"
        parts.append(f'<section class="figgroup"><h3>{name}</h3><div class="scroll"><table><thead><tr><th>图件</th><th>输入数值</th><th>重绘</th><th>底本页</th><th>差异</th></tr></thead><tbody>')
        parts.extend(html for n,html in sorted(rows));parts.append('</tbody></table></div></section>')
    return total,"".join(parts)


CSS = """
:root{color-scheme:light;--paper:#f8f7f2;--ink:#172e2d;--link:#075f68;--rule:#cbd6cf}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 system-ui,"Noto Sans CJK SC","PingFang SC",sans-serif}
main{max-width:1160px;margin:auto;padding:28px clamp(16px,4vw,56px) 80px}nav{display:flex;flex-wrap:wrap;gap:18px;font-size:.88rem;margin-bottom:28px}
a{color:var(--link);text-decoration:underline;text-underline-offset:3px}a:hover{color:#9c471f}
h1,h2,h3{font-family:Georgia,"Noto Serif CJK SC","Songti SC",serif;line-height:1.28}
h1{font-size:clamp(1.85rem,5vw,3.1rem);margin:0 0 .28em}h2{font-size:1.7rem;margin:2em 0 .6em;border-top:2px solid var(--ink);padding-top:.6em}
h3{font-size:1.18rem;margin:1.5em 0 .45em}header p,.note{max-width:86ch}p{margin:.5em 0 .9em}
.stats{display:flex;gap:25px;flex-wrap:wrap;margin:18px 0;color:#284c4c;font-weight:600}.stats b{font-size:1.36rem}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(217px,1fr));gap:12px}
.card{display:block;background:#edf1e9;border-left:3px solid #65938b;padding:13px 15px;text-decoration:none}
.card strong,.card span{display:block}.card span{font-size:.87rem;color:#385651;padding-top:4px}
.toolset{display:flex;align-items:end;gap:12px;flex-wrap:wrap;margin:10px 0 18px;padding:13px 16px;background:#edf1e9}
label{display:grid;gap:3px;font-size:.82rem}select,input,button{font:inherit;background:white;color:var(--ink);border:1px solid #9faea7;border-radius:3px;padding:5px 9px;min-height:33px}
button{cursor:pointer}output{font-size:.88rem}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:.875rem;background:#fffefa}
td,th{border-bottom:1px solid var(--rule);padding:9px 11px;text-align:left;vertical-align:top}
thead th{background:#e9ede6;color:#355453;font-weight:600;white-space:nowrap}tbody th{font-weight:500;min-width:120px}
tbody th span,small{display:block}small{font-size:.78rem;color:#536763}code{font:.78rem ui-monospace,monospace;color:#4c6562}
.links{min-width:90px}.links a{display:inline-block;margin-right:.6em;white-space:nowrap}summary{cursor:pointer;color:#2f5d5e}details p{max-width:38ch;min-width:14ch}
.figgroup [scope=row]{width:31%}.examples li{margin:.5em 0}.note{font-size:.92rem;color:#405d59} [hidden]{display:none!important}
@media print{body{background:#fff}main{max-width:none;padding:0}.toolset,nav{display:none}.scroll{overflow:visible}.figgroup{break-inside:auto}tr{break-inside:avoid}}
"""
JS = """
const controls=[...document.querySelectorAll('.toolset select,.toolset input')];
const rows=[...document.querySelectorAll('.figrow')];
function filter(){
 const series=document.querySelector('#series').value,site=document.querySelector('#site').value,
 family=document.querySelector('#family').value,q=document.querySelector('#q').value.trim().toLowerCase();
 let count=0; for(const row of rows){
  row.hidden=!!((series&&row.dataset.series!==series)||(site&&!row.dataset.sites.split(' ').includes(site))||
    (family&&row.dataset.family!==family)||(q&&!row.textContent.toLowerCase().includes(q)));
  if(!row.hidden)count++;
 }
 document.querySelectorAll('.figgroup').forEach(g=>g.hidden=!g.querySelector('tr.figrow:not([hidden])'));
 document.querySelector('output').textContent='显示 '+count+' / '+rows.length+' 张';
}
controls.forEach(el=>el.addEventListener('input',filter));
document.querySelector('button').addEventListener('click',()=>{controls.forEach(el=>el.value='');filter();});
filter();
"""


def card(href,title,subtitle):
    return f'<a class="card" href="{escape(href)}"><strong>{escape(title)}</strong><span>{escape(subtitle)}</span></a>'


def main():
    docs={r["doc_id"]:r for r in read_csv(LEG/"data/documents.csv")}
    canon={r["item_id"]:r for r in read_csv(LEG/"data/figure_reproduction.csv")}
    sources={r["local_path"]:r["url"] for r in read_csv(LEG/"data/source_inventory.csv.gz")}
    entries,pages,prows=proof(docs)
    total,frows=figure_groups(canon,sources,docs);nf=sum(total.values())
    holes=read_csv(HERE/"hole_headers/readings.csv")
    gathered=sum(len(e["pages"]) for e in entries.values())
    fig_n=sum(r["object_scope"]=="numbered_figure" for r in canon.values())
    cards="".join([card("figures_carbon/IR_Chemistry_Comparison_Atlas.pdf","孔隙水与沉积物碳","按站逐幅对照印刷剖面、重绘标记和测量字段。"),
        card("figures_depth/Sedimentation_Rate_Comparison.pdf","线性沉积速率","11 站成对展示年龄轴与深度轴，保留发表速率。"),
        card("figures_sr/comparison.pdf","科学成果图件","Site 846 稳定同位素与跨站沉积史，底本和数值重绘并列。"),
        card("figures_composite/IR11_F07_Comparison.pdf","Site 846 复合地层柱","查看三页续图中 GRAPE 和磁化率两条轨道的差异。")])
    opts="".join(f'<option value="{i}">{i}</option>' for i in range(844,855))
    fam_opts="".join(f'<option value="{k}">{v}（{total[k]}）</option>' for k,v in FAMILIES.items())
    document=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Leg 138 · 文字校读与数值重绘</title><style>{CSS}</style></head><body><main>
<nav aria-label="索引"><a href="../browse.html">航次总览</a><a href="#proof">文字校读</a><a href="#figures">图件检索</a><a href="#examples">校记实例</a></nav>
<header><h1>Leg 138 · 文字校读与数值重绘</h1><p>从校读文本返回原扫描页，或从一条曲线找到作者发表的数值。页码链接指向出版者的 PDF，下载分支后可离线打开本地阅读版、图件和数据。</p>
<div class="stats"><span><b>{nf}</b> 张本次重绘</span><span><b>{gathered}</b> 页纳入正文或局部校读</span><span><b>{len(set(r["hole"] for r in holes))}</b> 个钻孔的孔位栏</span></div></header>
<section><h2>底本与重绘对照</h2><div class="cards">{cards}</div></section>
<section id="proof"><h2>文字校读范围</h2><p>本批逐页记录涵盖 {gathered} 个物理页。另校读 {len(holes)} 个孔位字段行；合计涉及 {pages} 个不同物理页。下表的子项范围可重叠，行段数用于定位。现有校读由 AI 编辑对照底本完成，独立人工复核尚待进行。</p>
<div class="scroll"><table><thead><tr><th>出版物与章节</th><th>覆盖范围及底本 PDF 页码</th><th>阅读与校记</th></tr></thead><tbody>{prows}</tbody></table></div>
<p class="note">SP 和 PR 新校读层由原分发件在本地生成。表中链接提供构建说明及既有公开阅读版。全航次另有 <a href="triage/summary.json">OCR 差异抽样</a>，抽样记录单独计数。</p></section>
<section id="figures"><h2>数值重绘检索</h2><p>航次图件登记共有 {fig_n:,} 张编号图，下表列出本次新增的 {nf} 张。检索跨站图时，选择任一实际入图的站点即可。表内“输入数值”链接保留原作者表号；“离线”数据来自分支内的结构化副本。</p>
<div class="toolset"><label>系列<select id="series"><option value="">全部</option><option>IR</option><option>SR</option></select></label>
<label>站点<select id="site"><option value="">全部站点</option>{opts}</select></label>
<label>图类<select id="family"><option value="">全部图类</option>{fam_opts}</select></label><label>检索图号或字段<input id="q" type="search" placeholder="例如 SR.C15 或 磁化率"></label>
<button type="button">重置</button><output aria-live="polite">显示 {nf} / {nf} 张</output></div>{frows}</section>
<section id="examples"><h2>校记实例</h2><ul class="examples"><li><a href="#SR.C15.FIGURE2">Site 846 碳同位素</a>。第 15 章正文称作 raw，印刷点位支持 Table 3 的物种调整值。<a href="figures_sr/README.md">字段对照</a> · <a href="figures_sr/kernel_calibration.json">高斯滤波校准</a></li>
<li><a href="#IR16.F33">Site 851 有机碳</a>。光盘表含 67 个有机碳值，原图可辨认的 31 个点有逐样品比对。<a href="figures_carbon/figure33_organic_subset851.csv">样品对照</a></li>
<li>Site 845 速率表的电子版交换了年龄与速率列名；166.83 mcd 的年龄在印本为 10.59 Ma，电子版为 10.51 Ma。<a href="figures_depth/observations.csv">数值差异</a></li>
<li>Site 846 站章的时代界线按孔号、mbsf、mcd 和原文指定生物事件分别整理。<a href="text_ir/epoch_boundaries.csv">界线表</a> · {physical(docs["IR.C11"]["url"],21,"底本 PDF 第 21 页")}</li></ul></section>
</main><script>{JS}</script></body></html>'''
    (HERE/"index.html").write_text(document,encoding="utf-8")
    print(f"{nf} unique figure entries; {len(entries)} publications/chapters; {pages} distinct physical pages")
    assert len(re.findall(r'class="figrow" id="[^"]+"',document))==nf
    for target in re.findall(r'href="([^"]+)"',document):
        target=urldefrag(target).url
        if not target or target.startswith("https://") or target.startswith("http://"):continue
        assert (HERE/target).exists(),target


if __name__=="__main__":
    main()
