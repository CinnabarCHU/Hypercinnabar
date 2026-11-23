"""Build the dataset directory and validate release evidence, exact source-line roundtrips and coverage."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,gzip,hashlib,json,shutil,re
from native import C,P,ROOT,write,ident,member
def rows(path):
 with path.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
def main():
 dirs=[];links=[];cov=defaultdict(set)
 def add(id,keys,scope,path,cnt,rep,desc):
  dirs.append([id,'|'.join(keys),scope,path,cnt,rep,desc])
  for key in keys:links.append([id,key]);cov[key].add(rep)
 native=rows(C/'native_tables.csv')
 for v in native:
  add(v['item_id']+'.native',[v['item_id']],v['site'] or 'cross-site','native_lines.csv.gz',v['line_count'],'source_lines_and_token_positions','All distributed lines, including headers and notes; filter by item_id. Character positions are zero-based, end exclusive.')
 desc={'coring':'Original individual-core rows and separately labelled source-group totals. Printed calendar header, zero-prefixed UTC and native recovery retained.', 'carbons':'Publication-level carbon values. Blank or absent columns, flagged values and source sample spellings retained. For this family, Site 854 does not publish a Corg column.', 'core_depths':'Each reported core depth interval in mbsf and mcd, length and composite offset. The latter quantities are published correlation products.', 'index_properties':'Published moisture and density properties; units copied in physical_table_headers.csv; no silent repair of the electronic headers.', 'compressional_velocity':'Published velocity profile; native headers distinguish methods, scales and any correction.', 'vane_shear_strength':'Published vane shear profile; retain source hole as written or empty when absent in the distributed file.', 'thermal_conductivity':'Published conductivity profile. Source header gives units, original identifiers and depth scale.'}
 for f in sorted((C/'tables').glob('*.csv')):
  data=rows(f);ks=sorted({v['item_id'] for v in data})
  add('IR.'+f.stem,ks,'Leg 138',str(f.relative_to(C)),len(data),'named_fields_from_distributed_tables',desc[f.stem])
 repeats=rows(C/'carbonate_repeat_sources.csv');rk=[v['item_id'] for v in repeats]
 add('IR.carbonate_repeat_sources',rk,'Leg 138','carbonate_repeat_sources.csv',len(repeats),'evidence_directory','One row per numbered carbonate replicate table, with selected witness and explicit role of the chapter-page locator.')
 for fname,desc_text in [('samples','Reported per-sample run columns, printed absolute difference and the separately labelled mean-difference row.'),('runs','One record per First/Second/Third run as explicitly presented in the source table. The run ID is scoped to the published table row.')]:
  path=f'carbonate_repeat_{fname}.csv';rr=rows(C/path)
  add('IR.carbonate_repeat_'+fname,rk,'Leg 138',path,len(rr),'named_fields_mixed_witness_per_table',desc_text+' Per-site evidence in carbonate_repeat_sources.csv.')
 for f in sorted((C/'print_tables').glob('*.csv')):
  ch,n=re.search(r'IR(\d+)_T(\d+)',f.name).groups();id=ident(int(ch),'T',int(n))
  add(id+'.print',[id],str(835+int(ch)) if int(ch)>=9 else 'cross-site',str(f.relative_to(C)),len(rows(f)),'scan_collated_print_transcription','Printed-table witness only; row order and original blanks retained. Not a reconstructed copy of the missing online ASCII.')
 legacy_folder=C/'site846_prior'; legacy_folder.mkdir(exist_ok=True)
 legacy=ROOT.parent/'previous/ir'
 if (legacy/'data/tables').exists():
  for p in (legacy/'data/tables').glob('table-*.csv'):shutil.copyfile(p,legacy_folder/p.name)
  for name in ['editorial_note','item','location','item_source','section','dataset','print-checks']:
   p=legacy/f'metadata/{name}.csv'
   if p.exists():shutil.copyfile(p,legacy_folder/p.name)
  write(C/'site846_prior_bridge.csv',['pilot_item_id','global_item_id','pilot_status','pilot_title','pilot_section'],[[v['item_id'],ident(11,'T' if v['kind']=='table' else 'F',int(v['number'])),v['available'],v['title'],v['section_id']] for v in rows(legacy/'metadata/item.csv') if v['kind'] in ('table','figure') and v['number'].isdigit()])
 for p in sorted(legacy_folder.glob('table-*.csv')):
  n=int(p.stem[6:]);id=ident(11,'T',n);typ='site846_previous_print_transcription' if n in [2,11,19,21] else 'site846_previous_native_table'
  add(id+'.pilot',[id],'846',str(p.relative_to(C)),len(rows(p)),typ,'Site 846 previously collated field edition, kept as a separate witness in the same form as the original pilot. See site846_prior/item.csv and editorial_note.csv.')
 write(C/'datasets.csv',['dataset_id','source_items','scope','data_path','row_count','representation','description'],dirs)
 write(C/'dataset_items.csv',['dataset_id','item_id'],links)
 items=rows(C/'chapter_items.csv'); ids={r['item_id'] for r in items};assert len(ids)==len(items)
 assert all(id in ids for _,id in links)
 candidates=rows(C/'disc_list_collation.csv');absents={r['item_id'] for r in candidates if not r['native_path']};assert absents=={'IR06.T01','IR06.T03','IR06.T04','IR12.T06'}
 status=[]
 for r in items:
  if r['kind']!='table':continue
  k=r['item_id'];has_native=bool(r['native_path']);named=bool(cov[k]-{'source_lines_and_token_positions'})
  status.append([k,r['chapter'],r['site'],r['number'],int(has_native),int(named),'|'.join(sorted(cov[k])) or 'index_only'])
 write(C/'table_coverage.csv',['item_id','chapter','site','table_number','native_online','has_named_fields_in_ir_package','representations'],status)
 manifest=rows(C/'sources.csv');assert len(manifest)==229
 for s in manifest:
  b=(P/s['path']).read_bytes();assert len(b)==int(s['bytes']) and hashlib.sha256(b).hexdigest()==s['sha256'],s
 with gzip.open(C/'native_lines.csv.gz','rt',newline='',encoding='utf8') as f:
  lines=defaultdict(bytearray);cnt=Counter()
  for v in csv.DictReader(f):
   path=v['source_path']; assert int(v['line_number'])==cnt[path]+1;cnt[path]+=1
   t=v['raw_text'];b=t.encode('latin1');lines[path]+=b+{'CRLF':b'\r\n','LF':b'\n','CR':b'\r','none':b''}[v['line_ending']]
   for a,e,token in json.loads(v['tokens_with_positions']):assert t[a:e]==token
  for n in native:assert lines[n['source_path']]==(P/n['source_path']).read_bytes()
 assert sum(cnt.values())==17835 and len(cnt)==179
 stat=Counter(v['kind'] for v in items);chap=rows(C/'chapters.csv');assert len(chap)==20
 assert len([v for v in items if v['site']=='846'])==73
 if (C/'site846_prior_bridge.csv').is_file():assert {v['global_item_id'] for v in rows(C/'site846_prior_bridge.csv')}=={v['item_id'] for v in items if v['site']=='846'}
 cc=rows(C/'tables/carbons.csv');cores=rows(C/'tables/coring.csv')
 allsite=set(str(i) for i in range(844,855))
 assert {r['site'] for r in cc}==allsite and {r['site'] for r in cores}==allsite
 if (legacy_folder/'table-10.csv').is_file():
  earlier={r['source_line']:r for r in rows(legacy_folder/'table-10.csv') if r['row_kind']=='data'}
  rechecked={r['source_line']:r for r in cc if r['site']=='846'}
  assert earlier.keys()==rechecked.keys()
  for key,row in earlier.items():
   r=rechecked[key]
   for k1,k2 in [('depth_mbsf','depth_mbsf'),('depth_mcd','depth_mcd'),('total_carbon_pct','total_c_pct'),('inorganic_carbon_pct','inorganic_c_pct'),('carbonate_pct','carbonate_pct'),('organic_carbon_pct','organic_c_pct'),('nitrogen_pct','nitrogen_pct')]:assert r[k2]==row[k1],(key,k1,r[k2],row[k1])
 counts={'sources':len(manifest),'sources_bytes':sum(int(r['bytes']) for r in manifest),'chapter_pdfs':len(chap),'chapter_pdf_pages':sum(int(r['pdf_pages']) for r in chap),'figures':stat['figure'],'tables':stat['table'],'online_disc_tables':len(native),'listed_disc_tables':len(candidates),'recovered_print_tables_with_absent_disc_file':sorted(absents),'native_lines_exactly_reassembled':sum(cnt.values()),'table_numbers_with_named_data_in_this_module':sum(r[5] for r in status),'other_numbered_tables_without_named_fields_here':sum(not r[5] for r in status),'coring_by_row_kind':dict(Counter(r['row_kind'] for r in cores)),'carbon_sample_rows':len(cc),'carbon_rows_with_reported_corg':sum(bool(r['organic_c_pct']) for r in cc),'physical_named_rows':{f:len(rows(C/f'tables/{f}.csv')) for f in ('index_properties','compressional_velocity','vane_shear_strength','thermal_conductivity')}}
 repeatrows=rows(C/'carbonate_repeat_samples.csv');runs=rows(C/'carbonate_repeat_runs.csv')
 assert len(repeats)==11 and len(repeatrows)==329 and len(runs)==645
 sm={row['sample_row_id']:row for row in repeatrows};assert len(sm)==329
 for run in runs:assert sm[run['sample_row_id']][f"run_{run['published_run_number']}_carbonate_pct"]==run['carbonate_pct']
 assert len({v['run_record_id'] for v in runs})==645
 counts.update({'carbonate_repeat_sample_rows':318,'carbonate_individual_published_runs':645,'carbonate_repeat_table_mean_rows':11,'named_core_depth_interval_rows':len(rows(C/'tables/core_depths.csv'))})
 (C/'verification.json').write_text(json.dumps(counts,indent=2,ensure_ascii=False)+'\n');print(json.dumps(counts))
if __name__=='__main__':main()
