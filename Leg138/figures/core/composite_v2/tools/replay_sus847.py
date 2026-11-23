"""Run the distributed splice source for Site 847 susceptibility, compare every published row, and record stage limits."""
from pathlib import Path
import csv,hashlib,os,shlex,shutil,subprocess,tempfile,argparse
from collect_tracks import save

def run(primary,compiler,flags):
    inputs=[primary/f'SITE_847/SUS/SUS847{x}.FIN' for x in 'ABCD'];pr=primary/'PROGRAMS';reference=primary/'SITE_847/SUS/SUS847.MCD'
    with tempfile.TemporaryDirectory() as tmp:
        w=Path(tmp)
        source=(pr/'SPLICE.F').read_text('latin1')
        # The old, implicitly integer dummy variable junk is read with an F descriptor in the GRAPE branch.
        source=source.replace('      integer oleg','      real junk\n      integer oleg',1)
        (w/'splice.f').write_text(source,encoding='latin1')
        (w/'splice.inc').write_bytes((pr/'SPLICE.INC').read_bytes())
        args=[compiler,*flags,'-ffixed-line-length-none','-fno-align-commons','-std=legacy','-finit-local-zero','-O0','splice.f','-o','splice']
        subprocess.run(args,cwd=w,check=True)
        for i in inputs:(w/i.name.lower()).symlink_to(i.resolve())
        (w/'splice.847').symlink_to((primary/'SITE_847/SPLICE.847').resolve())
        log=subprocess.run([str(w/'splice')],cwd=w,input='1\n847\n4\nsplice.847\n',text=True,capture_output=True,timeout=22,check=True)
        produced=(w/'sus847.splice').read_bytes();published=reference.read_bytes()
        def parse(data):
            rows=[l.split() for l in data.decode('ascii').splitlines() if l.strip()]
            return [tuple([float(row[0]), float(row[1]), int(row[2]),row[3],int(row[4]),row[5],int(row[6]),*map(float,row[7:])]) for row in rows]
        old,new=parse(published),parse(produced)
        from collections import Counter
        published_counts,generated_counts=Counter(old),Counter(new)
        shared=sum((published_counts&generated_counts).values())
        save('sus847_historical_splice.csv',[dict(site=847,source_program='PROGRAMS/SPLICE.F',source_sha256=hashlib.sha256((pr/'SPLICE.F').read_bytes()).hexdigest(),
            published_path='SITE_847/SUS/SUS847.MCD',published_rows=len(old),replay_rows=len(new),shared_complete_rows_multiset=shared,
            ordered_rows_equal=sum(a==b for a,b in zip(old,new)),replay_only_rows=len(new)-shared,published_only_rows=len(old)-shared,
            exact_numeric_row_sequence=old==new,byte_identical_after_LF=produced.replace(b'\r\n',b'\n')==published.replace(b'\r\n',b'\n'),
            compiler_version=subprocess.check_output([compiler,'--version'],text=True).splitlines()[0],stage='hole-switch splice before PR figure smoothing')])
        print(len(old),len(new),shared,old==new)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('primary',type=Path);p.add_argument('--compiler',default=os.environ.get('FC','gfortran'))
    p.add_argument('--compiler-flags',default=os.environ.get('FC_EXTRA_FLAGS',''));a=p.parse_args();run(a.primary,a.compiler,shlex.split(a.compiler_flags))
