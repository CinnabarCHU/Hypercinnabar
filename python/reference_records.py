"""Prepare site-level observations on the authors' chronology for panel 8."""
import argparse
import io
import urllib.request
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
from scipy.interpolate import interp1d

def table(number, cache):
    path=cache/f'PANGAEA.{number}.tab'
    if not path.exists():
        url=f'https://doi.pangaea.de/10.1594/PANGAEA.{number}?format=textfile'
        with urllib.request.urlopen(url) as response:
            path.write_bytes(response.read())
    rows=path.read_text(encoding='utf-8-sig').split('*/',1)[1].strip().splitlines()
    return [line.split('\t') for line in rows[1:]]

def numeric(rows, columns):
    values=[]
    for row in rows:
        try: values.append([float(row[i]) for i in columns])
        except (ValueError,IndexError): continue
    return np.array(values)

def prepare(kt_workbook,cache,output):
    boundaries=table(783353,cache)
    series=[]
    for group,identifier,depth_column,anchor_column,carbon_column in [
        (1,763141,4,2,5),(3,756583,2,1,5)]:
        tie=numeric(boundaries,[anchor_column,3])
        age=interp1d(tie[:,0],tie[:,1]/1000,fill_value='extrapolate')
        obs=numeric(table(identifier,cache),[depth_column,carbon_column])
        series.extend(np.c_[np.full(len(obs),group),age(obs[:,0]),obs[:,1]])
    # Site 1258 bulk, using the Option 1 ages supplied by Kirtland Turner et al.
    sheet=load_workbook(kt_workbook,data_only=True,read_only=True).active
    bulk=numeric([[str(x) for x in row] for row in list(sheet.values)[4:]],[11,12])
    series.extend(np.c_[np.full(len(bulk),2),bulk[:,0]/1000,bulk[:,1]])
    series=np.asarray(series);series=series[np.lexsort((series[:,1],series[:,0]))]
    np.savetxt(output/'kt2014_observations.csv',series,delimiter=',',fmt=['%d','%.8f','%.5f'],
               header='site_record,age_Ma_option1,carbon_permil',comments='')
    obs=[]
    for row in table(883334,cache):
        try: t=float(row[3])/1000
        except ValueError: continue
        # Prefer Nuttallides when both taxa were analysed. W18 Table 1
        # converts Oridorsalis to the Nuttallides scale.
        if row[4]: y=float(row[4])
        elif row[6]: y=(float(row[6])+.37)/.97
        else: continue
        obs.append((t,y))
    np.savetxt(output/'w2018_1209.csv',sorted(obs),delimiter=',',fmt='%.8f',
               header='age_Ma,Nuttallides_scale_carbon_permil',comments='')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('kirtland_supplementary_table',type=Path)
    parser.add_argument('--cache',type=Path,default=Path('.sources/pangaea'))
    parser.add_argument('--output',type=Path,default=Path('data'))
    args=parser.parse_args();args.cache.mkdir(exist_ok=True,parents=True)
    prepare(args.kirtland_supplementary_table,args.cache,args.output)
