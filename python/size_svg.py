"""Give MATLAB's SVG plot its measured paper size while keeping its coordinate system."""
import re
from pathlib import Path

SIZES = {'F1':(173,134),'F2h':(190,71),'F2iso':(177,203),'F3':(178,90),
         'F4':(184,162),'F5':(190,102),'F6':(180,165),'F7':(190,132),'F8':(170,185),
         'S1':(162,211),'S2':(162,166),'S3':(162,221),'S4':(162,194),'S5':(162,173),
         'S6':(162,210),'S7':(162,214)}

def set_paper_size(path, figure):
    path = Path(path)
    data = path.read_bytes()
    tag = re.search(rb'<svg\b[^>]*>', data)
    if not tag:
        raise ValueError(f'No SVG root in {path}')
    old = tag.group()
    if re.search(rb'\bwidth="[0-9.]+mm"', old):
        return
    width, height = SIZES[figure]
    changed, count = re.subn(rb' width="([0-9.]+)" height="([0-9.]+)"',
        lambda m: f' width="{width}mm" height="{height}mm"'.encode()
        + (b'' if b'viewBox=' in old else b' viewBox="0 0 '+m[1]+b' '+m[2]+b'"'), old)
    if count != 1:
        raise ValueError(f'Unexpected SVG dimensions in {path}')
    path.write_bytes(data[:tag.start()]+changed+data[tag.end():])

if __name__ == '__main__':
    import sys
    for item in Path(sys.argv[1]).glob('*/*/plot.svg'):
        set_paper_size(item,item.parent.name)
