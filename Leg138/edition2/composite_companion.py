"""Bind the completed PR composite comparison atlas to source HTML pages, without changing PDF foliation."""
import argparse,csv,json,shutil
from pathlib import Path
import fitz
from companions import read,write,digest
from build_edition import link,note

def add(root,out):
    module=root/'figures/core/composite_v2';atlas=module/'Leg138_PR_Composite_Atlas.pdf';index=module/'data/figure_index.csv'
    if not (atlas.is_file() and index.is_file() and (out/'html/PR.html').is_file()):return None
    rows=read(index);assert len(rows)==22 and set(int(r['atlas_page']) for r in rows)==set(range(1,23))
    with fitz.open(atlas) as pdf:assert len(pdf)==22
    target=out/'resources/pr_composite';target.mkdir(exist_ok=True,parents=True);shutil.copyfile(atlas,target/atlas.name)
    shutil.copyfile(index,target/'figure_index.csv')
    shutil.copyfile(module/'README.md',target/'README.md')
    for fname in ['source_tracks.csv','site_series.csv','panel_regions.csv','figure_layers.csv','retained_layers.csv','scan_trace_checks.csv']:
        source=module/'data'/fname
        if source.exists():shutil.copyfile(source,target/fname)
    records=[];reader=out/'html/PR.html';page_text=reader.read_text()
    official=next(r for r in read(out/'documents.csv') if r['doc_id']=='PR')
    for r in rows:
        pos=r['pdf_page'];page=r['atlas_page'];overlay_rel=Path(r['vector_overlay'])
        if overlay_rel.is_absolute() or '..' in overlay_rel.parts:raise ValueError('Expected local vector path')
        vector=module/overlay_rel;assert vector.is_file()
        (target/overlay_rel).parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(vector,target/overlay_rel)
        rel='resources/pr_composite/'+atlas.name
        rec=dict(doc_id='PR',site=r['site'],item_id=r['pr_figure'] if r['pr_figure'].startswith('PR.F') else 'PR.F'+r['pr_figure'],source_pdf_page=pos,source_witness_sha256=official['source_pdf_sha256'],
                 atlas=rel,atlas_page=page,atlas_sha256=digest(target/atlas.name),vector_overlay='resources/pr_composite/'+overlay_rel.as_posix(),overlay_sha256=digest(vector))
        if 'published_source_sha256' in r and r['published_source_sha256']:
            assert r['published_source_sha256']==official['source_pdf_sha256']
        records.append(rec)
        marker='<section id="p'+str(pos)+'">';line='<p class="meta">Composite stratigraphic summary · '+link('../'+rel+'#page='+str(page),'Source and vector comparison')+' · '+link('../'+rec['vector_overlay'],'Vector overlay')+' · '+link('../resources/pr_composite/README.md','Inputs and filtering choices')+'</p>'+note('GRAPE, magnetic susceptibility and the three reflectance bands are drawn from released numerical series. Polarity, age, graphic lithology, units and the depth axis retain the original image. The historic 20-point filter is unresolved; the alternative display filter is documented.')
        if line not in page_text:page_text=page_text.replace(marker,marker+line,1)
    reader.write_text(page_text);write(out/'composite_companion.csv',records)
    home=out/'index.html';s=home.read_text();addon='<p>'+link('resources/pr_composite/'+atlas.name,'PR 综合地层图 · 图层对照附读')+' · '+link('composite_companion.csv','来源页与图层定位')+'</p>'
    if addon not in s:home.write_text(s.replace('</header>',addon+'</header>',1))
    return dict(sites=len({r['site'] for r in records}),comparison_pages=len(records),atlas_sha256=digest(atlas),source_pdf_changed=False)
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('root',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args();result=add(a.root,a.output)
    if result:(a.output/'composite_companion_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
