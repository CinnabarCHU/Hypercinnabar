"""Finalize a checked full-volume edition with reproducible manifests and exact file hashes."""
from collections import Counter
from pathlib import Path
import argparse,json,shutil
from companions import read,digest
def finalize(output,light):
    summary=json.loads((output/'verification.json').read_text())
    checks=json.loads((output/'table_and_object_checks.json').read_text())
    regions=json.loads((output/'region_checks.json').read_text())
    verified=json.loads((output/'independent_checks.json').read_text())
    assert summary['source_pages']==verified['source_ocr_page_equality']
    docs=read(output/'documents.csv')
    summary['series']={s:{'documents':sum(x['series']==s for x in docs),'source_pages':sum(int(x['source_pdf_pages']) for x in docs if x['series']==s),'edition_pages':sum(int(x['edition_pdf_pages']) for x in docs if x['series']==s)} for s in ('SP','PR','IR','SR')}
    summary['rendered_table_representations']=sum(int(r['pdf_table_assets']) for r in read(output/'pages.csv'))
    summary['new_rendered_tables']=checks['new_tables_confirmed_in_chapter_pdfs']
    summary['source_regions']=regions['item_location_records']
    summary['region_previews']=regions['crop_pngs']
    summary['site853_corrected_graft']=checks['corrected_site853_pdf_sha256']
    extra={}
    if (output/'sr_table_annex_checks.json').is_file():
        extra=json.loads((output/'sr_table_annex_checks.json').read_text())
        summary['sr_additional_print_tables']=extra['items']
        summary['sr_print_tables_with_positional_candidates']=extra['items_with_positional_cells']
        summary['sr_appendix_pages']=extra['new_chapter_pdf_pages']
        assert (output/'sr_table_annex_verified.json').is_file()
    composite={}
    if (output/'composite_companion_checks.json').exists():
        composite=json.loads((output/'composite_companion_checks.json').read_text())
        summary['pr_composite_companion_pages']=composite['comparison_pages']
        summary['pr_composite_companion_sha256']=composite['atlas_sha256']
    (output/'release_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    base=(light/'README.md').read_text().split('\n## 本次全卷导出')[0].rstrip()
    detail=f"""\n\n## 本次全卷导出\n\n{summary['documents']} 个分册覆盖 {summary['source_pages']:,} 个主体来源页，PDF 合计 {summary['paired_pdf_pages']:,} 页。其中 {summary['typeset_pages']:,} 页为重排与结构化资料，{summary['cards_and_figure_comparisons']} 页为精校站卡与具名图件，另保留 {summary['source_pages']:,} 个整页见证。{verified['intact_source_image_stream_references']:,} 个原图像流引用通过字节核验。\n\nPDF 和 HTML 实际编排 {summary['rendered_table_representations']} 项表的具名表示，包含新接入的 92 份 IR 电子表、63 份 IR 印表、7 份 SR 印表。IR 印表的 {checks['ir_cell_slots']:,} 个单元格中 {checks['provisional_ir_print_cells']} 个待复核；其他状态可在 table_and_object_checks.json 查验。SR 的 {checks['sr_accepted_objects']} 个已接受项目与 {checks['sr_withdrawn_running_references']} 个撤回的正文提及分别标明。\n\nsource_regions.csv 记录 {regions['item_location_records']:,} 个来源定位，产生 {regions['crop_pngs']:,} 个范围裁片。图面内 54 个量轴区域、11 个整图范围单列。另有印表窗口、图注定位和历史文字证据。rate_plot_lineage.csv 给每站绘图器、图件及输入数表 SHA-256。Site 853 随盘原行 59 的 0.14 在有机碳 MAR 栏，非碳酸盐 MAR 留空。\n"""
    if extra:
        detail+=f"\nSR 附读另外逐项列出此前没有具名数据的 {extra['items']} 张印表，含 {extra['segments']} 个来源页段。其中 {extra['items_with_positional_cells']} 张有位置候选，坐标读数覆盖 {extra['physical_body_rows']:,} 条物理行、{extra['candidate_body_cells']:,} 个候选表体槽。{extra['field_mapped_named_rows']} 行有人工逐字段读值；另有 {extra['separately_transcribed_unassigned_marks']} 个符号核过列名与位置，样品归属未定。{extra['segments_in_typeset_evidence_supplement']} 个证据段列于相应 SR 分册末的 {extra['new_chapter_pdf_pages']} 页附读。原页及前版重绘页码不变。\n"
    if composite:detail+="\nPR 综合地层图的 22 页对照图集作为 HTML 附读。已发布数值用于重绘 66 个物性面板，极性、时代、图示岩性、单元与深度轴保留原印图。历史 20 点滤波尚未复原，显示滤波另有编校说明。\n"
    (light/'README.md').write_text(base+detail);(output/'README.md').write_text(base+detail)
    for key in ('documents.csv','pages.csv','resources.csv','source_regions.csv','rate_plot_lineage.csv','verification.json','independent_checks.json','region_checks.json','region_file_checks.json','font_check.json','browser_checks.json','table_and_object_checks.json','release_summary.json','sr_table_catalog.csv','sr_table_annex.csv','sr_table_annex_checks.json','sr_table_annex_verified.json','composite_companion.csv','composite_companion_checks.json'):
        source=output/key
        if key in ('browser_checks.json','sr_table_catalog.csv','sr_table_annex.csv','sr_table_annex_checks.json','sr_table_annex_verified.json','composite_companion.csv','composite_companion_checks.json') and not source.exists():continue
        shutil.copyfile(source,light/key)
    listing=output/'SHA256SUMS'
    files=sorted(p for p in output.rglob('*') if p.is_file() and p!=listing)
    with listing.open('w') as f:
        for p in files:f.write(digest(p)+'  '+p.relative_to(output).as_posix()+'\n')
    release=dict(file_count=len(files),sha256sums_sha256=digest(listing),publication_manifest_sha256=digest(output/'documents.csv'),rate_plot_lineage_sha256=digest(output/'rate_plot_lineage.csv'),PR_pdf_sha256=digest(output/'pdf/PR.pdf'),site853_pdf_sha256=checks['corrected_site853_pdf_sha256'],site853_svg_sha256=checks['corrected_site853_svg_sha256'])
    if extra:
        release['sr_table_catalog_sha256']=digest(output/'sr_table_catalog.csv')
        release['sr_table_annex_sha256']=digest(output/'sr_table_annex.csv')
    if composite:
        release['pr_composite_atlas_sha256']=composite['atlas_sha256']
    (light/'release_hashes.json').write_text(json.dumps(release,indent=2)+'\n')
    return release
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);p.add_argument('light',type=Path);a=p.parse_args();print(json.dumps(finalize(a.output,a.light),indent=2))
