"""Archive a complete offline, paired publication after checking its per-file hashes."""
import argparse
import hashlib
import os
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

def pack(source,output):
    source=source.resolve()
    output=output.resolve()
    if output.is_relative_to(source):
        raise ValueError('Place the archive outside the publication folder')
    sums={}
    for line in (source/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        if name in sums:raise ValueError('Duplicate manifest path: '+name)
        sums[name]=digest
    files={p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
    if files != set(sums)|{'SHA256SUMS'}:raise ValueError('Directory membership differs from SHA256SUMS')
    output.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=output.parent,suffix='.zip');os.close(fd);tmp=Path(tmp)
    try:
        with ZipFile(tmp,'w',compression=ZIP_DEFLATED,compresslevel=4,allowZip64=True) as book:
            for name in sorted(files):
                data=(source/name).read_bytes()
                if name in sums and hashlib.sha256(data).hexdigest()!=sums[name]:
                    raise ValueError('Source file changed: '+name)
                entry=ZipInfo('Leg138_Full_Edition/'+name, date_time=(1980,1,1,0,0,0))
                entry.create_system=3
                entry.external_attr=0o100644 << 16
                book.writestr(entry,data,compress_type=ZIP_DEFLATED,compresslevel=4)
        with ZipFile(tmp) as book:
            if book.testzip():raise ValueError('Archive CRC check failed')
        tmp.replace(output)
    finally:
        tmp.unlink(missing_ok=True)
    print(len(files),'files,',output.stat().st_size,'bytes',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('edition',type=Path);parser.add_argument('archive',type=Path)
    a=parser.parse_args();pack(a.edition,a.archive)
