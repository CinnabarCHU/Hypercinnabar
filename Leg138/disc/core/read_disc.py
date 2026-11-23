"""Stream a source file as CSV, retaining source line numbers. Standard library only.
Example: python read_disc.py PRIMARY SITE_849/CHEM/CARBON.849 > site849.csv
"""
import argparse,csv,hashlib,re,sys
from pathlib import Path
SAMPLE=['leg','site','hole','core','core_type','section','top_cm','bottom_cm','mbsf']
ID_POS=((0,4),(7,11),(12,13),(14,17),(18,19),(20,22),(23,28),(29,34),(35,42))
def sample(line):return [line[a:b].strip() for a,b in ID_POS]
def classification(path):
    p=Path(path);n=p.name;cat=p.parent.name
    if n=='YMTRANS.TBL':return 'filesystem_map','documentation','disc_name_translation'
    if n.startswith('README') or cat=='READ_DIR':return 'documentation','documentation','distribution_or_tool_documentation'
    if cat=='PROGRAMS':return 'fortran_source' if p.suffix=='.F' else 'fortran_include','software','shipboard_workflow_source'
    if cat=='COREDATA':
        if p.suffix=='.ADJ':return 'core_offsets','derived','reported_mbsf_mcd_core_offsets'
        if n.startswith('DEPTH'):return 'first_grape_depth','derived','first_grape_sample_depth_conversion'
        return 'core_sections','operational_record','reported_core_and_cut_section_lengths'
    if cat.startswith('SITE_'):
        typ=n.split('.')[0];return {'AGE':('age_lowres','age_model','low_resolution_published_mcd_age'),'MCD_AGE':('age_mcd','age_model','high_resolution_grape_event_mcd_age'),'MBSF_AGE':('age_mbsf','age_model','high_resolution_grape_event_mbsf_age'),'MBSF':('depth_transform','derived','shipboard_mcd_to_mbsf_control_points'),'SPLICE':('splice','derived','prescribed_hole_switches_in_mcd')}[n.split('.')[0]]
    if p.suffix=='.REF':return 'spectra_511','calibrated_observation','published_reflectance_percent_511_channels'
    if cat=='COLOR':
        if n=='COL844B.FIN':return 'color_binary','undecoded_binary','archived_binary_with_embedded_labels_no_assigned_numeric_schema'
        if p.suffix=='.TEN':return 'color_ten','processed_measurement','ten_50_nm_mean_bands'
        return 'color_three','processed_measurement','three_published_bands_and_depth_fields'
    if cat=='GRAPE':
        if p.suffix=='.DAT':return 'grape_dat','reported_measurement','released_density_with_repeated_readings_and_two_integer_channels'
        if p.suffix=='.FIN':return 'grape_fin','processed_measurement','replicates_averaged_density_correction_smoothing_mcd'
        if p.suffix=='.MCD':return 'grape_mcd','derived','spliced_density_on_mcd_with_source_sample'
        if p.suffix=='.MBS':return 'grape_mbs','derived','spliced_density_rescaled_to_mbsf'
    if cat=='SUS':
        return ('sus_mcd','derived','spliced_susceptibility_on_mcd') if p.suffix=='.MCD' else ('sus_fin','processed_measurement','published_susceptibility_with_composite_depth')
    if cat=='CHEM':
        return ('carbon','reported_lab_product','released_carbon_table_with_empty_fields') if p.stem=='CARBON' else ('interstitial','reported_lab_product','interstitial_water_results_mixed_layout')
    if cat=='PP':return p.stem.lower(),'reported_lab_product','published_physical_property_table'
    if cat=='LOGS':return 'logs','reported_logging_product','logging_tool_channels_or_processing_products_see_per_file_header'
    return 'other','unclassified','see_original'
def fixed(line,start,width,n):return [line[start+i*width:start+(i+1)*width].strip() for i in range(n)]
def layout(path):
    typ=classification(path)[0];p=Path(path)
    std={'grape_dat':['record_flag','density_g_cm3','integer_1','integer_2'],'grape_fin':['mcd','density_g_cm3','corrected_density_g_cm3','smooth_corrected_density_g_cm3'],'sus_fin':['susceptibility_instrument_units','additional_integer_as_printed','mcd','additional_depth_field_m'],'color_three':['blue_450_500_pct','red_650_700_pct','infrared_850_900_pct','mcd','mcd_minus_mbsf'],'color_ten':['sensor_offset']+[f'R_{x}_{x+50}_pct' for x in range(450,950,50)],'spectra_511':['sensor_offset']+[f'pixel_{i}_pct' for i in range(1,512)],
    'carbon':['mcd','total_carbon_pct','inorganic_carbon_pct','carbonate_pct','organic_carbon_pct','nitrogen_pct'],
    'index':['mcd','wet_bulk_density_g_cm3','dry_bulk_density_g_cm3','grain_density_g_cm3','porosity_pct','wet_water_content_pct','dry_water_content_pct','void_ratio'],
    'compvel':['mcd','compressional_wave_velocity_m_s'],'thermcon':['mcd','thermal_conductivity_W_m_K'],'vaneshea':['mcd','vane_shear_strength_kPa']}
    if typ=='color_binary':return ['byte_offset','bytes_hex']
    if typ=='compvel' and p.name=='COMPVEL.844':return ['mbsf','corrected_velocity_m_s']
    basics={'age_lowres':['mcd','age_Ma','source_comment'],'age_mcd':['mcd','age_Ma'],'age_mbsf':['mbsf','age_Ma'],'depth_transform':['mcd','mbsf'],'splice':['mcd_start','hole_number'],
    'core_offsets':['site','hole','core','core_type','top_mbsf','bottom_mbsf','core_length_m','top_mcd','bottom_mcd','offset_m'],'first_grape_depth':['leg','site','hole','core','core_type','first_grape_mbsf','first_grape_mcd','offset_m'],
    'core_sections':['site','hole','core','core_type','top_mbsf']+[f'section_{i}_cm' for i in range(1,10)]+['core_catcher_cm'],
    'grape_mcd':['mcd','density_g_cm3','smoothed_density_g_cm3']+SAMPLE[1:],
    'grape_mbs':['rescaled_mbsf','density_g_cm3','smoothed_density_g_cm3','mcd'],
    'sus_mcd':['mcd','susceptibility_instrument_units']+SAMPLE[1:]}
    return SAMPLE+std[typ] if typ in std else basics.get(typ,['source_text'])
def data_rows(file,path=None):
    relative=path or file.as_posix();name=Path(relative).name;typ=classification(relative)[0];columns=layout(relative)
    seen_ref=False
    if typ=='color_binary':
        with file.open('rb') as stream:
            offset=0
            while data:=stream.read(256):
                yield '', 'binary_block', [offset,data.hex()]
                offset+=len(data)
        return
    with file.open(encoding='latin1') as f:
        for n,raw in enumerate(f,1):
            line=raw.rstrip('\r\n')
            if columns==['source_text']:
                yield n,'source_text',[line];continue
            if not line.strip():continue
            if typ=='spectra_511':
                if line.strip()=='START OF DATA':seen_ref=True;continue
                if line.strip()=='END OF DATA':seen_ref=False;continue
                if not seen_ref:continue
            if typ in ('compvel','thermcon','vaneshea','index','carbon') and n<=3:continue
            if typ=='core_offsets' and not re.match(r'^\s*8\d\d\s',line):continue
            if columns[:2]==['leg','site'] and typ!='first_grape_depth':
                if not re.match(r'^\s*\d{3}\b' if typ=='spectra_511' else r'^\s*138\b',line):
                    yield n,'unparsed_line',[line];continue
                ident=sample(line)
                if typ in ('spectra_511','color_ten'):
                    number=511 if typ=='spectra_511' else 10
                    tail=[line[42:45].strip()]+fixed(line,45,6,number)
                    ok=not line[45+number*6:].strip() and all(x for x in tail[1:])
                elif typ=='grape_dat':
                    tail=[line[a:b].strip() for a,b in ((42,43),(43,51),(51,59),(59,64))];ok=not line[64:].strip()
                elif typ=='sus_fin':
                    if name=='SUS845AX.FIN':tail=[line[a:b].strip() for a,b in ((42,50),(50,55),(55,62),(62,69))];ok=not line[69:].strip()
                    else:tail=[line[42:50].strip(),'',line[50:57].strip(),line[57:64].strip()];ok=not line[64:].strip()
                elif typ in ('index','compvel','thermcon','vaneshea','carbon','grape_fin'):
                    tail=fixed(line,42,7,len(columns)-9);ok=not line[42+7*len(tail):].strip()
                else:
                    tail=line[42:].split();ok=len(tail)==len(columns)-9
                vals=ident+tail
            elif typ=='age_lowres':
                v=line.strip().split(None,2);vals=(v+['']) if len(v)==2 else v
                ok=len(vals)==3 and all(re.fullmatch(r'[-+]?\d*\.?\d+',x) for x in vals[:2])
            elif typ=='core_offsets':
                vals=line.split();ok=len(vals) in (7,10)
                if len(vals)==7:vals+=['','','']
            elif typ=='core_sections':
                m=re.match(r'^\s*(\d{3})([A-E])\s+(\d+)([A-Z])\s+top:\s*([-.\d]+)\s+sec lengths:',line)
                ok=bool(m) and not line[75:].strip()
                vals=[*m.groups(),*fixed(line,35,4,9),line[71:75].strip()] if m else []
            else:
                vals=line.split();ok=len(vals)==len(columns)
            if not ok or len(vals)!=len(columns):
                yield n,'unparsed_line',[line]
            else:yield n,'data',vals
def cli():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('primary',type=Path);ap.add_argument('path');ap.add_argument('--fetch',action='store_true');ap.add_argument('--skip-hash',action='store_true');args=ap.parse_args()
    source_file=Path(__file__).with_name('sources.csv')
    with source_file.open() as inp:r=next((row for row in csv.DictReader(inp) if row['path']==args.path),None)
    if r is None:ap.error('Path not found in official release manifest')
    file=args.primary/args.path
    if args.fetch and not file.is_file():
        from urllib.request import urlopen
        import tempfile,os
        file.parent.mkdir(parents=True,exist_ok=True)
        with urlopen(r['url'],timeout=75) as stream:data=stream.read()
        if hashlib.sha256(data).hexdigest()!=r['sha256']:raise IOError('Source checksum differs')
        with tempfile.NamedTemporaryFile(dir=file.parent,delete=False) as temp:temp.write(data)
        os.replace(temp.name,file)
    if not args.skip_hash and hashlib.sha256(file.read_bytes()).hexdigest()!=r['sha256']:raise IOError('Source checksum differs')
    w=csv.writer(sys.stdout);cols=layout(args.path);w.writerow(['source_path','source_line','row_status',*cols,'unparsed_source_text'])
    for n,status,v in data_rows(file,args.path):
        w.writerow([args.path,n,status,*([*v,''] if status!='unparsed_line' else ['']*len(cols)+v)])
if __name__=='__main__':cli()
