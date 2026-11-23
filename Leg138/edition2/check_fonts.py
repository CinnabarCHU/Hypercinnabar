"""Check reflowed OCR characters against the actual rendering fonts' Unicode maps."""
from collections import Counter
from pathlib import Path
import argparse,gzip,json,unicodedata
from reportlab.pdfbase.ttfonts import TTFont
from companions import digest

def check(out,fonts):
    file_names={'body':'DejaVuSerif.ttf','caption':'DejaVuSans.ttf','heading':'DejaVuSans-Bold.ttf'}
    cmaps={role:TTFont(role,str(fonts/f)).face.charToGlyph for role,f in file_names.items()}
    used={role:Counter() for role in file_names}
    for path in (out/'audit').glob('*.jsonl.gz'):
        with gzip.open(path,'rt') as f:
            for record in map(json.loads,f):
                for block in record['packets']:
                    role=block['role']
                    if role in cmaps:
                        for line in block['lines']:used[role].update(ord(c) for c in line['text'])
                visual=record.get('visual_collation')
                if visual:
                    from revisions import reader_blocks
                    for role,text in reader_blocks(visual):
                        target=role if role in used else 'caption'
                        used[target].update(map(ord,text))
    layout_controls=Counter()
    missing=[]
    for role in file_names:
        for code,count in used[role].items():
            if chr(code) in ('\t','\n','\r'):
                layout_controls[f'U+{code:04X}']+=count
                continue
            if not cmaps[role].get(code,0):missing.append(dict(role=role,unicode=f'U+{code:04X}',count=count))
    return dict(scope='Unicode coverage of source OCR packets and visually collated strings using the base reader typefaces. Inline bold and italic runs are also inspected in rendered samples.',
                fonts={k:{'ttf':v,'sha256':digest(fonts/v),'distinct_codepoints':len(used[k])} for k,v in file_names.items()},
                non_glyph_layout_controls=dict(layout_controls),missing_codepoints=missing)
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('output',type=Path);ap.add_argument('--fonts',type=Path,default=Path('/usr/share/fonts/truetype/dejavu'))
    a=ap.parse_args();result=check(a.output,a.fonts);(a.output/'font_check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
