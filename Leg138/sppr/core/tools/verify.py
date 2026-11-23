"""Independent consistency checks on transcriptions, provenance links and the station section edition."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import csv,hashlib,json,gzip,argparse
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data'
def read(name):
    with (D/(name+'.csv')).open() as f:return list(csv.DictReader(f))
def verify(primary=None):
    x=read('site_crosswalk');cards=read('sp_site_cards');holes=read('site_holes');pr=read('pr_coring')
    assert len(x)==13 and len(cards)==12 and len(holes)==len({r['hole'] for r in holes})==42
    assert {r['proposed_site'] for r in x if r['proposed_site']}=={r['proposed_site'] for r in cards}
    assert {r['site'] for r in x if r['site']}=={r['site'] for r in holes}=={str(n) for n in range(844,855)}
    assert {r['proposed_site'] for r in x if not r['site']}=={'EEQ-4A','EEQ-5'}
    assert [r['site'] for r in x if not r['proposed_site']]==['850']
    assert next(r for r in x if r['site']=='854')['priority']=='2'
    byhole={r['hole']:r for r in pr if r['row_kind']=='hole'}
    assert all(r['latitude_printed']==byhole[r['hole']]['latitude'] and r['longitude_printed']==byhole[r['hole']]['longitude'] for r in holes)
    cols=['cores','interval_drilled_m','interval_cored_m','core_recovered_m','apc_cored_m','apc_recovered_m','xcb_cored_m','xcb_recovered_m','time_on_hole_h']
    for r in pr:
        if r['row_kind']!='site_total':continue
        hs=[v for v in byhole.values() if v['site']==r['site']]
        for col in cols:assert sum(Decimal(v[col] or '0') for v in hs)==Decimal(r[col]),(r['site'],col)
    assert sum(Decimal(v['core_recovered_m']) for v in byhole.values())==Decimal('5536.78')
    assert Counter(r['profile_relation'] for r in read('survey_profiles'))=={'shared_survey_profile_graphic':9,'different_survey_product':1,'no_prospectus_site':1}
    with gzip.open(D/'pages.jsonl.gz','rt') as f:pages=[json.loads(l) for l in f]
    assert len({(r['doc_id'],r['pdf_page']) for r in pages})==len(pages)==165
    prows=read('pr_site_figures');assert len(prows)==44 and len(read('pr_sections'))==22
    ids={r['item_id'] for r in read('report_items')};assert {r['item_id'] for r in prows}<=ids
    workflows=read('pr_plot_workflows')
    assert len(workflows)==len({r['item_id'] for r in workflows})==22
    assert {r['item_id'] for r in workflows}<={r['item_id'] for r in prows}
    assert Counter(r['site'] for r in workflows)=={str(n):2 for n in range(844,855)}
    assert len(read('sp_card_fields'))==146 and len(read('sp_survey_times'))==19
    timestamps={r['iso_utc'] for r in read('sp_survey_times')};assert '' not in timestamps
    assert next(r for r in read('sp_site_cards') if r['proposed_site']=='WEQ-4')['sediment_record']=='VNTR01-05 GC and VNTR01-06 PC'
    assert next(r for r in read('sp_site_cards') if r['proposed_site']=='EEQ-2')['secondary_site']=='0842Z 25 Sept. 1989'
    series=read('pr_fig15_backtrack');assert [int(r['age_ma']) for r in series]==list(range(10))
    if primary:
        for r in read('source_manifest'):
            p=primary/r['filename']
            with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
    edition=ROOT/'publication/Leg138_SP_Proposed_Sites.pdf'
    if edition.exists():
        import fitz
        d=fitz.open(edition);assert len(d)==len(d.get_toc())==36
        for i,r in enumerate(cards):
            txt=d[3*i].get_text();assert r['proposed_site'] in txt and 'Objectives' in txt and r['anticipated_sediment_rocks'] in txt
            assert d[3*i+1].get_images() and d[3*i+2].get_images()
    result={'sp_pr_pages':len(pages),'prospectus_cards':len(cards),'preliminary_sites':len({r['site'] for r in holes}),'published_holes':len(holes),'published_hole_records':len(byhole),'checked_native_fields':146,'paired_publication_profiles':9,'site_total_native_fields_compared':len(cols)*11,'digitized_site851_graphic_markers':len(series),'station_edition_pages':36 if edition.exists() else None}
    result['source_captions_with_processing_evidence']=len(workflows)
    return result
if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--primary',type=Path);print(json.dumps(verify(a.parse_args().primary),indent=2))
