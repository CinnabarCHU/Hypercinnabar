"""Assemble a reproducible local demo around the verified GUI and plugin artifacts."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import zlib

EXPECTED = {
    'packages/acycle_deepseek-0.7.0-py3-none-any.whl':'d4b0bb18fa6c29065a788fbd78c0ff218b896d113c01eaedaf702c79f60544ca',
    'packages/dsh-acycle-0.7.0.tgz':'187f9d4121437d4c223a6ff5f88ffbdd86d936340eb074a2621df656d3601211',
    'acycle/matlab/+acgui/live.m':'a2e3e3606a4e36e952aa914e6f9101b6ae12bed8ba3746433344790ce0e28b47',
    'acycle/acycle-runtime.json':'48638f3fbf72cbf1066e87f03ddf98cc2e172e355c2290a402709f73d7fcdd24',
}


def png_chunk(kind, data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)


def assemble(artifact, destination):
    for name, expected in EXPECTED.items():
        if hashlib.sha256((artifact/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('Unexpected source artifact '+name)
    if destination.exists():
        raise FileExistsError('Choose a new assembly directory '+str(destination))
    destination.mkdir(parents=True)
    for name in ('acycle','packages'):
        shutil.copytree(artifact/name,destination/name)
    source = Path(__file__).resolve().parent
    for name in ('start_local_demo.m','local_test.py','check_harness.mjs','README.zh-CN.md'):
        shutil.copyfile(source/name,destination/name)
    study = destination/'study'
    study.mkdir()
    for name in ('series.csv','second.csv'):
        with (study/name).open('w',newline='',encoding='utf-8') as handle:
            writer=csv.writer(handle)
            for depth in range(256):
                if name=='series.csv':
                    value=math.sin(2*math.pi*depth/20)+.2*math.cos(2*math.pi*depth/5)
                else:
                    value=math.cos(2*math.pi*depth/17)
                writer.writerow([depth,format(value,'.17g')])
    width,height=128,192
    pixels=bytearray()
    for y in range(height):
        pixels.append(0)
        for x in range(width):
            pixels.append(round(125+65*math.sin(2*math.pi*(y+.12*x)/28)+25*math.cos(2*math.pi*y/9)))
    header=struct.pack('>IIBBBBB',width,height,8,0,0,0,0)
    (study/'core.png').write_bytes(b'\x89PNG\r\n\x1a\n'+png_chunk(b'IHDR',header)+
        png_chunk(b'IDAT',zlib.compress(bytes(pixels),9))+png_chunk(b'IEND',b''))
    manifest={'version':'0.7.0','source_commit':'514d059226425d0101418d3bb23c44bf91f66709',
        'source_run':'https://github.com/CinnabarCHU/Hypercinnabar/actions/runs/45193226531',
        'artifact_id':14828515569,'verified_components_sha256':EXPECTED,
        'harness_tools_version':'0.2.2-rc.5',
        'entry_point':'start_local_demo.m','test_command':'python3 local_test.py check',
        'sample_coordinate_unit':'m','sample_frequency_unit':'cycles/m'}
    (destination/'LOCAL_TEST_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    lines=[]
    for file in sorted(destination.rglob('*')):
        if file.is_file():
            lines.append(hashlib.sha256(file.read_bytes()).hexdigest()+'  '+file.relative_to(destination).as_posix())
    (destination/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    output=destination.parent/(destination.name+'.zip')
    with ZipFile(output,'w',ZIP_DEFLATED,compresslevel=5) as z:
        for file in sorted(destination.rglob('*')):
            if file.is_file():
                name=(Path(destination.name)/file.relative_to(destination)).as_posix()
                info=ZipInfo(name,date_time=(2026,11,25,0,0,0))
                info.compress_type=ZIP_DEFLATED
                info.external_attr=0o100644<<16
                z.writestr(info,file.read_bytes())
    with ZipFile(output) as z:
        assert z.testzip() is None
    print(output)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact',required=True,type=Path)
    parser.add_argument('--destination',required=True,type=Path)
    args=parser.parse_args()
    assemble(args.artifact.resolve(),args.destination.resolve())
