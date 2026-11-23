"""Render IR interval layers in the PR figure layout; typeset an eleven-site facsimile comparison."""
from pathlib import Path
from itertools import groupby
import argparse, base64, csv, hashlib, html, io, math, shutil, tempfile, textwrap
import fitz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FixedLocator, FormatStrFormatter
from PIL import Image
from playwright.sync_api import sync_playwright
from read_tables import ROOT, DATA, save
from check_rates import PR_SHA, read
VEC=ROOT/'vector'
TICKS_BY_SITE={
844:([0,1,2,3,4],[0,5,10],[0,10,20,30,40],[0,1,2,3,4],[0,1,2,3,4]),
845:([0,1,2,3,4],[0,5,10,15,20],[0,20,40,60,80],[0,1,2,3,4],[0,1,2,3,4]),
846:([0,1,2,3,4,5],[0,10,20,30,40],[0,20,40,60,80],[0,1,2,3,4,5],[0,1,2,3,4,5]),
847:([0,1,2,3,4,5,6],[0,5,10,15,20],[0,40,80],[0,1,2,3,4,5,6],[0,1,2,3,4,5,6]),
848:([0,.5,1,1.5],[0,.5,1,1.5],[5,15,25],[0,.5,1,1.5],[0,.5,1,1.5]),
849:([0,2,4,6,8,10],[0,5,10,15,20],[0,40,80,120],[0,1,2,3,4,5],[0,2,4,6,8,10]),
850:([0,2,4,6,8],[0,5,10,15,20],[20,60,100],[0,1,2,3,4],[0,2,4,6,8]),
851:([0,2,4,6],[0,2,4,6,8,10],[20,60,100],[0,1,2,3],[0,2,4,6]),
852:([0,.5,1,1.5,2],[0,.25,.5,.75,1],[0,10,20,30],[0,.25,.5,.75,1],[0,.5,1,1.5,2]),
853:([0,.5,1,1.5],[0,.25,.5,.75,1],[0,5,10,15,20],[0,.25,.5,.75],[0,.5,1,1.5]),
854:([0,.25,.5,.75,1],[0,5,10,15,20,25],[0,.25,.5,.75,1],[0,.25,.5,.75,1])}
LABELS={'bulk_mar':'Bulk sediment','organic_carbon_mar':'Organic carbon','carbonate_mar':'Carbonate','noncarbonate_mar':'Non-carbonate','sedimentation_rate':''}
NOTES={
844:'10.40–13.50 Ma 与 13.50–16.00 Ma 的 PR 阶梯约为 37.8 与 26.7 m/Myr，IR 表 16 列 35.63 与 28.82。两处宽平台均已对原印图放大复核。',
845:'IR 印本表 14 把均值置于区间老端所在行，电子表把同一印行拆为两行。首段的年轻端由该章控制点表的 0 Ma 芯顶补足。近坐标轴的极短阶梯容易与刻度重叠。',
846:'1.58–2.41 Ma 的 PR 阶梯约为 59.0 m/Myr，与 IR 表 12 的 58.95 相符。该章表 8 的同段刊值为 46.4。两套年代控制深度分别保存。',
847:'5.68–6.30 Ma 的 PR 阶梯约为 29.3 m/Myr，IR 表 12 列 41.79。PR 曲线还延伸至 6.30 Ma 之后。右栏有机碳线取自 PR 印图的 25 个十字符号。',
848:'沉积速率可辨区间与 IR 表 16 接近。有机碳在 0.42–0.57 Ma 的图上墨迹约 0.63 mg/(cm²·kyr)，IR 表 16 印本与电子本在 0–0.73 Ma 列 1.4。两类曲线各自核对。',
849:'部分区间达到约 100 m/Myr。本站沉积速率面板的纵轴满幅为 120 m/Myr，其他四个面板的纵轴各有量纲和尺度。',
850:'沉积速率横跨多个很窄的年代区间。印图可辨的区段与 IR 表 15 刊值逐一比较；保留无法独立读取的短段与原表行号。',
851:'IR 表 14 从老端年龄 0.73 Ma 起排，首段年轻端据该章控制点表的 0 Ma 芯顶。短时段在印图上窄至数个像素，未纳入统一判定。',
852:'PR 有机碳面板可辨 11 个十字符号。右栏保留这些图读点及连线，站章表 15 的区间均值另存。',
853:'IR 表 12 末段（7.28–7.50 Ma）非碳酸盐 MAR 栏空白，0.14 印在有机碳 MAR 栏。右图有机碳取自 PR 的 8 枚十字符号。随盘深度表头为 mbsf，印本为 mcd。',
854:'初报图注提到有机碳，实际只有四面板，右上是沉积速率。三个 MAR 面板的逐样品曲线在停积处断开。3.48–5.29 Ma 的表值为 0.00；扫描阶梯约高于零线 0.35 m/Myr。'}
def make_figure(site,panels,intervals,marks,page):
    fig_no=panels[0]['pr_figure']; srch=page.search_for(f'Figure {fig_no}.')[0]
    left=min(float(p['left_pt']) for p in panels)-60;right=max(float(p['right_pt']) for p in panels)+14
    top=min(float(p['top_pt']) for p in panels)-12;bottom=max(float(p['bottom_pt']) for p in panels)+(91 if site==854 else 34)
    if site == 854:
        cap=next(b for b in page.get_text('blocks') if f'Figure {fig_no}.' in b[4])
        left=min(left,cap[0]-4);right=max(right,cap[2]+4);bottom=max(bottom,cap[3]+4)
    crop=fitz.Rect(left,top,right,bottom);fig=plt.figure(figsize=(crop.width/72,crop.height/72))
    for j,p in enumerate(panels):
        l,r,t,b=[float(p[k]) for k in ('left_pt','right_pt','top_pt','bottom_pt')]
        unit=p['unit']; key=p['quantity'];max_age=float(p['x_max_Ma']);ymax=float(p['y_max'])
        ax=fig.add_axes([(l-left)/crop.width,(bottom-b)/crop.height,(r-l)/crop.width,(b-t)/crop.height])
        yrange=TICKS_BY_SITE[site][j]
        if p['interval_layer']!='individual_series_only':
            xs=[];ys=[]
            for row in intervals:
                if row[key]=='':xs.append(math.nan);ys.append(math.nan);continue
                rate=float(row[key]);xs.extend([float(row['young_Ma']),float(row['old_Ma'])]);ys.extend([rate,rate])
            ax.plot(xs,ys,color='black',lw=.8,solid_capstyle='butt')
        elif key=='organic_carbon_mar' and marks:
            ax.plot([float(m['age_Ma']) for m in marks],[float(m['value']) for m in marks],
                    color='black',lw=.42,marker='+',markersize=3,markeredgewidth=.52)
        ax.set(xlim=(0,max_age),ylim=(0,ymax),xlabel='Age (Ma)',ylabel='Sedimentation rate (m/m.y.)' if key=='sedimentation_rate' else 'Mass accumulation rate ('+('mg' if key=='organic_carbon_mar' else 'g')+ '/(cm² kyr))')
        step=1 if max_age==7 else 2 if max_age==8 else 3
        ax.xaxis.set_major_locator(MultipleLocator(step));ax.xaxis.set_minor_locator(MultipleLocator(.5 if max_age in (7,8) else 1))
        ax.yaxis.set_major_locator(FixedLocator(yrange));ax.yaxis.set_minor_locator(MultipleLocator((yrange[-1]-yrange[-2])/2))
        ax.yaxis.set_major_formatter(FormatStrFormatter('%g'));ax.xaxis.set_major_formatter(FormatStrFormatter('%g'))
        ax.tick_params(direction='in',top=True,right=True,width=.5,length=4,pad=2,labelsize=6.8)
        ax.tick_params(which='minor',direction='in',top=True,right=True,width=.45,length=2.2)
        ax.yaxis.labelpad=.9;ax.xaxis.labelpad=.3
        if LABELS[key]:
            xp=.31 if site==846 and key=='bulk_mar' else .08;ax.text(xp,.96,LABELS[key],ha='left',va='top',transform=ax.transAxes,fontsize=7)
    caption=f'Figure {fig_no}. Sedimentation rate and bulk, organic carbon, carbonate, and non-carbonate (1-carbonate) mass-accumulation rates (MAR) vs. age for Site {site}. The thin solid line in the MAR plots represents discrete sample points. The thick solid line in the MAR plots represents the mean value between stratigraphic control points.'
    # Caption reflows in its original vacant rectangle; original facsimile remains the textual witness.
    wrapped=textwrap.fill(caption,width=116 if site==854 else 53,break_long_words=False,break_on_hyphens=False)
    fig.text((srch.x0-left)/crop.width,(bottom-srch.y0)/crop.height,wrapped,fontfamily='Liberation Serif',fontsize=9.1,va='top',linespacing=1.08)
    VEC.mkdir(exist_ok=True)
    svg=VEC/f'Site{site}_intervals.svg';fig.savefig(svg,metadata={'Date':None})
    fig.savefig(VEC/f'Site{site}_intervals.pdf',metadata={'CreationDate':None,'ModDate':None});plt.close(fig)
    return crop,svg
def data_uri(b,mime):return f'data:{mime};base64,'+base64.b64encode(b).decode('ascii')
def scan_uri(p,rect):
    pm=p.get_pixmap(matrix=fitz.Matrix(2.6,2.6),colorspace=fitz.csGRAY,clip=rect)
    im=Image.frombytes('L',(pm.width,pm.height),pm.samples);buff=io.BytesIO();im.save(buff,format='JPEG',quality=91,optimize=True)
    return data_uri(buff.getvalue(),'image/jpeg')
def build(pr,out,browser_exe):
    if hashlib.sha256(pr.read_bytes()).hexdigest()!=PR_SHA:raise ValueError('Unexpected PR PDF checksum')
    plt.rcParams.update({'font.family':'Liberation Sans','font.size':7.5,'axes.labelsize':7.3,'svg.fonttype':'none','pdf.fonttype':42,'axes.linewidth':.55,'svg.hashsalt':'ODP138-PR-rates'})
    panels=read('pr_panel_axes.csv');intervals=read('ir_mean_intervals.csv');summary=read('pr_rate_summary.csv');manifest=read('ir_interval_witnesses.csv')
    allmarks=read('pr_printed_marks.csv');chunks=[];capt=[]
    with fitz.open(pr) as doc:
        for site_key,group in groupby(panels,key=lambda x:x['site']):
            site=int(site_key);ls=list(group);q=ls[0];rs=next(r for r in summary if r['site']==site_key)
            tab=next(r for r in manifest if r['site']==site_key and r['role']=='interval_mean');page=doc[int(q['pr_pdf_page'])-1]
            marks=[r for r in allmarks if r['site']==site_key]
            crop,svg=make_figure(site,ls,[r for r in intervals if r['site']==site_key],marks,page)
            raw=scan_uri(page,crop);rebuilt=data_uri(svg.read_bytes(),'image/svg+xml')
            exceptional=(f" · 超出图读容差 {rs['different_at_print_scale']} 段" if rs['different_at_print_scale']!='0' else '')
            panel_title='IR 区间层 ＋ PR 有机碳图读层' if marks else f"IR 随盘表 {tab['ir_table']} · 区间层重绘"
            foot='右图有机碳十字符号取自 PR 印图，其余阶梯取自 IR 表。' if marks else '右图按 IR 表值作图；逐样品折线、十字符号和未证实的区间层保留在左图。'
            text=f"""<section><header><span>Ocean Drilling Program　／　Leg 138</span><span>东赤道太平洋　·　航次报告图件对校</span></header>
<h1>Site {site}<span>沉积速率与质量堆积速率</span></h1>
<div class="pairs"><figure><figcaption>Preliminary Report · 图 {q['pr_figure']}<small>印页 {q['pr_print_page']} / PDF {q['pr_pdf_page']}</small></figcaption><img src="{raw}"></figure><figure><figcaption>{panel_title}<small>站章印页 {tab['ir_print_page']} / PDF {tab['ir_pdf_page']}</small></figcaption><img src="{rebuilt}"></figure></div>
<div class="meta"><b>核对了 {rs['evaluated']} / {rs['total_intervals']} 个沉积速率区间{exceptional}</b><span>图读容差 ±{float(rs['tolerance_m_Myr']):g} m/Myr</span></div>
<p>{NOTES[site]}</p><footer>{foot}图注沿用原图位置，区间边界及出版版本见配套数据。<span>{site-843} / 11</span></footer></section>"""
            chunks.append(text);capt.append(dict(site=site,pr_figure=q['pr_figure'],pr_pdf_page=q['pr_pdf_page'],ir_mean_table=tab['ir_table'],svg='vector/'+svg.name,print_digitized_marks=len(marks),source_crop_left=round(crop.x0,2),source_crop_top=round(crop.y0,2),source_crop_right=round(crop.x1,2),source_crop_bottom=round(crop.y1,2),editorial_note=NOTES[site]))
    save('figure_index.csv',capt)
    css="""@page{size:297mm 210mm;margin:0}*{box-sizing:border-box}body{margin:0;font:10pt/1.45 'Noto Sans CJK SC',sans-serif;color:#21343a;-webkit-print-color-adjust:exact}section{height:210mm;width:297mm;position:relative;padding:6mm 12mm 7mm;page-break-after:always}section:last-child{page-break-after:auto}header,footer,.meta,figcaption{display:flex;align-items:baseline;justify-content:space-between}header{padding-bottom:1.5mm;border-bottom:1px solid #92aba9;color:#365759;font:8.3pt 'Liberation Sans','Noto Sans CJK SC'}h1{font:700 24pt/1.18 'Liberation Serif','Noto Serif CJK SC';color:#19343c;margin:2mm 0 2mm}h1 span{font:14pt 'Noto Serif CJK SC';margin-left:5mm}.pairs{display:grid;grid-template-columns:1fr 1fr;gap:8mm}figure{margin:0}figcaption{font:600 11pt 'Liberation Serif','Noto Serif CJK SC';border-bottom:1px solid #b3c5c2;padding-bottom:1mm}figcaption small{font:8pt 'Noto Sans CJK SC';font-weight:400;color:#51696a}figure img{width:100%;height:143.5mm;display:block;object-fit:contain}.meta{border-top:1px solid #98b2b1;padding-top:1.2mm;color:#244d4d}.meta b{font-size:9.4pt}.meta span{font:8.3pt 'Liberation Sans','Noto Sans CJK SC'}p{margin:1mm 0;font-size:9.4pt;line-height:1.52}footer{position:absolute;bottom:4mm;left:12mm;right:12mm;color:#536b6d;font-size:7.7pt;border-top:1px solid #ccd8d7;padding-top:.8mm}footer span{white-space:nowrap}"""
    s='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>ODP Leg 138 · Preliminary Report figure collation</title><style>'+css+'</style><body>'+''.join(chunks)+'</body></html>'
    with tempfile.TemporaryDirectory() as td,sync_playwright() as pw:
        p=Path(td)/'atlas.html';p.write_text(s);browser=pw.chromium.launch(executable_path=browser_exe or shutil.which('chromium'),args=['--no-sandbox','--single-process','--no-zygote','--disable-dev-shm-usage'])
        page=browser.new_page();page.goto(p.as_uri());page.evaluate('document.fonts.ready');page.pdf(path=str(out),print_background=True,prefer_css_page_size=True,tagged=True);browser.close()
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('pr_pdf',type=Path);p.add_argument('--output',type=Path,default=ROOT/'Leg138_PR_Rate_Atlas.pdf');p.add_argument('--chromium');a=p.parse_args();build(a.pr_pdf,a.output,a.chromium)
