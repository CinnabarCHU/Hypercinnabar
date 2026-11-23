"""Produce the human-readable, site-ordered PR scientific section with traceable operational tables."""
from pathlib import Path
from decimal import Decimal
import argparse,csv,gzip,json,html,collections,math,base64
def e(v):return html.escape(str(v or ''))
def read(p):return list(csv.DictReader(p.open()))
def tab(headers,rows):
    return '<table><thead><tr>'+''.join('<th>'+e(v)+'</th>' for v in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(v)+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table>'
def link(url,label):return '<a href="'+e(url)+'">'+e(label)+'</a>'
def header(eyebrow,h):return '<div class="eyebrow">'+e(eyebrow)+'</div><h1>'+e(h)+'</h1>'
def make(root,data,pdf):
    from weasyprint import HTML
    sp=root/'sppr/core/data'
    cross={r['site']:r for r in read(sp/'site_crosswalk.csv') if r['site']}
    stats={r['site']:r for r in read(data/'carbon_coverage.csv')}
    holes=read(sp/'pr_coring.csv')
    ir=collections.defaultdict(dict)
    for r in read(data/'ir_hole_headers.csv'):ir[r['hole']][r['field']]=r['value_as_extracted']
    secs=[r for r in read(sp/'pr_sections.csv') if r['section']=='Scientific report']
    figures=read(sp/'pr_site_figures.csv')
    docs={r['doc_id']:r for r in read(data/'documents.csv')}
    blocks=collections.defaultdict(list)
    for line in gzip.open(data/'pr_science_blocks.jsonl.gz','rt'):
        r=json.loads(line);blocks[r['site']].append(r)
    def irlink(site,n=1):return docs[f'IR.C{int(site)-835:02}']['url']+f'#page={n}'
    srcs=collections.defaultdict(set)
    for r in read(root/'sr/core/dataset_site_evidence.csv'):srcs[r['site']].add(r['chapter'])
    modern=json.loads((data/'modern_positions.geojson').read_text());coast=json.loads((data/'modern_coast.json').read_text())
    def map_svg():
        X=lambda lon:40+(lon+113)*14;Y=lambda lat:10+(14-lat)*13
        svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 515 270">','<defs><clipPath id="box"><rect x="40" y="10" width="448" height="234"/></clipPath></defs><rect x="40" y="10" width="448" height="234" fill="#f2f8f7" stroke="#a6bfbc"/>']
        for t in [0,5,10]:
            svg.append(f'<path d="M40 {Y(t)}H488" stroke="#d9e5e4"/><text x="35" y="{Y(t)+3}" text-anchor="end" font-size="8">{t}°</text>')
        for t in [-110,-105,-100,-95,-90,-85]:
            svg.append(f'<path d="M{X(t)} 10V244" stroke="#d9e5e4"/><text x="{X(t)}" y="258" text-anchor="middle" font-size="8">{abs(t)}°W</text>')
        svg.append('<g clip-path="url(#box)">')
        for ln in coast['lines']:svg.append('<polyline fill="none" stroke="#8a9e93" stroke-width=".9" points="'+' '.join(f'{X(x):.2f},{Y(y):.2f}' for x,y in ln)+'"/>')
        for f in modern['features']:
            a=f['properties'];lon,lat=f['geometry']['coordinates'];x,y=X(lon),Y(lat)
            if a['stage']=='SP':svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.6" fill="none" stroke="#ad6b37" stroke-width="1.05"/>')
            elif a['record'].endswith('A'):
                dy={'849':7,'850':-1}.get(a['source_site'],3)
                svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.2" fill="#135964"/><text x="{x+5:.2f}" y="{y+dy:.2f}" font-family="sans-serif" font-size="8">{a["source_site"]}</text>')
        svg.append('</g></svg>');return ''.join(svg)
    cover=header('OCEAN DRILLING PROGRAM  ·  EASTERN EQUATORIAL PACIFIC','Leg 138 航次站点校读本')
    cover+='<p class="lead">以 1991 年航后初报的站点科学叙述为正文，逐站对照航前选址、船上作业表和 1992 年 IR 孔摘要。后续研究作为独立的 SR 篇章及数据入口。</p>'
    cover+=map_svg()+'<p class="fine">现代位置。青色实点取 PR 中各站首孔，棕色空圈按 SP 的候选坐标绘制。两者可能重叠。岸线为 Natural Earth 1:50m；显示时未另作大地基准转换。</p>'
    cover+=tab(['实钻站','计划站','实钻孔数','岩芯数','取芯段 / m','回收 / m','站作业 / d'],[[s,cross[s]['proposed_site'] or '航中新增',sum(r['row_kind']=='hole' and r['site']==s for r in holes),row['cores'],row['interval_cored_m'],row['core_recovered_m'],row['time_on_site_d']] for s in sorted(cross) for row in holes if row['row_kind']=='site_total' and row['site']==s])
    cover+='<p class="fine">SP 表 1 与 PR 表 1。原刊的两处备用站 EEQ-4A、EEQ-5 保留在计划目录。完整档案包附两册底本及 IR、SR 各章。</p>'
    method=header('COLLATION  ·  SHIPBOARD OPERATIONS','42 孔的两份船上记载')
    method+='<p>将 PR 表 1 与 IR 孔摘要逐孔核对六项数值：PR 的水深栏与 IR 钻台面探底值、进尺、岩芯数、取芯段长、回收长和回收百分比。252 项中 249 项按数值完全相同。846A、846B 的回收长在 IR 孔摘要中各少一位小数。第三处差异见下表。</p>'
    method+=tab(['852B 出处','刊载内容'],[['PR 表 1，印页 31','13 芯，进尺 113.4 m，回收 119.68 m。'],['IR 第 17 章孔摘要，首印页','12 芯，进尺 113.4 m，回收 119.68 m。'],['IR 第 17 章随盘 TABLE.1','1H–13H 共十三行；13H 起止深度均 113.4 m，进尺、回收均为零。']])
    method+='<p>同孔的 IR 摘要另印钻台面总深 4985.0 m。按该页钻台面探底 3871.6 m 与进尺 113.4 m 相加为 3985.0 m，相差 1000.0 m。本版保留刊值，并把复算列为校记。851D 的孔摘要也有 1.0 m 的参比面算术差。</p>'
    method+='<p class="fine">'+link(irlink('852'),'IR 852 原页')+'　'+link(docs['PR']['url']+'#page=30','PR 表 1 原页')+'　'+link(irlink('851'),'IR 851 原页')+'</p>'
    method+='<h2>读本的文本与图表</h2><p>各站的英文科学叙述按 PR 原节和 PDF 页分组重排。站节标题经过核对，正文采用官方文字层，可见 OCR 和原排印差错。数字表和校记另存 CSV，可回到原页及随盘行号。书后的站勘、沉积速率和光学样张标明各自的重建范围。</p>'
    repeat_dir=root/'ir/core'
    samples=[r for r in read(repeat_dir/'carbonate_repeat_samples.csv') if r['row_kind']=='sample']
    runs=read(repeat_dir/'carbonate_repeat_runs.csv')
    by_run=collections.Counter(r['published_run_number'] for r in runs)
    example=next(r for r in samples if r['sample_row_id']=='IR18.T11:r022')
    first,second=(example[k] for k in ('run_1_carbonate_pct','run_2_carbonate_pct'))
    delta=abs(Decimal(first)-Decimal(second))
    method+='<h2>同一样品的多次碳酸盐测定</h2>'
    method+=f'<p>11 站的 IR 重复测定表列出 {len(samples)} 个样品、{len(runs)} 个明确标为第一、第二或第三次的测定值。第一和第二次各 {by_run["1"]} 项，第三次 {by_run["3"]} 项。每个测次保留各自的读数，原刊差值另列。</p>'
    method+=tab(['Site 853 · 表 11','第一次 / %','第二次 / %','原刊绝对差 / 百分点','复算绝对差 / 百分点'],[
        [f'第 {example["source_row"]} 个样品',first,second,example['published_absolute_difference_pct'],format(delta,'.2f')]])
    method+='<p class="fine">孔 '+e(example['reported_hole'])+'，样品 '+e(example['sample_label'])+' cm。绝对差按两次刊载百分数相减后取绝对值。　'+link(irlink('853',example['chapter_pdf_page']),'IR 表 11 原页 · 印页 '+e(example['printed_page']))+'</p>'
    carbon=header('INITIAL REPORTS  ·  ORGANIC GEOCHEMISTRY','跨站查询：已刊有机碳')
    carbon+='<p>11 张站章碳分析表共有 2,296 个样品行。666 行填有有机碳值，来自 10 个站。表中的零、一个刊为负数的值以及带脚注的结果均按来源保留。854 的表只列无机碳和碳酸盐。</p>'
    carbon+='<img class="carbon" src="'+(data/'carbon_by_site.svg').resolve().as_uri()+'"><p class="fine">每点一条刊载行。纵坐标为站章表中的 mcd，各站独立建立复合深度。面板标题的数字为有机碳非空行数。站间没有年龄对齐或插值。</p>'
    carbon+='<h2>一个脚注符号，三种含义</h2>'+tab(['站及随盘表','原表中 a 的含义','带此记号的有机碳行'],[['848 · TABLE.17','在库仑分析后的非碳酸盐残渣中测定。','17'],['852 · TABLE.13','最后加入的数据，没有进入该站其他表、图或统计。','33'],['853 · TABLE.10','两次有机碳测量的均值。','8']])
    carbon+='<p>同一字母的含义由每张表的脚注决定。在 852 的同一张表里，“两次测量的均值”另用 b 标记。已刊均值只占一个刊载行，独立测次须有各自的记录才能还原。</p>'
    parts=['<section>'+cover+'</section>','<section>'+method+'</section>','<section>'+carbon+'</section>']
    for sec in secs:
        site=sec['site'];c=cross[site];cs=stats[site]
        body=header('PRELIMINARY REPORT  ·  SCIENTIFIC REPORT',f'Site {site}')
        body+='<p class="lead">'+e(sec['checked_heading'])+'</p>'
        if c['proposed_site']:
            body+='<p>计划站 '+e(c['proposed_site'])+'，优先级 '+e(c['priority'])+'。SP 候选位置 '+e(c['candidate_latitude'])+'，'+e(c['candidate_longitude'])+'。实钻首孔 '+e(c['reference_hole'])+' 位于 '+e(c['hole_latitude'])+'，'+e(c['hole_longitude'])+'。按两份刊载坐标计算，两点相距约 '+e(c['great_circle_difference_km'])+' km。</p>'
        else:body+='<p>PR 将本站列为航中新增站；它在 SP 的候选站表中没有对应项。</p>'
        body+=tab(['实钻孔','岩芯数','进尺 / m','取芯段 / m','回收 / m','PR 水深 / m','IR 海面水深 / m'],[[r['hole'],r['cores'],r['interval_drilled_m'],r['interval_cored_m'],r['core_recovered_m'],r['water_depth_m'],ir[r['hole']]['water_depth_sea_level_m']] for r in holes if r['row_kind']=='hole' and r['site']==site])
        body+='<p class="fine">'+('　'.join(v for v in [link(c['sp_url'],'SP 站勘卡') if c['sp_url'] else '',link(c['source_url'],'PR 科学站节'),link(c['ops_url'],'PR 作业站节'),link(irlink(site),'IR 孔摘要')] if v))+'。水深两栏的参比面分别为钻台面、海面。</p>'
        body+='<p>本站 IR 碳表含 '+e(cs['source_rows'])+' 个样品行，其中 '+e(cs['with_org_c'])+' 行列有有机碳。SR 随盘数据能由行内站号或明确的表归属关联到本站的章节见在线目录和本机数据入口。</p>'
        body+='<h2>Scientific report</h2>'
        last=None
        for r in blocks[site]:
            if last!=r['pdf_page']:
                last=r['pdf_page'];body+='<div class="sourcepage">'+link(docs['PR']['url']+f'#page={last}',f'PR · PDF {last}')+'</div>'
            body+='<p class="eng">'+e(r['text'])+'</p>'
        parts.append('<section>'+body+'</section>')
    css="""@page{size:A4;margin:17mm 18mm 17mm;@bottom-left{content:"ODP  ·  LEG 138     /     STATION READER";font:7pt "DejaVu Sans";color:#55706e}@bottom-right{content:counter(page);font:8pt "DejaVu Sans";color:#274f51}}*{box-sizing:border-box}body{font:10.2pt/1.58 "Noto Sans CJK SC",sans-serif;color:#233335}section{break-before:page}section:first-child{break-before:auto}.eyebrow{font:8pt "DejaVu Sans";color:#286965;letter-spacing:.1em;border-top:1pt solid #5b8883;padding-top:7pt}h1,h2{font-family:"Noto Serif CJK SC",serif;color:#193f40;line-height:1.25;break-after:avoid}h1{font-size:23pt;margin:10pt 0 7pt}h2{font-size:15pt;margin:13pt 0 5pt}.lead{font-size:11pt}p{margin:4.5pt 0 6pt}svg{width:100%;height:69mm}.fine,.sourcepage{font-size:8.1pt;color:#4c6364}.sourcepage{margin-top:7.5pt;break-after:avoid}a{color:#226460;text-decoration:none}table{width:100%;border-collapse:collapse;font:9.1pt/1.35 "DejaVu Sans","Noto Sans CJK SC";margin:7pt 0 3pt}thead{background:#eaf3f0}td,th{text-align:left;padding:3.6pt 4pt;border-bottom:.45pt solid #ccdad6}tr{break-inside:avoid}.eng{font:11.2pt/1.43 "Liberation Serif",serif;text-align:justify;hyphens:manual;orphans:2;widows:2}.carbon{width:100%}"""
    source='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>Leg 138 航次站点校读本</title><style>'+css+'</style>'+''.join(parts)+'</html>'
    HTML(string=source,base_url=str(data.resolve())).write_pdf(pdf)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('data',type=Path);p.add_argument('output',type=Path);a=p.parse_args();make(a.root,a.data,a.output)
