"""Expand the chapter 1 print groups for machine queries without extrapolating the authors' stages."""
from pathlib import Path
import csv,re
E=Path(__file__).resolve().parents[1]
def run():
    with (E/'print/SR.C01.TABLE1.csv').open() as f:rows=list(csv.DictReader(f))
    with (E/'data/historical_rotation_stages.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['site','part_of_leg138','age_start_Ma','age_end_Ma','pole_latitude_deg_N','pole_longitude_deg_E','angular_rate_deg_per_Ma_as_signed_by_authors','source_table','print_row','pdf_page','print_page'])
        for r in rows:
            lat=re.fullmatch(r'([\d.]+)°N',r['pole_latitude_as_printed'])[1]
            lon=re.fullmatch(r'([\d.]+)°W',r['pole_longitude_as_printed'])[1]
            lo,hi=r['time_applicable_Ma'].split(' to ')
            for site in map(int,r['printed_site_group'].split('|')):
                w.writerow([site,int(844<=site<=854),lo,hi,lat,'-'+lon,r['rotation_degrees_per_Ma'].replace('−','-'),'SR.C01.TABLE1.PRINT.E2',r['table_row'],r['source_pdf_page'],r['source_print_page']])
if __name__=='__main__':run()
