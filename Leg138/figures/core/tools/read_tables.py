"""Build interval and source-row transcriptions for the eleven Leg 138 initial-report chapters."""
from pathlib import Path
import argparse, csv, hashlib, re
from bisect import bisect_right
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
TABLES=[(12,16,38,47,156,165),(10,14,41,47,229,235),(8,12,31,40,295,304),(8,12,23,34,357,368),(9,16,39,52,715,728),(8,12,38,48,772,782),(10,15,31,42,839,850),(10,14,41,43,931,933),(11,15,23,37,989,1003),(8,12,22,30,1044,1052),(7,11,19,26,1081,1088)]
FIELDS=['mean_carbonate_pct','mean_organic_carbon_pct','sedimentation_rate','dry_bulk_density','bulk_mar','carbonate_mar','noncarbonate_mar','organic_carbon_mar']
EXT='https://www-odp.tamu.edu/publications/138_IR/'
def save(name,rows):
    with (DATA/name).open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
def parselines(raw):
    return raw.decode('latin-1').expandtabs().splitlines()
def numprefix(s):
    result=[]
    for token in s.split():
        if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)?',token):break
        result.append(token)
    return result
def decode_values(numbers,site,lineno,source_line):
    if site==853:
        # Table 12's rightmost token can be either Corg MAR or non-carbonate MAR.
        # Use the published fixed columns, independently of the count of populated cells.
        # Line 59 starts its final token at character 87. The print page confirms Corg.
        starts=(16,26,35,45,55,66,76,86)
        result=dict.fromkeys(FIELDS,'')
        for token in re.finditer(r'\S+',source_line):
            slot=bisect_right(starts,token.start())-1
            if slot<0 or result[FIELDS[slot]]:
                raise ValueError((site,lineno,token.start()))
            result[FIELDS[slot]]=token.group()
        return result
    if len(numbers)==8:keys=FIELDS
    elif len(numbers)==6:keys=[FIELDS[i] for i in [0,2,3,4,5,6]]
    elif len(numbers)==1:keys=[FIELDS[2]]
    elif site==854 and len(numbers)==3:keys=[FIELDS[i] for i in [0,2,3]]
    else:raise ValueError((site,lineno,numbers))
    d=dict.fromkeys(FIELDS,'');d.update(zip(keys,numbers,strict=True));return d
def parse_control(raw,site,num):
    result=[];lookup={}
    for n,s in enumerate(parselines(raw),1):
        nums=numprefix(s)
        if not nums:continue
        if len(nums)==1:
            kind='interstitial_rate';depth=age='';rate=nums[0]
        elif len(nums) in (2,3):
            kind='control_horizon';depth=nums[0];age=nums[-1];rate=nums[1] if len(nums)==3 else ''
            lookup[float(age)]=(depth,n)
        else:raise ValueError((site,n,nums))
        result.append(dict(site=site,ir_table=num,source_line=n,row_role=kind,depth_m_as_published=depth,age_Ma=age,rate_as_printed_on_row=rate,source_line_text=s.rstrip()))
    return result,lookup
def parse_mean(raw,site,num,controls):
    points=[];intervals=[];source=[]
    previous=None;pending=None
    for n,s in enumerate(parselines(raw),1):
        vals=numprefix(s)
        if not vals:continue
        source.append(dict(site=site,ir_table=num,source_line=n,source_line_text=s.rstrip()))
        if site in (848,850,851,852):
            point=(vals[0],vals[1],n)
            if len(vals)>2:
                if previous is None:
                    assert float(vals[1])>0 and 0 in controls
                    previous=(controls[0][0],'0',0)
                intervals.append((previous,point,n,decode_values(vals[2:],site,n,s)))
            previous=point;points.append(point)
        elif site==845:
            # Print table (p.235) places these values on the same line as the interval-ending horizon.
            # The distribution breaks each printed row into two lines and omits the 0-Ma core top.
            if len(vals)==2:
                point=(vals[0],vals[1],n);points.append(point)
            else:
                if previous is None:previous=(controls[0][0],'0',0)
                intervals.append((previous,point,n,decode_values(vals,site,n,s)));previous=point
        else:
            if len(vals)==2:
                point=(vals[0],vals[1],n);points.append(point)
                if previous is not None:
                    assert pending is not None,(site,n)
                    intervals.append((previous,point,*pending));pending=None
                previous=point
            else:
                assert pending is None,(site,n)
                pending=n,decode_values(vals,site,n,s)
    assert pending is None
    returned=[]
    for a,b,ln,values in intervals:
        ca=controls.get(float(a[1]));cb=controls.get(float(b[1]));cd=''
        if ca and cb:
            cd=f'{(float(cb[0])-float(ca[0]))/(float(b[1])-float(a[1])):.5f}'
        assert float(b[1])>float(a[1])
        returned.append(dict(site=site,ir_table=num,young_Ma=a[1],old_Ma=b[1],depth_top_m_as_published=a[0],depth_base_m_as_published=b[0],top_source_line=a[2] or '',base_source_line=b[2],values_source_line=ln,zero_top_from_control_table='yes' if not a[2] else 'no',control_depth_top_m=ca[0] if ca else '',control_depth_base_m=cb[0] if cb else '',control_top_source_line=ca[1] if ca else '',control_base_source_line=cb[1] if cb else '',control_endpoint_slope_m_Myr=cd,**values))
    return returned,source
def build(ir):
    all_rows=[];all_src=[];all_ctrl=[];manifest=[]
    for j,(control,mean,cp,mp,cpr,mpr) in enumerate(TABLES):
        site,chap=j+844,j+9
        base='VOLUME/DATA/TABLES/CHAP_'+str(chap)+'/'
        m=''
        for number,role,ip,ipp in [(control,'age_control',cp,cpr),(mean,'interval_mean',mp,mpr)]:
            rel=base+f'TABLE.{number}';raw=(ir/rel).read_bytes();sha=hashlib.sha256(raw).hexdigest()
            manifest.append(dict(site=site,ir_chapter=chap,ir_table=number,role=role,ir_pdf_page=ip,ir_print_page=ipp,distribution_path=rel,source_url=EXT+rel,sha256=sha,bytes=len(raw)))
            if role=='age_control':
                ctrl,lookup=parse_control(raw,site,number);all_ctrl+=ctrl
            else:
                rows,src=parse_mean(raw,site,number,lookup);all_rows+=rows;all_src+=src
    save('ir_interval_witnesses.csv',manifest);save('ir_mean_intervals.csv',all_rows);save('ir_mean_source_rows.csv',all_src);save('ir_control_source_rows.csv',all_ctrl)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('ir_primary',type=Path);build(p.parse_args().ir_primary)
