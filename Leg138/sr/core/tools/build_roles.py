"""Describe the evidence role of source fields without imposing measurement equivalence across papers."""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
def role(item,field):
    if field in {'leg','site','hole','core','core_type','section','top_cm','bottom_cm','sample','analysis_id','species','sample_label_as_printed','laboratory_id','event_id','datum','fossil_group','anomaly','event_name','source_label','opal_source','limit_type'}:
        return 'identifier_or_source_description'
    if field=='depth_mbsf':return 'published_drilling_reference_depth'
    if field in {'depth_mcd','depth_rmcd','depth_offset_m'} or (field.startswith('site') and field.endswith('_mcd')):return 'transformed_or_published_composite_depth'
    if item=='SR.C15.TABLE7' and field in {'d18o','d13c'}:return 'interpolated_series'
    if item=='SR.C15.TABLE5' and field in {'d18o','d13c'}:return 'spliced_averaged_series'
    if field.endswith('_adjusted'):return 'author_adjusted_analysis_result'
    if field.endswith('_used'):return 'author_selected_analysis_result'
    if field in {'d18o_raw','d13c_raw','d18o','d13c','dry_over_150_g','dry_under_150_g'}:return 'published_analytical_value'
    if field in {'coarse_pct','lsr_cm_kyr','dbd_g_cm3','rate_m_per_myr','terrigenous_pct'} or field.endswith('_mar'):return 'author_derived_value'
    if field in {'abundance','preservation','etching','overgrowth'}:return 'author_semiquantitative_observation'
    if field in {'caco3_pct','opal_pct','benthic_d18o','benthic_d13c','planktonic_d18o','planktonic_d13c'}:return 'published_sample_property_source_dependent'
    if field.startswith('COH_'):return 'calculated_spectral_coherence'
    if field in {'SBP90','H91','CK92','Berggren_1985'}:return 'cited_author_chronology'
    if field=='mean':return 'author_summary_with_source_footnotes'
    if field.lower().startswith(('age','interval_','hole_')) or field=='this_study':return 'author_chronological_assignment_or_interval'
    raise ValueError((item,field))
if __name__=='__main__':
    with (ROOT/'datasets.csv').open() as data,(ROOT/'field_roles.csv').open('w',newline='') as output:
        rows=csv.DictReader(data);w=csv.writer(output)
        w.writerow(['dataset_id','item_id','field_order','field','descriptive_role'])
        for table in rows:
            for n,field in enumerate(json.loads(table['fields_json']),1):
                w.writerow([table['dataset_id'],table['item_id'],n,field,role(table['item_id'],field)])
