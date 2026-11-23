from native import C,P,member,ident,write
import re
TABLES=[11,9,7,7,8,7,9,9,10,7,6]
def decode():
 result=[];counts=[]
 for ch,n in enumerate(TABLES,9):
  before=len(result);hole='';path=member(ch,n)
  for ln,s in enumerate((P/path).read_text(encoding='latin1').splitlines(),1):
   c=re.search(r'(?<!\d)(\d{3})[-]?([A-E])',s)
   if c:hole=''.join(c.groups())
   a=s.strip().split()
   if not a or not re.fullmatch(r'(?:(?:138-)?\d{3}[A-E]-)?\d+[HXN]',a[0]):continue
   if len(a)==3:
    assert (ch,ln)==(17,20)
    a+=['','']
   assert len(a)==5 and hole,(ch,ln,s)
   result.append([ident(ch,'T',n),ch+835,path,ln,hole,*a])
  counts.append(len(result)-before)
 write(C/'tables/core_depths.csv',['item_id','site','source_path','source_line','reported_hole','core_label','depth_range_mbsf','core_length_m','depth_range_mcd','delta_m'],result)
 return len(result),counts
if __name__=='__main__':print(decode())
