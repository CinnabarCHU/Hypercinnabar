"""Replay the five Fortran programs on published GRAPE data. Run as python replay_grape.py PRIMARY OUT.
Compiler FC defaults to gfortran; FC_EXTRA_FLAGS can locate an unpacked compiler. Original sources stay intact.
"""
from pathlib import Path
import argparse,csv,hashlib,difflib,json,os,re,shlex,subprocess,tempfile
from collections import defaultdict
from decimal import Decimal
FLAGS=['-std=legacy','-ffixed-line-length-none','-fno-align-commons','-finit-local-zero','-O0']
def writecsv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def digest(data):return hashlib.sha256(data).hexdigest()
def compile_codes(disc,w,out):
    cc=os.environ.get('FC','gfortran');extra=shlex.split(os.environ.get('FC_EXTRA_FLAGS',''))
    version=subprocess.check_output([cc,'--version'],text=True).splitlines()[0]
    inputs=[]
    for p in sorted((disc/'PROGRAMS').glob('*')):
        if p.suffix not in ('.F','.INC'):continue
        s=p.read_text(encoding='latin1');m=s
        if p.name=='FIXGRAPE.F':m=m.replace('\tcharacter ahole\n','',1)
        elif p.name=='SPLICE.F':m=m.replace('      integer oleg','      real junk\n      integer oleg',1)
        elif p.name=='DEP_ADJ.F':m=m.replace("'/home/bligh/users/pisias/data/leg138.data/core.data/'","'./'")
        (w/p.name.lower()).write_text(m,encoding='latin1')
        if m!=s:(out/'patches'/f'{p.name}.diff').write_text(''.join(difflib.unified_diff(s.splitlines(True),m.splitlines(True),'original/'+p.name,'build/'+p.name.lower())))
        inputs.append(dict(original_file=p.name,source_sha256=digest(p.read_bytes()),build_source_lf_sha256=digest(m.encode('latin1'))))
    for src in sorted(w.glob('*.f')):
        z=subprocess.run([cc,*extra,*FLAGS,src.name,'-o',src.stem],cwd=w,text=True,capture_output=True,check=True)
    (out/'compiler.txt').write_text(version+'\n'+' '.join(FLAGS)+'\n')
    writecsv(out/'fortran_sources.csv',inputs)
def run(ex,w,answers):
    proc=subprocess.run([ex],cwd=w,input='\n'.join(answers)+'\n',text=True,capture_output=True,timeout=15)
    if proc.returncode:raise RuntimeError('exit '+str(proc.returncode)+' '+proc.stderr[-320:].replace('\n',' '))
def link(w,name,source):
    dest=w/name
    if not dest.exists():dest.symlink_to(source.resolve())
def values(lines,shape):
    vals=defaultdict(list)
    for i,line in enumerate(lines,1):
        if not line.strip():continue
        v=line.split()
        if shape=='fin':
            key=[line[a:b].strip() for a,b in ((0,4),(7,11),(12,13),(14,17),(18,19),(20,22),(23,28),(29,34),(35,42))]
            fields=[line[j:j+7].strip() for j in range(42,70,7)]
        else:fields,key=v[:3],v[3:]
        if len(fields)!=(4 if shape=='fin' else 3):raise ValueError(f'{shape} source line {i}: {line!r}')
        normalized=lambda x:re.sub(r'^0+([0-9])',r'\1',x) if x.isdigit() else x
        vals[tuple(normalized(x) for x in key)].append(tuple(Decimal(v) for v in fields))
    return {(key,i):fields for key,cs in vals.items() for i,fields in enumerate(cs)}
def subset(replay,ref,shape):
    a=values(replay,shape);b=values(ref,shape);ks=set(a)&set(b);cols=4 if shape=='fin' else 3
    return dict(replay_rows=len(a),published_rows=len(b),paired_occurrences=len(ks),equal_all_fields=sum(a[k]==b[k] for k in ks),equal_each_field=','.join(str(sum(a[k][ix]==b[k][ix] for k in ks)) for ix in range(cols)),replay_only=len(a)-len(ks),published_only=len(b)-len(ks))
def blankrow(site,scope,process,source,reference):
    return dict(site=site,hole=scope,process=process,input_path=source,reference_path=reference,status='',replay_rows='',published_rows='',paired_occurrences='',equal_all_fields='',equal_each_field='',replay_only='',published_only='',equal_text_lines='',normalized_sha256='',note='')
def process_site(disc,out,bin_dir,n):
    site=f'SITE_{n}';root=disc/site;groot=root/'GRAPE';rows=[]
    with tempfile.TemporaryDirectory() as d:
        w=Path(d);corr=w/'corr';corr.mkdir()
        for name,source in [(f'depths{n}.fin',disc/'COREDATA'/f'DEPTH{n}.FIN'),(f'splice.{n}',root/f'SPLICE.{n}'),(f'mbsf.{n}',root/f'MBSF.{n}'),(f'gr{n}.mcd',groot/f'GR{n}.MCD')]:link(w,name,source)
        reference=groot/f'GR{n}.MBS';row=blankrow(n,'','MBSFSPLI',f'{site}/GRAPE/GR{n}.MCD + {site}/MBSF.{n}',str(reference.relative_to(disc)))
        try:
            run(bin_dir/'mbsfspli',w,['0',str(n),f'mbsf.{n}'])
            produced=(w/f'gr{n}.mcd.mbs').read_bytes().replace(b'\r\n',b'\n')
            if not reference.is_file():
                row.update(status='generated_no_published_reference',replay_rows=len(produced.splitlines()),normalized_sha256=digest(produced),note='Program produced lines; the official directory does not list an MBS reference file for this site.')
                pub=None
            else:pub=reference.read_bytes().replace(b'\r\n',b'\n')
            if pub is not None:
                left=produced.splitlines();right=pub.splitlines()
                row.update(status='identical_lf_bytes' if produced==pub else 'differences_recorded',replay_rows=len(left),published_rows=len(right),equal_text_lines=sum(a==b for a,b in zip(left,right)),normalized_sha256=digest(produced),note='Byte comparison after CRLF→LF, original order; same coordinates required.')
        except Exception as e:row.update(status='failed',note=str(e)[:400])
        rows.append(row)
        holes=sorted(p.stem[-1] for p in groot.glob(f'GR{n}?.FIN'))
        successful=[]
        for h in holes:
            lower=h.lower();raw=groot/f'GR{n}{h}.DAT';ref=groot/f'GR{n}{h}.FIN'
            link(w,f'grfix_0{n}{lower}.dat',raw);link(w,f'gr{n}{lower}.fin',ref)
            row=blankrow(n,h,'FIXGRAPE → DEP_ADJ → GRAPECOR',str(raw.relative_to(disc)),str(ref.relative_to(disc)))
            try:
                run(bin_dir/'fixgrape',w,[str(n),lower,'0','0','1','y']);mod=w/f'grfix_0{n}{lower}.dat.mod'
                link(w,f'fix{lower}.dat',mod)
                run(bin_dir/'dep_adj',w,[f'fix{lower}.dat','16',str(n)])
                lines=(w/f'fix{lower}.adj').read_text().splitlines()
                (corr/f'gr{n}{lower}.fin').write_text(''.join(l[:58]+f'{Decimal(l[58:65]):10.2f}\n' for l in lines if l.strip()))
                successful.append((h,row))
            except Exception as e:row.update(status='failed',note=str(e)[:400])
            rows.append(row)
        try:
            run(bin_dir/'grapecor',corr,[str(n),str(len(holes))])
        except Exception as e:
            for h,row in successful:row.update(status='failed',note=str(e)[:400])
        for h,row in successful:
            if row['status']=='failed':continue
            try:
                produced=corr/f'gr{n}{h.lower()}.cor';pub=groot/f'GR{n}{h}.FIN'
                results=subset(produced.read_text().splitlines(),pub.read_text().splitlines(),'fin')
                eq=(results['equal_all_fields']==results['published_rows']==results['replay_rows'])
                row.update(results,status='identical_numeric_rows' if eq else 'differences_recorded',normalized_sha256=digest(produced.read_bytes().replace(b'\r\n',b'\n')),note='Four value fields in order: mcd, reported density, corrected density, smoothed corrected density. Duplicate sample IDs paired in file order.')
            except Exception as e:row.update(status='failed',note=str(e)[:400])
        row=blankrow(n,'','SPLICE',f'{site}/GRAPE/GR{n}<hole>.FIN + {site}/SPLICE.{n}',f'{site}/GRAPE/GR{n}.MCD')
        try:
            run(bin_dir/'splice',w,['0',str(n),str(len(holes)),f'splice.{n}']);produced=w/f'gr{n}.splice'
            results=subset(produced.read_text().splitlines(),(groot/f'GR{n}.MCD').read_text().splitlines(),'splice')
            eq=results['equal_all_fields']==results['published_rows']==results['replay_rows']
            row.update(results,status='identical_numeric_rows' if eq else 'differences_recorded',normalized_sha256=digest(produced.read_bytes().replace(b'\r\n',b'\n')),note='Compare only with stated distribution. SPLICE uses corrected FIN density; the README labels MCD as uncorrected density. Fields: MCD, density, smoothed density. Different processing stages can differ.')
        except Exception as e:row.update(status='failed',note=str(e)[:400])
        rows.append(row)
    return rows
def main():
    p=argparse.ArgumentParser();p.add_argument('primary',type=Path);p.add_argument('out',type=Path);p.add_argument('--sites',type=int,nargs='+',default=range(844,855));a=p.parse_args()
    disc=a.primary.resolve();out=a.out.resolve();(out/'patches').mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir=Path(tmp);compile_codes(disc,bin_dir,out);rows=[]
        for site in a.sites:rows+=process_site(disc,out,bin_dir,site)
    writecsv(out/'grape_replay.csv',rows)
if __name__=='__main__':main()
