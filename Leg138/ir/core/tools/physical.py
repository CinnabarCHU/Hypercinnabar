"""Decode the distributed physical properties tables and preserve unit/header anomalies per file."""
from native import P,C,member,ident,write
import re
NUMBER=[[17,18,19,20],[16,17,18,19],[15,16,17,18],[14,15,16,17],[20,21,22,23],[14,15,17,16],[19,20,21,22],[16,17,18,19],[16,17,18,19],[13,14,16,15],[12,None,13,14]]
KINDS=['index_properties','compressional_velocity','vane_shear_strength','thermal_conductivity']
VALS=['wet_bulk_density','dry_bulk_density','grain_density','porosity','wet_water_content','dry_water_content','void_ratio']
SAMPLE=re.compile(r'^\s*(?:(?:138-)?\d{3}-?[A-E]-?)?\d+[A-Z]+[-]?(?:\d|CC)')
HOLE=re.compile(r'(?<!\d)(\d{3})-?([A-E])')
def build():
 dat={k:[] for k in KINDS};headers=[]
 base=['item_id','site','source_path','source_line','reported_hole','sample_label','depth_mbsf','depth_mcd','second_depth_unlabelled']
 for ch,nums in enumerate(NUMBER,9):
  for k,n in enumerate(nums):
   if n is None:continue
   kind=KINDS[k];path=member(ch,n);id=ident(ch,'T',n);rows=dat[kind];before=len(rows);hole='';first=None;ndepth=None;comments=[]
   lines=(P/path).read_text(encoding='latin1').splitlines()
   for ln,s in enumerate(lines,1):
    if not s.strip():continue
    velocity_only=(ch,k)==(9,1) and re.match(r'^\s*[-.+]?\d+(\.\d+)?\s+[-.+]?\d+',s)
    if not SAMPLE.match(s) and not velocity_only:
     if m:=HOLE.search(s):
      if len(s.strip())<25 or ('+' in s and '846C' in s):hole=''.join(m.groups())
     continue
    if first is None:first=ln
    a=s.split()
    if velocity_only:
     samp='';values=a
    else:
     samp=' '.join(a[:2]);values=a[2:]
     if m:=HOLE.search(a[0]):hole=''.join(m.groups())
    following=None
    if (ch,n)==(9,17) and len(a)==11:
     following=HOLE.fullmatch(values[-1].strip('-').split('-')[-1])
     assert following is not None;values=values[:-1];comments.append('CHAP_9/TABLE.17 contains the next hole header at the end of the last B-hole row.')
    nv=7 if k==0 else 1; dep=len(values)-nv
    assert dep in (1,2) and (ndepth is None or ndepth==dep),(ch,n,ln,s,ndepth)
    ndepth=dep
    for v in values:
     if not re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)',v):comments.append(f'Line {ln} retains nonnumeric spelling {v!r}.')
    unknown_second=dep==2 and (ch,n)==(10,16)
    rows.append([id,ch+835,path,ln,hole,samp,values[0],values[1] if dep==2 and not unknown_second else '',values[1] if unknown_second else '',*values[dep:]])
    if following:hole=''.join(following.groups())
   assert first is not None
   if (ch,n)==(10,16):comments.append('The source has two numerical depth columns but labels only the first in the electronic header. The second column remains unassigned.')
   if (ch,n)==(19,12):comments.append('The distributed units label dry-bulk and grain density as g/cm2. No unit correction or conversion is applied.')
   if (ch,n)==(9,19):comments.append('Distributed header reads 138-884B-; this string is retained although the report chapter is Site 844.')
   if (ch,n)==(9,18):comments.append('Only depth and corrected velocity are present in this two-column table.')
   headers.append([id,ch+835,kind,path,first,len(rows)-before,' | '.join(s.rstrip() for s in lines[:first-1]),' '.join(comments)])
 for k,rows in dat.items():
  write(C/f'tables/{k}.csv',base+(VALS if k=='index_properties' else [k]),rows)
 write(C/'physical_table_headers.csv',['item_id','site','family','source_path','first_data_line','row_count','source_header_and_first_context','editorial_note'],headers)
 return {k:len(v) for k,v in dat.items()}
if __name__=='__main__':print(build())
