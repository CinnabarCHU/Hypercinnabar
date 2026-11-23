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
    missing=[]
    for role in file_names:
        for code,count in used[role].items():
            if not cmaps[role].get(code,0):missing.append(dict(role=role,unicode=f'U+{code:04X}',count=count))
    return dict(scope='source OCR packets selected as modern body, heading or caption; no claim about semantic OCR accuracy',
                fonts={k:{'ttf':v,'sha256':digest(fonts/v),'distinct_codepoints':len(used[k])} for k,v in file_names.items()},
                missing_codepoints=missing)
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('output',type=Path);ap.add_argument('--fonts',type=Path,default=Path('/usr/share/fonts/truetype/dejavu'))
    a=ap.parse_args();result=check(a.output,a.fonts);(a.output/'font_check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
