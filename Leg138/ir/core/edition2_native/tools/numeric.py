"""Decode the report tables with numeric columns, retaining source strings and anchor lines."""
import re
from statistics import median

# Column sequences are in original electronic order; blank cells keep their slot.
PORE='depth_mbsf pH salinity chloride sodium alkalinity sulfate magnesium calcium potassium strontium lithium silica ammonia'.split()
MEANS='composite_depth age_ma mean_CaCO3 mean_Corg sedimentation_rate mean_DBD bulk_MAR CaCO3_MAR non_CaCO3_MAR Corg_MAR'.split()
SPEC={
 'IR12.T13':'depth_mbsf depth_mcd total_C inorganic_C organic_C total_N methane',
 'IR13.T12':'depth_mbsf SiO2 TiO2 Al2O3 Fe2O3 MnO MgO CaO Na2O K2O P2O5 total LOI',
 'IR13.T13':'depth_mbsf CaO nonvolatile LOI hundred_minus_LOI Ca_unignited CaCO3_unignited CaCO3_measured',
 'IR13.T14':'depth_mbsf Al_bulk Si_bulk Ca_bulk Fe_bulk Mn_bulk Ti_bulk P_bulk CaCO3_estimate Al_CF Si_CF Fe_CF Mn_CF Ti_CF P_CF',
 'IR13.T15':'depth_mbsf depth_mcd age_ma bulk_MAR Al_MAR Fe_MAR Mn_MAR hydrothermal_Fe_MAR opal_MAR',
 'IR15.T12':'depth_mbsf depth_mcd SiO2 TiO2 Al2O3 Fe2O3 MnO CaO Na2O K2O P2O5 total LOI',
 'IR15.T13':'depth_mbsf depth_mcd SiO2_LOI Al2O3_LOI Fe2O3_LOI MnO_LOI CaO_LOI Na2O_LOI K2O_LOI P2O5_LOI CaCO3_measured CaCO3_estimated',
 'IR15.T14':'top_depth_mbsf midpoint_depth_mcd midpoint_age_Myr SiO2_MAR Al2O3_MAR Fe2O3_MAR MnO_MAR P2O5_MAR opal_MAR',
}
# The text and headers have different alignments in some of the split-line mean tables.
MEAN_CENTRES={9:[4,13,22,30,39,47,55,63,71,79],10:[4,13,22,30,39,48,57,68,79,90],12:[3,15,25,36,47,58,69,79,89,100],13:[3,14,24,34,44,54,63,72,81,90],14:[4,12,20,29,36,45,53,60,68,75],15:[4,13,22,30,38,47,54,62,69,78],16:[4,13,22,30,38,47,54,62,70,78],17:[4,15,26,38,50,61,71,82,93,104],18:[3,14,21,31,39,50,61,72,82,95],19:[4,13,23,34,45,55,66,77]}
SAMPLE=re.compile(r'^\s*(?:(?:138-)?\d{3}-?[A-E]-)?\d+[HXN]-(?:\d+|CC)')
HOLE_HEADER=re.compile(r'^\s*(?:(?:138-|-)?(\d{3})-?([A-E])-?|Hole\s+([A-E]))\s*$')
NUM=re.compile(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)$')

def tok(s):return list(re.finditer(r'\S+',s))
def centre(t):return (t.start()+t.end())/2
def fixed(tokens,names,centres,notes):
    if len(tokens)==len(names):return {k:t.group() for k,t in zip(names,tokens)}
    result={}
    for t in tokens:
        opts=sorted(range(len(names)),key=lambda i:abs(centre(t)-centres[i])); i=opts[0]
        if names[i] in result or abs(centre(t)-centres[i])>(abs(centres[opts[1]]-centres[i])/2+1):
            notes.append('overlapping_or_outlying_column');result['unresolved_source_fragment']=(result.get('unresolved_source_fragment','')+' '+t.group()).strip();continue
        result[names[i]]=t.group()
    return result

def decode(id,site,fam,ls,emit,mark):
    if fam in ('porewater','elemental','hydrocarbon'):
        names=SPEC.get(id,'depth_mbsf methane').split() if fam!='porewater' else PORE[:(-1 if id in ['IR09.T13','IR13.T10'] else None)]
        coreonly=id=='IR13.T15';prefix=1 if coreonly else 2;hole='';references=[]
        for line in ls:
            tt=tok(line)
            if SAMPLE.match(line) and len(tt)==len(names)+prefix:references.append([centre(t) for t in tt[prefix:]])
        assert references,id
        centres=[median(col) for col in zip(*references)]
        for i,s in enumerate(ls,1):
            if m:=HOLE_HEADER.fullmatch(s):hole=(m[1] or str(site))+(m[2] or m[3]);mark(i,'hole_heading');continue
            if not SAMPLE.match(s) and not (coreonly and (re.match(r'^\s*\d+\.',s) or i==18)):continue
            tokens=tok(s);data={};notes=[]
            if SAMPLE.match(s) or (coreonly and i==18):
                label=tokens[0].group();data['core_section']=label
                h=re.search(r'(\d{3})-?([A-E])-',label)
                if h:hole=h[1]+h[2]
                else:
                    if not hole:notes.append('hole_not_stated_in_source')
                if not coreonly or (coreonly and i in (21,23)):
                    data['interval_cm']=tokens[1].group();tokens=tokens[2:]
                else:tokens=tokens[1:]
                if coreonly and i==18:
                    data['core_section']=label;hole='';notes.append('source_core_label_truncated')
            data['reported_hole']=hole
            data.update(fixed(tokens,names,centres,notes));emit(i,data,notes)
        return ['reported_hole','core_section','interval_cm']+names
    if fam in ('sediment_means','cross_site'):
        names=(MEANS if site!=854 else [x for x in MEANS if x not in ('mean_Corg','Corg_MAR')]) if fam=='sediment_means' else ['mean_age_ma']+[f'site_{s}_sedimentation_rate' for s in range(846,854)]
        centres=MEAN_CENTRES[int(id[2:4])] if fam=='sediment_means' else [2.2,14,25,36,47,58,69,80,91]
        for i,s in enumerate(ls,1):
            tt=tok(s)
            if not tt or not NUM.fullmatch(tt[0].group()):continue
            notes=[];d=fixed(tt,names,centres,notes)
            if (id,i)==('IR18.T12',59):
                notes.append('Corg_MAR_verified_in_print_at_0.14_noncarbonate_MAR_blank')
            if (id,i)==('IR13.T16',40):notes.append('column_positions_shift_relative_to_print_and_adjacent_intervals; preserve electronic positions')
            if id=='IR06.T02' and not d.get('mean_age_ma'):notes.append('age_absent_in_electronic_source')
            if fam=='sediment_means':d['row_kind']='interval_and_boundary' if d.get('composite_depth') and len(d)>2 else ('boundary' if d.get('composite_depth') else 'interval_parameters')
            emit(i,d,notes)
        return (['row_kind'] if fam=='sediment_means' else [])+names
    if fam=='reflectors':
        names='traveltime_s synthetic_depth_m depth_mbsf depth_mcd age_ma'.split();last='';label_line=''
        for i,s in enumerate(ls,1):
            a=s.split();notes=[]
            if not a or not (NUM.fullmatch(a[0]) or re.match(r'^R\d|^(?:Chert|Basement)$',a[0],re.I)):continue
            if not NUM.fullmatch(a[0]):label=a.pop(0);last=label;label_line=i
            else:label=''
            assert len(a)<=len(names),(id,i,s)
            d=dict(zip(names,a));d.update(reflector_label_as_written=label,reflector_group_context=last,reflector_group_source_line=label_line);emit(i,d,notes)
        return ['reflector_label_as_written','reflector_group_context','reflector_group_source_line']+names
    if fam=='age_control':
        # IR10.T10 explicitly labels the middle column Age and the right column Rate;
        # retain those labels even though the chapter's interpretation and print order differ.
        names=['composite_depth','sedimentation_rate','age_ma'] if id!='IR10.T10' else ['composite_depth','age_ma_as_header','rate_as_header']
        for i,s in enumerate(ls,1):
            a=tok(s)
            if not a or not NUM.fullmatch(a[0].group()):continue
            vals=[]
            for t in a:
                if NUM.fullmatch(t.group()) and len(vals)<3:vals.append(t)
                else:break
            notes=[];k=[0,1,2] if len(vals)==3 else ([0,2] if len(vals)==2 else [1]);d={names[j]:v.group() for j,v in zip(k,vals)}
            if id=='IR10.T10' and len(vals)==2:d={names[0]:vals[0].group(),names[1]:vals[1].group()};
            d['remarks']=s[vals[-1].end():].strip()
            if id=='IR10.T10':notes.append('native_age_and_rate_headers_order_differs_from_chapter_interpretation')
            emit(i,d,notes)
        return names+['remarks']
    raise ValueError(fam)
