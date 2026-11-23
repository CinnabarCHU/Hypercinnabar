"""Critical transcriptions checked against publisher page images. Table-specific columns preserve layout."""
from pathlib import Path
import csv
E=Path(__file__).resolve().parents[1];C=E.parent
CH={int(v['chapter']):v for v in csv.DictReader((C/'chapters.csv').open())}
metas=[]
def put(ch,num,pdf,headers,rows,role,note):
    doc=CH[ch];folio=int(doc['print_page_first'])+pdf-1;item=f'SR.C{ch:02d}.TABLE{num}';file=f'print/{item}.csv'
    with (E/file).open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['source_pdf_page','source_print_page','table_row']+headers)
        for i,x in enumerate(rows,1):
            assert len(x)==len(headers),(item,x)
            w.writerow([pdf,folio,i]+x)
    metas.append([item+'.PRINT.E2',item,ch,doc['source'],pdf,folio,file,len(rows),role,note])
def toks(t):return [r.split() for r in t.splitlines() if r.strip()]
def run():
    put(1,1,8,['printed_site_group','pole_latitude_as_printed','pole_longitude_as_printed','rotation_degrees_per_Ma','time_applicable_Ma'],[
      ['84|495|503|844|845','16.8°N','115.9°W','−1.336','0 to 5'],
      ['84|495|503|844|845','19.1°N','108.5°W','−2.052','5 to 19'],
      ['677|846|847','41.9°N','99.0°W','−0.47','0 to 5'],
      ['677|846|847','40.1°N','93.3°W','−0.916','5 to 19'],
      ['848|849|850|851|852|853|854','61.6°N','82.5°W','0.97','0 to 5'],
      ['848|849|850|851|852|853|854','70.3°N','70.3°W','0.73','5 to 11']],
      'historical_rotation_model_parameters','Three visual row groups, two intervals per group. Includes legacy sites 84, 495, 503 and 677. No extrapolation beyond each interval.')
    put(3,3,10,['site','depth_range_mcd','mean_number_of_measurements_per_2_cm_bin'],toks('''846 0–287 1.90
847 0–148 2.47
848 0–50 2.61
849 0–123 2.25
850 0–87 1.60
851 0–89 1.42
852 0–128 2.87'''),'computed_count_summary','Native chapter 3 data files store depth transforms. This publication reports the mean count per 2-cm bin.')
    put(3,4,11,['site','event_depth_rmcd','GRAPE_as_printed','N','standard_deviation'],toks('''846 145.27 1.621 4 0.031
847 117.41 1.571 5 0.011
848 36.60 1.409 4 0.015
849 101.47 1.605 4 0.016
850 76.16 1.533 2 0.008
851 69.12 1.463 2 0.041
852 41.72 1.367 4 0.025'''),'computed_stack_summary','Event F across seven sites. N and standard deviation are separate published statistics.')
    rates=toks('''shipboard 846 33.2 15.0–51.5 5.5 61.3
shipboard 847 36.7 21.7–51.7 15.5 66.7
shipboard 848 12.2 6.3–18.1 5.2 21.2
shipboard 849 41.9 21.5–62.3 25.8 75.5
shipboard 850 33.3 16.3–50.3 18.0 64.2
shipboard 851 26.2 15.8–36.6 18.8 48.1
shipboard 852 14.1 10.3–17.9 9.1 20.6
predicted 846 28.9 8.9–81.7 1.4 674.3
predicted 847 34.2 14.8–77.2 3.9 335.2
predicted 848 11.1 4.2–25.9 1.7 84.8
predicted 849 39.9 14.9–94.4 8.6 377.5
predicted 850 31.1 11.0–76.2 6.0 194.5
predicted 851 23.8 10.2–55.4 3.8 240.5
predicted 852 12.8 6.6–28.4 3.0 147.1
tuned 846 41.0 25.5–56.5 11.4 121.2
tuned 847 35.3 19.5–51.1 11.9 124.9
tuned 848 10.4 5.0–15.8 1.9 36.4
tuned 849 36.2 11.9–60.5 9.0 199.9
tuned 850 28.5 7.5–49.5 6.9 210.0
tuned 851 22.4 10.1–34.7 7.9 72.2
tuned 852 12.3 7.5–17.1 4.8 31.5''')
    put(3,6,15,['printed_panel','site','mean_rate','plus_minus_one_sd_range','minimum_rate','maximum_rate'],rates,'published_summary_and_predictions','Three panels. Units mcd/m.y. Note a: 0–5 m.y. only for Sites 847–852. Note c relates the middle panel spread to D in Table 5.')
    put(4,1,5,['site','depth_log_m','correlation_before','correlation_after','average_number_Fourier_coefficients'],toks('''846 75–230 0.67 0.93 15.0
846 244–340 0.83 0.86 12.3
847 64–231 0.44 0.82 8.7
849 149–335 0.70 0.85 13.8
850 70–206 0.47 0.78 12.6
850 206–346 0.79 0.86 13.7
851 74–253 0.52 0.80 11.2'''),'computed_comparison','Correlations between GRAPE and logging observations, before and after mapping. Repeated sites represent distinct depth windows.')
    put(36,1,2,['characteristic_as_printed','column1_Site844','column2_Site844','column3_Site846'],[
      ['Water depth (m)','3400','3300','3800'],['Latitude (°N)','7.55','3.57','2.46'],['Longitude (°W)','90.28','90.49','110.34'],
      ['Transect','Eastern','Eastern','Western'],['Age to basement (Ma)','17','18.8','12.4'],['Sediment thickness (mcd)','310','450','390'],
      ['CaCO₃ (%)','5–70','30–70','70–80'],['Sedimentation rate (m/m.y.)','5–45','10–60','15–55'],['Age range of samples used in this study (Ma)','6.8–17','0–18','0–12.4']],
      'site_characteristics_printed_with_conflicting_headers','Table headings actually read 844, 844, 846. Abstract (leaf 1) and Methods (leaf 2) specify 844, 846 and 851. Preserve printed headers; those narrative site identities are a separate editorial interpretation.')
    rows=toks('''844 17.5 0.70900 0.70860 125
845 17 0.70915 0.70865 94
846 17 0.70894 0.70870 162
847 7 0.70905 0.70894 188
848 11 0.70914 0.70885 91
849 10.5 0.70907 0.70886 94
850 11–12 0.70914 0.70882 92
851 11 0.70908 0.70885 102
852 10 0.70915 0.70888 92
853 7–10 0.70913 0.70894 86
854 9–10 0.70906 0.70891 88''')
    rows+=[['Average','','0.70910','','98'],['Modern seawater','','0.70916','','90']]
    put(41,3,7,['source_row_label','age_Ma','Sr87_Sr86_measured_nearest_basement','Sr87_Sr86_seawater_of_basement_age','Sr_nearest_basement_uM'],rows,'measured_ratios_and_author_comparisons','Average and modern seawater are two separately labelled summary/reference rows. Unit µM is stated in the column header as well as these source cells.')
    with (E/'data/print_datasets.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow('dataset_id item_id chapter source pdf_page print_page file records role editorial_note'.split());w.writerows(metas)
    print(len(metas),sum(q[7] for q in metas))
if __name__=='__main__':run()
