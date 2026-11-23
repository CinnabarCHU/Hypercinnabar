"""Generate modern position views. Keep published coordinates and editorial display assumptions."""
import argparse,csv,json,hashlib,re
from pathlib import Path
from urllib.request import urlopen
COAST='https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_coastline.geojson'
def deg(s):
    m=re.fullmatch(r"(\d+)°\s*(\d+(?:\.\d+)?)\s*['′]?\s*([NSEW])",s.strip())
    if m is None:raise ValueError(s)
    return round((int(m[1])+float(m[2])/60)*(-1 if m[3] in 'SW' else 1),8)
def build(root,out,cache):
    if cache and cache.exists():b=cache.read_bytes()
    else:
        with urlopen(COAST,timeout=60) as f:b=f.read()
    # Preserve segment vertices inside the displayed map; a wider crop avoids edge effects.
    bounds=[-115,-8,-78,17];lines=[]
    for ft in json.loads(b)['features']:
        g=ft['geometry'];parts=g['coordinates'] if g['type']=='MultiLineString' else [g['coordinates']]
        for part in parts:
            group=[]
            for x,y,*_ in part:
                if bounds[0]<=x<=bounds[2] and bounds[1]<=y<=bounds[3]:group.append([round(x,4),round(y,4)])
                elif group:
                    if len(group)>1:lines.append(group)
                    group=[]
            if len(group)>1:lines.append(group)
    (out/'modern_coast.json').write_text(json.dumps(dict(source=COAST,source_sha256=hashlib.sha256(b).hexdigest(),bounds=bounds,lines=lines),separators=(',',':')))
    features=[]
    sp=root/'sppr/core/data'
    def collect(file,typ,key):
        for r in csv.DictReader((sp/file).open()):
            if typ=='PR' and r['row_kind']!='hole':continue
            url=('https://www-odp.tamu.edu/publications/prosp/digital/138prosp.pdf#page=8' if typ=='SP' else 'https://www-odp.tamu.edu/publications/prelim/138PREL.PDF#page='+r['pdf_page'])
            features.append(dict(type='Feature',geometry=dict(type='Point',coordinates=[deg(r['longitude']),deg(r['latitude'])]),properties=dict(record=r[key],stage=typ,kind='planned_site' if typ=='SP' else 'occupied_hole',source_site=r[key] if typ=='SP' else r['site'],latitude_as_published=r['latitude'],longitude_as_published=r['longitude'],published_horizontal_datum=None,display_assumption='plotted as geographic degrees without datum transformation',source_url=url)))
    collect('sp_time.csv','SP','proposed_site');collect('pr_coring.csv','PR','hole')
    assert len(features)==54
    (out/'modern_positions.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=features),ensure_ascii=False,separators=(',',':')))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('out',type=Path);p.add_argument('--coast-cache',type=Path);a=p.parse_args();build(a.root,a.out,a.coast_cache)
