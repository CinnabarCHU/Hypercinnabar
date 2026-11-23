"""Embed locally compiled Leg 138 station, item and dataset indices into a file:// reader."""
import argparse
import csv
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path
from edition_browser import build_portal


def load_rows(root, name):
    with (root / name).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def by_site(rows):
    return {r['site']: r for r in rows if r['site']}


def build(root, data, output):
    def src(name):
        return load_rows(root, name)
    def local(name):
        return load_rows(data, name)
    cards = {r['proposed_site']: r for r in src('sppr/core/data/sp_site_cards.csv')}
    repeats = by_site(src('ir/core/carbonate_repeat_sources.csv'))
    repeat_samples = src('ir/core/carbonate_repeat_samples.csv')
    for idx, card in enumerate(cards.values()):
        card['edition_page'] = 1 + idx * 3
    cross = src('sppr/core/data/site_crosswalk.csv')
    total = by_site([r for r in src('sppr/core/data/pr_coring.csv') if r['row_kind'] == 'site_total'])
    carbon = by_site(local('carbon_coverage.csv'))
    strands = by_site(src('figures/core/data/figure_index.csv'))
    plate = by_site(src('plates/core/data/station_summary.csv'))
    splice = by_site(src('disc/core/replay/splice_membership.csv'))
    profiles = by_site(src('sppr/core/data/survey_profiles.csv'))
    ir = by_site([r for r in local('documents.csv') if r['series']=='IR' and r['role']=='site_chapter'])
    ir_items = src('ir/core/chapter_items.csv')
    sr = {r['chapter']:r for r in src('sr/core/chapters.csv')}
    datasets = {r['dataset_id']:r for r in src('sr/core/datasets.csv')}
    sr_evidence = src('sr/core/dataset_site_evidence.csv')
    notes = src('sppr/core/data/editorial_notes.csv')
    holes = src('sppr/core/data/site_holes.csv')
    split = src('plates/core/optical/patches.csv')
    comparisons = local('pr_ir_field_comparison.csv')
    carbon_editions = local('carbon_distribution_comparison.csv')
    reported = {(r['source_item'],r['source_line']):r for r in local('carbon_reported.csv')}
    carbon_rows = []
    for row in src('ir/core/tables/carbons.csv'):
        parsed = reported.get((row['item_id'],row['source_line']))
        if parsed is None:
            if row['organic_c_pct']:
                raise ValueError(f"Unmatched published value {row['item_id']} line {row['source_line']}")
            parsed = dict(site=row['site'],hole=row['reported_hole'],sample=row['sample_label'],
                          depth_mbsf=row['depth_mbsf'],depth_mcd=row['depth_mcd'],published_organic_c='',
                          organic_c_pct='',footnote_marker='',footnote_role='no_published_organic_c',
                          source_item=row['item_id'],source_line=row['source_line'],
                          source_url='https://www-odp.tamu.edu/publications/138_IR/'+row['source_path'])
        carbon_rows.append(parsed)
    with gzip.open(root/'sppr/core/data/pr_site_text_blocks.jsonl.gz','rt') as stream:
        pr_blocks = [json.loads(line) for line in stream]
    sites = {}
    search = []
    for r in cross:
        s = r['site']
        if not s:
            continue
        key = ir[s]
        items = [i for i in ir_items if i['site']==s]
        ir_native = sum(bool(i['native_path']) for i in items)
        evidence = []
        for e in sr_evidence:
            if e['site']!=s:continue
            d=datasets[e['dataset_id']]
            evidence.append(dict(item=d['item_id'], id=d['dataset_id'], title=sr[d['chapter']]['title'],
                                 chapter=d['chapter'], count=e['records_including_site'], source=e['source'], url=sr[d['chapter']]['url']))
            search.append([s,d['dataset_id'],d['description'] + ' · ' + sr[d['chapter']]['title'],'SR',sr[d['chapter']]['url']])
        owned_notes=[n for n in notes if n['item_id']==f'PR.OPS.{s}' or (r['proposed_site'] and n['item_id']==f'SP.S.{r["proposed_site"]}')]
        diffs=[d for d in comparisons if d['site']==s and d['status']!='same_numeric_value']
        ci=Counter(v['comparison'] for v in carbon_editions if v['site']==s)
        optical={k['role']:k['file'] for k in split if k['core_id'].startswith(s)}
        station_crows=[[c[k] for k in carbon_fields] for c in carbon_rows if c['site']==s]
        assert len(station_crows)==int(carbon[s]['source_rows'])
        assert sum(bool(c[5]) for c in station_crows)==int(carbon[s]['with_org_c'])
        for i in items:
            search.append([s,i['item_id'],i['title'] or i['kind'],'IR',key['url'] + '#page='+i['pdf_page'] if i['pdf_page'] else key['url']])
        for p in src('sppr/core/data/pr_site_figures.csv'):
            if p['site']==s:search.append([s,p['item_id'],p['role']+' · '+p['graphic_role'],'PR',p['source_url']])
        sites[s]=dict(cross=r, ir=key, ir_count=len(items), ir_native=ir_native, pr=total[s],
                      repeat=repeats[s],
                      repeat_rows=[[v['sample_row_id'],v['sample_label'],v['run_1_carbonate_pct'],
                                    v['run_2_carbonate_pct'],v['run_3_carbonate_pct'],
                                    v['published_absolute_difference_pct'],v['row_kind']]
                                   for v in repeat_samples if v['site']==s],
                      carbon=carbon[s], strand=strands[s], plates=plate[s], splice=splice[s],
                      profiles=profiles[s], sr=evidence, notes=owned_notes, diffs=diffs, comparison=ci,
                      optical=optical, holes=[h['hole'] for h in holes if h['site']==s],
                      carbon_rows=station_crows,
                      pr_blocks=[[b['section'], b['pdf_page'], b['page_fragment'], b['source_url']]
                                 for b in pr_blocks if b['site']==s])
    proposals={r['proposed_site']:dict(card=cards[r['proposed_site']],cross=r) for r in cross if r['proposed_site']}
    docs=local('documents.csv')
    for d in docs:
        if d['series'] in ('SP','PR','SR','IR') and d['role'] not in ('site_chapter',):
            search.append([d['site'],d['doc_id'],d['title'],d['series'],d['url']])
    data_object = dict(sites=sites, proposals=proposals, search=search, carbon_fields=carbon_fields,
                       positions=json.loads((data/'modern_positions.geojson').read_text())['features'],
                       coast=json.loads((data/'modern_coast.json').read_text())['lines'])
    expedition=build_portal(root,output.parent)
    data_object['portal_keys']=[[tab,row[0],row[2]] for tab,entries in expedition.items() for row in entries]
    template = Path(__file__).with_name('browser_template.html').read_text()
    payload=json.dumps(data_object,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    output.write_text(template.replace('@DATA@',payload),encoding='utf-8')


carbon_fields = ('hole','sample','depth_mbsf','depth_mcd','published_organic_c','organic_c_pct','footnote_marker',
                 'footnote_role','source_item','source_line','source_url')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path,help='archive root containing module/core directories')
    parser.add_argument('--data',type=Path,help='integration data directory')
    parser.add_argument('--output',type=Path,help='path to browse.html')
    args=parser.parse_args()
    data=args.data or (args.root/'data' if (args.root/'data/carbon_coverage.csv').exists()
                       else args.root/'integration/core/data')
    build(args.root,data,args.output or data.parent/'browse.html')
