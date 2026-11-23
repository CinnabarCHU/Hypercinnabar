"""Load addressed editorial readings and source-data reconstructions."""
import csv
import json
import re
from pathlib import Path

def readings(root, doc_id=None):
    result={}
    for path in sorted((root/'revision').glob('text_*/pages.jsonl')):
        for line in path.read_text(encoding='utf8').splitlines():
            row=json.loads(line)
            if doc_id and row['doc_id']!=doc_id:continue
            key=(row['doc_id'],int(row['source_page']))
            blocks=row['blocks']
            if key in result or not blocks or len({b['id'] for b in blocks})!=len(blocks):
                raise ValueError(f'Duplicate page or block, or empty reading: {path} {key}')
            if any(not isinstance(b['text'],str) or not b['text'].strip() for b in blocks):
                raise ValueError(f'Empty transcription: {key}')
            if not row.get('review_scope') or len(row.get('witness_sha256',''))!=64:
                raise ValueError(f'Missing source or scope: {key}')
            result[key]=row
    from plan_report import available_readings
    for row in available_readings(root,doc_id):
        result[row['doc_id'],int(row['source_page'])]=row
    return result

def reader_blocks(page):
    roles={'heading':'heading','title':'heading','section_heading':'heading','caption':'caption',
        'figure_caption':'caption','table_caption':'caption','footnote':'caption','note':'caption',
        'notice':'notice','folio':'notice','running_header':'notice','running_head':'notice','page_header':'notice'}
    return [(roles.get(b['role'],'body'),b['text']) for b in page['blocks']]

def figure_edits(root):
    result={}
    for path in sorted((root/'revision').glob('figures_*/manifest.csv')):
        with path.open(encoding='utf-8-sig',newline='') as stream:
            for row in csv.DictReader(stream):
                key=row['item_id']
                if key in result or not all(row[k] for k in ('source_page','source_kind','inputs','renderer','output','redraw_extent','qualification')):
                    raise ValueError(f'Incomplete or duplicate figure: {path} {key}')
                if not (root/row['output']).is_file() or not (root/row['renderer']).is_file():
                    raise FileNotFoundError(key)
                row['evidence_file']=path.relative_to(root).as_posix()
                result[key]=row
    return result

def styled_text(block, *, html=False):
    """Escape witness text and apply explicitly collated codepoint spans only."""
    from html import escape
    tags={'italic':'i','bold':'b','subscript':'sub','superscript':'sup','underline':'u'}
    spans=block.get('inline_styles',[])
    text=block['text']
    start={};stop={}
    for i,s in enumerate(spans):
        lo,hi=int(s['begin']),int(s['end']);style=s['style']
        if not 0<=lo<hi<=len(text) or style not in tags:
            raise ValueError((block['id'],s))
        start.setdefault(lo,[]).append((i,tags[style]))
        stop.setdefault(hi,[]).append(i)
    active={};last=0;parts=[]
    for n in sorted({*start,*stop,len(text)}):
        literal=escape(text[last:n])
        for tag in reversed(list(dict.fromkeys(active.values()))):
            literal=f'<{tag}>{literal}</{tag}>'
        parts.append(literal)
        for i in stop.get(n,()):active.pop(i)
        active.update(start.get(n,()))
        last=n
    markup=''.join(parts)
    if html:
        # Adjacent scripts attach to a common base, e.g. U with K′ above 37.
        # Keep the normal DOM reading order for selection, search and copy.
        markup=re.sub(r'(<sup>[^<>]+</sup>)(<sub>[^<>]+</sub>)',
                      r'<span class="script-pair">\1\2</span>',markup)
    return markup

def checked_lines(root,doc_id=None):
    result={}
    path=root/'revision/hole_headers/readings.csv'
    if path.is_file():
        with path.open(encoding='utf-8',newline='') as src:
            for row in csv.DictReader(src):
                if doc_id and row['doc_id']!=doc_id:continue
                page=(row['doc_id'],int(row['source_page']))
                addr=tuple(int(row[k]) for k in ('block','line','part'))
                if addr in result.setdefault(page,{}):raise ValueError((page,addr))
                result[page][addr]=row
    return result

def partially_collated(packets,checked,source_hash):
    """Apply exact, witness-bound readings but keep the archived OCR packets intact."""
    remainder=dict(checked); result=[]
    for packet in packets:
        material=[]
        for s in packet['lines']:
            addr=(s['block'],s['line'],s['part'])
            patch=remainder.pop(addr,None)
            if patch:
                if s['text']!=patch['publisher'] or source_hash!=patch['witness_sha256']:
                    raise ValueError(('stale line reading',addr))
                material.append(patch['reading'])
            else:material.append(s['text'])
        if packet['role']!='positioned':
            result.append((packet['role'],' '.join(material)))
        elif any((s['block'],s['line'],s['part']) in checked for s in packet['lines']):
            result.extend(('body',checked[(s['block'],s['line'],s['part'])]['reading'])
                       for s in packet['lines'] if (s['block'],s['line'],s['part']) in checked)
    if remainder:raise ValueError(('missing witness addresses',list(remainder)))
    return result

def page_blocks(collated,packets,fields):
    """Splice verified physical ranges while preserving all uncovered reading packets.

    A complete transcription of the stated page reading scope is rendered in its
    editor-defined order. In a partial overlay, insert a corrected block at the
    first encountered addressed source line and omit only its explicitly claimed
    OCR lines. Everything else retains its previous reading role and order.
    """
    proof=collated['blocks']
    if not collated.get('overlay_only',False):return proof
    by_address={}
    for i,b in enumerate(proof):
        addresses=b.get('source_addresses')
        if not addresses:raise ValueError(('unanchored partial block',b['id']))
        for a in addresses:
            addr=tuple(a)
            if addr in by_address:raise ValueError(('overlapping partial blocks',addr))
            by_address[addr]=i
    rendered=[];inserted=set();seen=set()
    for pk in packets:
        pending=[]
        def append_pending():
            if pending:
                rendered.append({'role':pk['role'],'text':' '.join(pending)})
                pending.clear()
        for line in pk['lines']:
            addr=tuple(line[k] for k in ('block','line','part'))
            if addr in by_address:
                seen.add(addr);append_pending()
                idx=by_address[addr]
                if idx not in inserted:rendered.append(proof[idx]);inserted.add(idx)
            elif pk['role']!='positioned':
                pending.append(fields.get(addr,{}).get('reading',line['text']))
            elif addr in fields:
                append_pending();rendered.append({'role':'body','text':fields[addr]['reading']})
        append_pending()
    if set(by_address)!=seen:raise ValueError(('absent anchors',set(by_address)-seen))
    return rendered
