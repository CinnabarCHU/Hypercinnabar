from pathlib import Path
import csv
HERE=Path(__file__).resolve().parents[1]; CORE=HERE.parent; PRIMARY=CORE.parent/'primary'
def readcsv(f):
 with f.open(encoding='utf8',newline='') as stream:return list(csv.DictReader(stream))
items={r['item_id']:r for r in readcsv(CORE/'chapter_items.csv')}
TARGET={r['item_id']:items[r['item_id']] for r in readcsv(CORE/'table_coverage.csv') if r['native_online']=='1' and r['has_named_fields_in_ir_package']=='0'}
def family(r):
 t=r['title'].lower();item=r['item_id']
 if 'constraints' in t:return 'fossils'
 if 'reversal' in t:return 'reversals'
 if 'control points' in t:return 'age_control'
 if 'interstitial' in t:return 'porewater'
 if 'average' in t:return 'sediment_means'
 if 'traveltimes' in t:return 'reflectors'
 if 'methane' in t:return 'hydrocarbon'
 if item.startswith('IR06.'):return 'cross_site'
 return 'elemental'
