"""Build the site/family inventory and bounded physical/chemical CSV extracts from the hash manifest."""
from pathlib import Path
from collections import defaultdict,Counter
import argparse,csv,gzip,io,hashlib,re,sys,json,contextlib
from read_disc import layout,data_rows,classification
CORE=Path(__file__).resolve().parent
def writer(path,columns,stack):
    if path.suffix=='.gz':
        bf=stack.enter_context(path.open('wb'));gz=stack.enter_context(gzip.GzipFile(fileobj=bf,mode='wb',mtime=0));f=stack.enter_context(io.TextIOWrapper(gz,encoding='utf-8',newline=''))
    else:f=stack.enter_context(path.open('w',encoding='utf-8',newline=''))
    w=csv.writer(f,lineterminator='\n');w.writerow(columns);return w
def siteof(path):
    m=re.search(r'(?:SITE_|CORE|DEPTH|\b)(8[45]\d)',path)
    return m[1] if m else ''
def main():
    ap=argparse.ArgumentParser();ap.add_argument('primary',type=Path);ap.add_argument('--out',type=Path,default=CORE);a=ap.parse_args()
    primary=a.primary.resolve();out=a.out;out.mkdir(parents=True,exist_ok=True)
    source=list(csv.DictReader((out/'sources.csv').open()));family_stats=defaultdict(Counter);site_stats=defaultdict(Counter)
    with contextlib.ExitStack() as stack:
        summ=writer(out/'file_index.csv.gz',['path','site','family','record_role','description','bytes','sha256','physical_lines','data_rows','unparsed_rows','text_rows','header_note'],stack)
        spec=writer(out/'spectrum_files.csv.gz',['site','path','sha256','rows','unparsed_rows','closed_end_marker','rows_with_leg_or_site_different_from_directory','acquisition_header','calibration_header','historic_raw_name'],stack)
        bad=writer(out/'parse_exceptions.csv.gz',['path','source_line','unparsed_source_text'],stack)
        sourceheaders=writer(out/'ascii_headers.csv.gz',['path','source_line','header_text'],stack)
        sources_out={}
        series={'carbon':'carbon','index':'physical_index','compvel':'compressional_velocity','thermcon':'thermal_conductivity','vaneshea':'vane_shear','core_offsets':'core_offsets','core_sections':'core_sections','first_grape_depth':'first_grape_depth'}
        for entry in source:
            name=entry['path'];p=primary/name;site=siteof(name);typ,role,desc=classification(name);cols=layout(name);meta=site_stats[site];fc=family_stats[(site,typ)]
            meta['files']+=1;meta['bytes']+=int(entry['bytes']);fc['files']+=1;fc['bytes']+=int(entry['bytes'])
            c=Counter();header_note=''
            with p.open(encoding='latin1') as f:lines=f.read().splitlines()
            if typ=='color_binary':
                header_note='Binary object with embedded labels, numeric records not decoded. File retained unchanged.'
            elif typ=='spectra_511':
                # The fixed-width fields are six characters each, following the sample and sensor offsets.
                # Data delimiters and payload field count are checked for every row; source bytes stay accessible.
                headers=lines[:4];data=False
                for idx,line in enumerate(lines,1):
                    if line.strip()=='START OF DATA':data=True;continue
                    if line.strip()=='END OF DATA':data=False;continue
                    if not data:continue
                    if not line[:4].strip().isdigit() or len(line.rstrip())!=45+511*6 or len(line[45:].split())!=511:
                        bad.writerow([name,idx,line]);c['unparsed_line']+=1
                    else:
                        c['data']+=1
                        c['id_diff']+=line[:4].strip()!='138' or line[7:11].strip().lstrip('0')!=site
                source_name=re.search(r'(\S+\.raw)\b',headers[0],re.I)
                spec.writerow([site,name,entry['sha256'],c['data'],c['unparsed_line'],not data,c['id_diff'],headers[0].strip(),headers[1].strip(),source_name.group(1) if source_name else ''])
                meta['spectrum_files']+=1;meta['spectrum_rows']+=c['data'];header_note='Calibration and historical acquisition filename in spectrum_files.csv.gz.' + (' Original file ends without END OF DATA marker.' if data else '')
            else:
                if typ in ('interstitial','logs','carbon','index','compvel','vaneshea','thermcon','core_offsets'):
                    # The first three rows, even when one is blank, preserve the native column layout for these families.
                    nhead=1 if typ=='core_offsets' else 3
                    for j,line in enumerate(lines[:nhead],1):sourceheaders.writerow([name,j,line])
                    header_note='See first source lines in ascii_headers.csv.gz and full original.'
                for n,status,values in data_rows(p,name):
                    c[status]+=1
                    if status=='unparsed_line':
                        bad.writerow([name,n,values[0]]);continue
                    if status!='data':continue
                    group=series.get(typ)
                    if group=='compressional_velocity' and site=='844':group='compressional_velocity_site844'
                    if group:
                        if group not in sources_out:sources_out[group]=writer(out/(group+'.csv.gz'),['source_path','source_line',*cols],stack)
                        sources_out[group].writerow([name,n,*values])
                    elif typ.startswith('age_'):
                        if 'age_models' not in sources_out:sources_out['age_models']=writer(out/'age_models.csv.gz',['source_path','source_line','site','source_series','printed_depth','depth_scale','age_Ma','source_comment'],stack)
                        sources_out['age_models'].writerow([name,n,site,typ,values[0],cols[0],values[1],values[2] if len(values)>2 else ''])
                    elif typ in ('splice','depth_transform'):
                        if typ not in sources_out:sources_out[typ]=writer(out/(typ+'.csv.gz'),['source_path','source_line','site',*cols],stack)
                        sources_out[typ].writerow([name,n,site,*values])
                    if typ=='carbon':
                        meta['carbon_rows']+=1
                        meta['reported_corg_rows']+=bool(values[cols.index('organic_carbon_pct')])
                    if typ=='grape_dat':meta['grape_dat_rows']+=1
                if typ=='grape_dat':meta['grape_dat_holes']+=1
                if typ=='core_sections':meta['core_section_files']+=1
                if typ=='logs':meta['log_files']+=1
            fc['data']+=c['data'];fc['unparsed_line']+=c['unparsed_line'];fc['text_rows']+=c['source_text']
            summ.writerow([name,site,typ,role,desc,entry['bytes'],entry['sha256'],len(lines) if typ!='color_binary' else '',c['data'] if typ!='color_binary' else '',c['unparsed_line'],c['source_text'],header_note])
        fields=['files','bytes','carbon_rows','reported_corg_rows','grape_dat_holes','grape_dat_rows','core_section_files','log_files','spectrum_files','spectrum_rows']
        w=writer(out/'site_summary.csv',['site',*fields],stack)
        for site,co in sorted(site_stats.items()):
            if site:w.writerow([site,*[co[k] for k in fields]])
        w=writer(out/'family_summary.csv',['site','family','files','bytes','data_rows','unparsed_lines','source_text_lines'],stack)
        for (site,typ),co in sorted(family_stats.items()):w.writerow([site,typ,*[co[k] for k in ('files','bytes','data','unparsed_line','text_rows')]])
    print('Files',len(source),'bytes',sum(int(r['bytes']) for r in source),'unparsed lines',sum(c['unparsed_line'] for c in family_stats.values()))
if __name__=='__main__':main()
