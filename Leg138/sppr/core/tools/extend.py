"""Rebuild the Leg 138 SP/PR catalogue from the two PDF witnesses and previously verified volume tables."""
from pathlib import Path
from collections import defaultdict
import argparse,csv,hashlib,json,re,shutil,subprocess,math,gzip
ROOT=Path(__file__).resolve().parents[1]
SP_URL='https://www-odp.tamu.edu/publications/prosp/digital/138prosp.pdf'
PR_URL='https://www-odp.tamu.edu/publications/prelim/138PREL.PDF'
SHAS={'SP':'7934144bec5ec839c5a95c113cec9a266ac2ad5ef4b97b50cd44ffad3d534e37','PR':'48f7d7e22f672f499c38d610d995ad713874cfd01bc29516cf6b2f4cbe6d18c5'}
SITES=['WEQ-2','WEQ-3','WEQ-4','WEQ-5','WEQ-6','WEQ-7','EEQ-1','EEQ-2','EEQ-3','EEQ-4','EEQ-4A','EEQ-5']
PRE=['EEQ-2','EEQ-1','EEQ-4','EEQ-3','WEQ-5','WEQ-6',None,'WEQ-4','WEQ-3','WEQ-7','WEQ-2']
SCI=[7,9,11,13,16,17,18,21,22,23,25]
OPS=[80,81,83,85,87,89,90,92,94,95,97]
ONSITE=[80,81,83,85,87,89,91,92,94,95,97]
FIRST_FIG=[3,6,9,12,16,19,22,25,28,31,34]
DAT=ROOT/'data'
def save(name,rows):
    with (DAT/(name+'.csv')).open('w',newline='') as f:
        out=csv.DictWriter(f,fieldnames=list(rows[0]));out.writeheader();out.writerows(rows)
def read(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))
def norm(s):return ' '.join(s.split())
def link(doc,page):return (SP_URL if doc=='SP' else PR_URL)+f'#page={page}'
def event_iso(s):
    hit=re.search(r'(\d{2})(\d{2})Z (\d{2}) Sept\.? 1989',s)
    return f'1989-09-{hit[3]}T{hit[1]}:{hit[2]}Z' if hit else ''
def deg(s):
    d,m,axis=re.fullmatch(r'(\d+)°([\d.]+)′([NSEW])',s).groups()
    return (int(d)+float(m)/60)*(1 if axis in 'NE' else -1)
def distance(a,b):
    lat,lon,latb,lonb=map(math.radians,[a[0],a[1],b[0],b[1]])
    h=math.sin((latb-lat)/2)**2+math.cos(lat)*math.cos(latb)*math.sin((lonb-lon)/2)**2
    return 6371.0088*2*math.asin(math.sqrt(h))
def pdf_text(path):
    txt=subprocess.check_output(['pdftotext','-layout',str(path),'-']).decode().split('\f')
    assert not txt[-1].strip()
    return txt[:-1]
def card_fields(sp):
    cards=[]; fields=[]; events=[]
    roles={'SITE':'proposal_identifier','PRIORITY':'planning_rank','POSITION':'target_position','WATER DEPTH':'reported_survey_value','SEISMIC RECORD':'prior_geophysical_survey','Primary site':'survey_time_primary','Crossing':'survey_time_crossing','Secondary site':'survey_time_secondary','SEDIMENT RECORD':'prior_sediment_sampling','SEDIMENT THICKNESS':'interpreted_sediment_thickness','PROPOSED DRILLING PROGRAM':'planned_drilling','LOGGING':'planned_logging','OBJECTIVES':'scientific_context_and_plan','NATURE OF SEDIMENT/ROCKS ANTICIPATED':'anticipated_lithology'}
    for i,site in enumerate(SITES):
        n=14+3*i;text=sp[n-1]
        t=text[text.index('SITE:'):]
        m=re.search(r'POSITION:\s*(.+?)\s*WATER DEPTH:',t,re.S);position=norm(m[1]).replace("55.3fN","55.3'N")
        depth=norm(re.search(r'WATER DEPTH:\s*(.+?)\s*SEISMIC RECORD:',t,re.S)[1])
        survey=norm(re.search(r'SEISMIC RECORD:\s*(.*?)\s*SEDIMENT RECORD:',t,re.S)[1]).replace('station 6,0828Z','station 6, 0828Z')
        survey_parts=re.split(r'\s+(Primary site|Crossing|Secondary site)\s*:\s*',survey)
        station=survey_parts[0];sub=dict(zip(survey_parts[1::2],survey_parts[2::2]))
        sediment=norm(re.search(r'SEDIMENT RECORD:\s*(.*?)SEDIMENT THICKNESS:',t,re.S)[1])
        thick_str=norm(re.search(r'SEDIMENT THICKNESS:\s*(.+?)\s*PROPOSED DRILLING PROGRAM:',t,re.S)[1])
        if site=='WEQ-4':
            sediment+=' and VNTR01-06 PC'
            thick_str='312 m'
        drill=norm(re.search(r'PROPOSED DRILLING PROGRAM:\s*(.+?)\s*LOGGING:',t,re.S)[1])
        logging=norm(re.search(r'LOGGING:\s*(.+?)\s*OBJECTIVES:',t,re.S)[1])
        objective=norm(re.search(r'OBJECTIVES:\s*(.+?)\s*NATURE OF SEDIMENT/ROCKS ANTICIPATED:',t,re.S)[1])
        # The following letterforms, punctuation and line joins were compared with the scanned cards.
        replacements={14:{'is -27 m':'is ~27 m'},17:{'is -12.5 Ma':'is ~12.5 Ma'},20:{'crust -13 Ma':'crust ~13 Ma','is -312 m':'is ~312 m'},23:{'crust -10 Ma':'crust ~10 Ma','is -93 m':'is ~93 m'},35:{'Rise -18 Ma':'Rise ~18 Ma','(-300- 400':'(~300-400'},38:{'east-west- trending':'east-west-trending','northeast- southwest':'northeast-southwest','smooth basement The sediment':'smooth basement. The sediment'},41:{'(-25 m':'(~25 m'},47:{'~IO Ma':'~10 Ma'}}
        for old,new in replacements.get(n,{}).items():
            assert old in objective,(n,old);objective=objective.replace(old,new)
        lith=norm(t.split('NATURE OF SEDIMENT/ROCKS ANTICIPATED:')[1])
        priority=re.search(r'PRIORITY:\s*(\d+)',t)[1]
        values={'SITE':site,'PRIORITY':priority,'POSITION':position,'WATER DEPTH':depth,'SEISMIC RECORD':station,**sub,'SEDIMENT RECORD':sediment,'SEDIMENT THICKNESS':thick_str,'PROPOSED DRILLING PROGRAM':drill,'LOGGING':logging,'OBJECTIVES':objective,'NATURE OF SEDIMENT/ROCKS ANTICIPATED':lith}
        base=dict(item_id='SP.S.'+site,proposed_site=site,doc_id='SP',pdf_page=n,print_page=n+1,source_url=link('SP',n))
        fields.extend(dict(**base,field=k,semantic_role=roles[k],text_status='field_collated_against_scan',published_text=v) for k,v in values.items())
        cards.append(dict(**base,priority=priority,position_printed=position,water_depth_printed=depth,seismic_record=station,primary_site=sub.get('Primary site',''),crossing=sub.get('Crossing',''),secondary_site=sub.get('Secondary site',''),sediment_record=sediment,sediment_thickness_printed=thick_str,proposed_drilling_program=drill,logging=logging,objectives=objective,anticipated_sediment_rocks=lith,map_pdf_page=n+1,profile_pdf_page=n+2))
        if sub:
            for k,v in sub.items():events.append(dict(**base,printed_event_label=k,printed_time=v,iso_utc=event_iso(v),qualifier=''))
        else:
            assert event_iso(station)
            events.append(dict(**base,printed_event_label='SEISMIC RECORD',printed_time=re.search(r'\d{4}Z.+?1989',station)[0],iso_utc=event_iso(station),qualifier='analog seismic only' if 'analog seismic only' in station else ''))
    return cards,fields,events
def headings(pr):
    section=[];byhole={}
    for i,n in enumerate(SCI):
        site=str(844+i);lines=pr[n-1].splitlines()
        hits=[j for j,l in enumerate(lines) if re.match(rf'^Site {site} \((?:proposed|new site)',l.strip()) and len(l.strip())<55]
        assert len(hits)==1,(site,hits)
        sci_head=('Site '+site+' (proposed Site '+PRE[i]+')') if PRE[i] else 'Site 850 (new site)'
        section.append(dict(site=site,section='Scientific report',doc_id='PR',pdf_page=n,print_page=n+1,pdf_last=SCI[i+1] if i<10 else 26,start_line_in_layout=hits[0]+1,source_ocr_heading=lines[hits[0]].strip(),checked_heading=sci_head,source_url=link('PR',n)))
        page=OPS[i];ls=pr[page-1].splitlines();start=next(j for j,l in enumerate(ls) if l.strip().startswith('TRANSIT') and re.search(rf'TO SITE {site}',l.strip()))
        section.append(dict(site=site,section='Operations report including transit',doc_id='PR',pdf_page=page,print_page='' if page==80 else page+3,pdf_last=OPS[i+1] if i<10 else 97,start_line_in_layout=start+1,source_ocr_heading=ls[start].strip(),checked_heading=ls[start].strip(),source_url=link('PR',page)))
    for n in range(80,98):
        for i,l in enumerate(pr[n-1].splitlines()):
            if not re.match(r'^HOLES? ',l.strip()):continue
            normalized=re.sub(' +','',l.strip().split(' ',1)[1]).replace('85ID','851D').replace('85IE','851E')
            for hole in normalized.split('/'):
                assert re.fullmatch(r'8\d{2}[A-E]',hole),hole
                byhole[hole]=(n,i+1,l.strip())
    return section,byhole
def volume_release(primary,import_dir):
    dirs={k:primary/(k+'.pdf') for k in SHAS}
    for k,p in dirs.items():
        with p.open('rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest()==SHAS[k]
    sp,pr=(pdf_text(dirs[k]) for k in ['SP','PR'])
    assert (len(sp),len(pr))==(55,110)
    cache=import_dir/'data' if import_dir else DAT;cards,fields,events=card_fields(sp)
    save('sp_site_cards',cards);save('sp_card_fields',fields);save('sp_survey_times',events)
    section,byhole=headings(pr)
    save('pr_sections',section)
    for name in ['sp_time','sp_logging','sp_totals','sp_transit','pr_coring','pr_operations','pr_time_chart','pr_lab']:
        path=cache/(name+'.csv')
        if path.resolve()!=(DAT/path.name).resolve():shutil.copyfile(path,DAT/path.name)
    seed_items=cache/'items.csv' if (cache/'items.csv').exists() else cache/'report_items.csv'
    used=[r for r in read(seed_items) if r['doc_id'] in ('SP','PR')]
    figs=[r for r in used if r['kind']=='figure' and r['doc_id']=='PR']
    assert len(figs)==36
    for r in used:
        if r['item_id'].startswith('SP.S.'):r['status']='full_card_fields_collated'
    existing={r['item_id'] for r in used}
    for s in section:
        site=s['site'];id_=f'PR.{"SCI" if s["section"]=="Scientific report" else "OPS"}.{site}'
        if id_ not in existing:
            used.append(dict(item_id=id_,doc_id='PR',section=s['section'],title=s['checked_heading'],kind='text',pdf_first=s['pdf_page'],pdf_last=s['pdf_last'],scope='Site '+site,status='section_located',note='Boundary pages may also contain the preceding or following site.'))
    save('report_items',used)
    rawrows=read(cache/'pr_coring.csv');holes=[r for r in rawrows if r['row_kind']=='hole'];assert len(holes)==42
    holemap=[]
    for r in holes:
        n,line,raw=byhole[r['hole']]
        holemap.append(dict(site=r['site'],hole=r['hole'],proposed_site=PRE[int(r['site'])-844] or '',latitude_printed=r['latitude'],longitude_printed=r['longitude'],latitude_deg=f"{deg(r['latitude']):.8f}",longitude_deg=f"{deg(r['longitude']):.8f}",doc_id='PR',table_item='PR.T1',pdf_page=r['pdf_page'],row_locator=r['hole'],source_url=link('PR',r['pdf_page']),operations_pdf_page=n,operations_layout_line=line,operations_heading_ocr=raw,operations_url=link('PR',n)))
    save('site_holes',holemap)
    graph=[];finds={c['proposed_site']:c for c in cards};position={r['proposed_site']:r for r in read(cache/'sp_time.csv')}
    for i,p in enumerate(PRE):
        site=str(844+i);first=next(r for r in holemap if r['hole']==site+'A')
        c=finds[p] if p else {};t=position[p] if p else {}
        arc=distance(tuple(deg(t[k]) for k in ('latitude','longitude')),(float(first['latitude_deg']),float(first['longitude_deg']))) if p else None
        graph.append(dict(site=site,proposed_site=p or '',status='occupied_named_proposal' if p else 'added_during_leg',priority=c.get('priority',''),sp_pdf_page=c.get('pdf_page',''),sp_map_pdf_page=c.get('map_pdf_page',''),sp_profile_pdf_page=c.get('profile_pdf_page',''),pr_sci_pdf_page=SCI[i],pr_ops_site_pdf_page=ONSITE[i],pr_heading=section[i*2]['checked_heading'],reference_hole=first['hole'],pr_table_pdf_page=first['pdf_page'],candidate_latitude=t.get('latitude',''),candidate_longitude=t.get('longitude',''),hole_latitude=first['latitude_printed'],hole_longitude=first['longitude_printed'],great_circle_difference_km=f'{arc:.2f}' if arc is not None else '',source_url=link('PR',SCI[i]),sp_url=c.get('source_url',''),ops_url=link('PR',ONSITE[i])))
    for p in ['EEQ-4A','EEQ-5']:
        c=finds[p];t=position[p]
        graph.append(dict.fromkeys(graph[0],''))
        graph[-1].update(proposed_site=p,status='proposed_only_in_reviewed_leg',priority=c['priority'],sp_pdf_page=c['pdf_page'],sp_map_pdf_page=c['map_pdf_page'],sp_profile_pdf_page=c['profile_pdf_page'],candidate_latitude=t['latitude'],candidate_longitude=t['longitude'],source_url=c['source_url'],sp_url=c['source_url'])
    save('site_crosswalk',graph)
    roles=[]
    for i,n in enumerate(FIRST_FIG):
        site=str(844+i)
        for k,role in [(0,'multi-hole composite compilation'),(1,'published survey profile'),(2,'calculated chronological series')]:
            r=figs[n-1+k];source=''
            if k==1:source=('JOIDES Resolution, Leg 138 site survey' if site in ('850','854') else 'R/V Thomas Washington, VENTURE 01')
            roles.append(dict(site=site,item_id=r['item_id'],role=role,graphic_role='primary focus',doc_id='PR',pdf_page=r['pdf_first'],pdf_last=r['pdf_last'],acquisition_attribution=source,source_url=link('PR',r['pdf_first'])))
        paleo=figs[1 if i<4 else 14]
        roles.append(dict(site=site,item_id=paleo['item_id'],role='plate backtracking',graphic_role=('eastern site marked; ages printed for magnetic lineations' if i<4 else ('trajectory illustrated with labelled age ticks' if site=='851' else 'present location shown; path described as similar')),doc_id='PR',pdf_page=paleo['pdf_first'],pdf_last=paleo['pdf_last'],acquisition_attribution='interpreted reconstruction',source_url=link('PR',paleo['pdf_first'])))
    save('pr_site_figures',roles)
    with gzip.open(cache/'pages.jsonl.gz','rt') as z:pages=[json.loads(l) for l in z if l.strip()]
    with (DAT/'pages.jsonl.gz').open('wb') as f:
        with gzip.GzipFile(fileobj=f,mtime=0,mode='wb') as z:
            for r in pages:
                if r['doc_id'] in ('SP','PR'):z.write((json.dumps(r,ensure_ascii=False)+'\n').encode())
    docrows=[]
    for k,n in [('SP',55),('PR',110)]:
        docrows.append(dict(doc_id=k,pdf_pages=n,bytes=dirs[k].stat().st_size,sha256=SHAS[k],filename=k+'.pdf',url=link(k,1).split('#')[0]))
    save('source_manifest',docrows)
    report={'SP_pages':55,'PR_pages':110,'proposals':len(cards),'checked_published_card_fields':len(fields),'survey_time_entries':len(events),'actual_sites':sum(bool(r['site']) for r in graph),'holes':len(holes),'paired_precruise_sites':sum(r['status']=='occupied_named_proposal' for r in graph),'new_sites':1,'proposal_only':2,'source_index_items':len(used),'site_figure_relations':len(roles),'volume_numbered_scientific_figures':len(figs),'site_section_anchors':len(section)}
    (DAT/'coverage.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('primary',type=Path);parser.add_argument('previous_sppr_root',type=Path,nargs='?',help='Optional prior Site 846 catalogue for the initial import. In the release, certified volume tables are already present.')
    args=parser.parse_args();DAT.mkdir(parents=True,exist_ok=True);volume_release(args.primary,args.previous_sppr_root)
