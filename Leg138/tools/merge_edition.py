"""Assemble and verify the Leg 138 collation from six independently reproducible PDF parts.

Usage: python merge_edition.py PATH_TO_LEG138_ALL OUTPUT.pdf [--manifest checks.json]
Requires PyMuPDF and WeasyPrint, plus the Noto Sans/Serif CJK SC fonts for the contents page.
"""
import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import html
import json
from pathlib import Path

import fitz
from weasyprint import HTML


@dataclass(frozen=True)
class Part:
    path: str
    heading: str
    english: str
    detail: str
    chapters: tuple = ()


PARTS = (
    Part('publication/Station_reader.pdf','航次与站点校读','Station reader',
         '航后初报的站点科学叙述、计划与实钻位置、孔作业记录和有机碳数据出处。'),
    Part('sppr/core/publication/Leg138_SP_Proposed_Sites.pdf','航前拟钻站','Proposed drilling sites',
         'Scientific Prospectus 的 12 个候选站。计划站说明、测区图与测线剖面均可按站翻阅。'),
    Part('figures/core/Leg138_PR_Rate_Atlas.pdf','航后初报图件对校','Preliminary Report figures',
         'Sites 844–854 的沉积与物质累积速率图。图集逐站标明曲线或符号的恢复依据。',
         tuple((idx + 1, f'Site {site}') for idx, site in enumerate(range(844,855)))),
    Part('sr/core/figures/SR06_Figure11_comparison.pdf','后续研究图件复算','Scientific Results figure',
         'Scientific Results 第 6 章图 11。用发表的年代与深度表复算沉积速率，与原刊图版对照。'),
    Part('plates/core/optical/Optical_windows_Leg138.pdf','岩芯照片与标尺','Core photographs',
         '每站一张原生彩照，分别截取第 3 节沉积物内窗及同高的标尺窗口。保留来源像素与裁片坐标。',
         ((1,'Sites 844–846'),(2,'Sites 847–849'),(3,'Sites 850–852'),(4,'Sites 853–854'))),
    Part('sppr/core/figures/pr_fig15_graphic_check.pdf','航后初报的古地理图读','Site 851 backtrack',
         '初报图 15 印刷轨迹上十个时代点的图读值。对照其现代标记与实钻坐标，保留原图标注差异。'),
)


def outline_rows(source, offset):
    rows = []
    for depth, title, page, dest in source.get_toc(simple=False):
        dest = {key:value for key,value in dest.items() if key != 'xref'}
        if dest.get('kind') == fitz.LINK_GOTO:
            dest['page'] += offset
        rows.append([depth + 1, title, page + offset if page > 0 else page, dest])
    return rows


def contents_page(parts):
    items = []
    for part, spans in zip(PARTS,parts):
        first,last = spans['first_page'], spans['last_page']
        pages = str(first) if first == last else f'{first}–{last}'
        items.append(f'<section><div class="folio">{pages}</div><div class="heading">{html.escape(part.heading)}</div>'
                     f'<div class="english">{html.escape(part.english)}</div><p>{html.escape(part.detail)}</p></section>')
    document = """<!doctype html><html lang="zh-CN"><meta charset="utf-8"><style>
    @page { size: A4; margin:18mm 21mm 17mm }
    *{box-sizing:border-box} body{font-family:"Noto Sans CJK SC",sans-serif;color:#213236;margin:0}
    .eyebrow,.english,.folio,footer{font-family:"DejaVu Sans","Noto Sans CJK SC",sans-serif}
    .eyebrow{font-size:9pt;letter-spacing:1.35pt;color:#326263}
    h1,.heading{font-family:"Noto Serif CJK SC",serif}
    h1{font-size:30pt;line-height:1.35;margin:13pt 0 6pt;font-weight:600}
    .intro{font-size:10pt;line-height:1.7;margin:0 0 19pt}
    section{border-top:.65pt solid #acbfbc;padding:8pt 0 10pt;break-inside:avoid}
    .heading{font-size:14pt;font-weight:600;line-height:1.4}
    .folio{float:right;color:#285e62;font-size:13pt;margin-top:2pt}
    .english{font-size:8.5pt;color:#326263;margin:2pt 0}
    p{font-size:9.2pt;line-height:1.6;margin:2pt 0 0}
    footer{border-top:.7pt solid #acbfbc;color:#526a69;font-size:8pt;letter-spacing:.6pt;padding-top:9pt}
    </style><div class="eyebrow">OCEAN DRILLING PROGRAM · LEG 138</div><h1>分卷目录</h1>
    <div class="intro">点击条目跳转至相应部分。卷内书签可按站点或图版继续浏览。</div>"""
    raw = HTML(string=document + ''.join(items) + '<footer>LEG 138  /  COLLATED REPORT EDITION</footer></html>').write_pdf()
    pdf = fitz.open(stream=raw,filetype='pdf')
    assert len(pdf) == 1, 'Contents page overflow'
    return pdf


def link_identity(link, offset=0):
    rect = tuple(round(v,2) for v in link['from'])
    if link['kind'] == fitz.LINK_GOTO:
        to = link.get('to',fitz.Point(0,0))
        return ('internal',rect,link['page']+offset,tuple(round(v,2) for v in to))
    return (link['kind'],rect,link.get('uri') or link.get('file') or link.get('nameddest') or '')


def assemble(root, target, manifest):
    doc = fitz.open()
    outline, spans = [], []
    for part in PARTS:
        filename = root / part.path
        with fitz.open(filename) as source:
            offset = len(doc)
            doc.insert_pdf(source, links=True, annots=True, widgets=True)
            outline.append([1,part.heading,offset+1])
            outline.extend(outline_rows(source,offset))
            outline.extend([2,title,offset+page] for page,title in part.chapters)
            spans.append(dict(path=part.path,heading=part.heading,first_page=offset+1,
                              last_page=len(doc),input_sha256=hashlib.sha256(filename.read_bytes()).hexdigest()))
    with contents_page(spans) as contents:
        doc.insert_pdf(contents)
    contents_page_no = len(doc)
    outline.insert(0,[1,'分卷目录 · Contents',contents_page_no])
    doc.set_toc(outline,collapse=1)
    doc.xref_set_key(doc.pdf_catalog(),'PageMode','/UseOutlines')
    page = doc[-1]
    for part, span in zip(PARTS,spans):
        markers = page.search_for(part.english)
        assert len(markers) == 1, (part.english,markers)
        anchor = markers[0]
        page.insert_link({'kind':fitz.LINK_GOTO,
            'from':fitz.Rect(57,anchor.y0-23,page.rect.width-57,anchor.y1+22),
            'page':span['first_page']-1,'to':fitz.Point(0,0)})
    first = doc[0]
    footer_text = f'Contents  /  {contents_page_no}'
    first.insert_text((270,820),footer_text,fontsize=8,color=(.16,.37,.38))
    first.insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(265,805,337,829),
                       'page':contents_page_no-1,'to':fitz.Point(0,0)})
    doc.set_metadata({'title':'ODP Leg 138 · 航次校读本与图件对校',
                      'subject':'Sites 844–854, planning dossiers, shipboard reports, Scientific Results and core photographs',
                      'keywords':'Leg 138; eastern equatorial Pacific; Ocean Drilling Program; source collation'})
    target.parent.mkdir(parents=True,exist_ok=True)
    doc.save(target,garbage=4,deflate=True,no_new_id=True)
    doc.close()
    preserved = 0
    with fitz.open(target) as result:
        for part, item in zip(PARTS,spans):
            with fitz.open(root / part.path) as source:
                offset = item['first_page']-1
                before = 0
                for i, original in enumerate(source):
                    merged = result[offset+i]
                    assert original.rect == merged.rect
                    merged_text = merged.get_text()
                    if offset+i == 0:
                        assert footer_text in merged_text
                        merged_text = merged_text.replace(footer_text+'\n','')
                    assert original.get_text() == merged_text, (part.path,i+1)
                    source_links = Counter(link_identity(link,offset) for link in original.get_links())
                    dest_links = Counter(link_identity(link) for link in merged.get_links())
                    assert not (source_links - dest_links), (part.path,i+1,source_links-dest_links)
                    assert sum(dest_links.values()) == sum(source_links.values()) + int(offset+i == 0)
                    before += sum(source_links.values())
                item['preserved_source_links'] = before
                preserved += before
        index_links = result[-1].get_links()
        assert sorted(link['page']+1 for link in index_links) == [s['first_page'] for s in spans]
        assert any(link.get('page') == contents_page_no-1 for link in result[0].get_links())
        assert len(result.get_toc()) == len(outline)
        for row in result.get_toc():
            assert 1 <= row[2] <= len(result)
    report = dict(parts=spans, total_pages=contents_page_no,contents_page=contents_page_no,
                  bookmark_count=len(outline),preserved_source_links=preserved,new_internal_links=1+len(spans),
                  output_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),output_bytes=target.stat().st_size)
    if manifest:
        manifest.parent.mkdir(parents=True,exist_ok=True)
        manifest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--manifest',type=Path)
    args = parser.parse_args()
    summary = assemble(args.root,args.output,args.manifest)
    print(f"{summary['total_pages']} pages, {summary['bookmark_count']} bookmarks, "
          f"{summary['preserved_source_links']} original links, {summary['new_internal_links']} contents links.")
