import re
from numeric import HOLE_HEADER,tok,NUM
# Approximate intended age/comment anchors, from the distinct headings and populated cells.
TAIL={9:(59,66),10:(67,76),13:(62,72),15:(59,67),16:(70,80),17:(66,74),18:(74,83),19:(59,70)}

def decode(id,site,lines,emit,mark):
    ch=int(id[2:4]);core_context='';hole='';anchor='';age_x,comment_x=TAIL[ch]
    for ln,s in enumerate(lines,1):
        if m:=HOLE_HEADER.fullmatch(s):hole=(m[1] or str(site))+(m[2] or m[3]);core_context='';anchor=ln;mark(ln,'hole_heading');continue
        if re.match(r'^\s*(?:138-)?\d{3}[A-E]-\d+[HX]-\s*$',s):core_context=s.strip();hole=re.search(r'(\d{3}[A-E])-',core_context).group(1);anchor=ln;mark(ln,'core_heading');continue
        tokens=tok(s);notes=[]
        if len(tokens)<4:continue
        first=tokens[0].group()
        if not (re.search(r'\d[HX][-\d]',first) or core_context and first.isdigit()):continue
        d={'core_section':first,'interval_cm':tokens[1].group(),'depth_mbsf':tokens[2].group(),'depth_mcd':tokens[3].group()}
        if h:=re.search(r'(\d{3}[A-E])-',first):hole=h[1];anchor=ln
        d['reported_hole']=hole;d['context_line']=anchor
        if first.isdigit() and core_context:d['reported_core_prefix']=core_context
        tail=tokens[4:]
        if (id,ln)==('IR13.T07',55):
            d['depth_mcd']='';tail=tokens[3:];notes.append('composite_depth_empty_in_source')
        if (id,ln)==('IR19.T05',72):notes.append('source_core_section_written_without_hyphen')
        a=next((ix for ix,t in enumerate(tail) if NUM.fullmatch(t.group().lstrip('~<>')) and (abs(t.start()-age_x)<=10 or (id,ln) in [('IR18.T06',35),('IR18.T06',60)])),None)
        if a is not None:
            age=tail[a];p=age.start();end=age.end()
            if a and tail[a-1].group() in ('~','<','>'):p=tail[a-1].start()
            interpretation_start=tokens[2].end() if (id,ln)==('IR13.T07',55) else tokens[3].end()
            if a+1<len(tail) and NUM.fullmatch(tail[a+1].group()):
                end=tail[a+1].end();notes.append('two_alternative_MPTS_ages_as_written')
            d['interpretation']=s[interpretation_start:p].strip();d['age_ma']=s[p:end];d['comments']=s[end:].strip()
        elif tail:
            # Native comments are normally separated by a wide run of spaces.
            p=next((t.start() for t in tail if t.start()>=comment_x-3),len(s));d['interpretation']=s[tokens[3].end():p].strip();d['comments']=s[p:].strip()
            if m:=re.search(r'(?:Poorly defined|Section break|Reversed in|Near section)',d['interpretation'],re.I):
                text=d['interpretation'];d['comments']=text[m.start():]+((' '+d['comments']) if d['comments'] else '');d['interpretation']=text[:m.start()].strip();notes.append('comment_and_interpretation_touch_in_source')
        if not NUM.fullmatch(d['depth_mbsf']) or (d['depth_mcd'] and not NUM.fullmatch(d['depth_mcd'])):notes.append('irregular_depth_string')
        if first.endswith('-'):notes.append('section_number_absent')
        emit(ln,d,notes)
    return 'reported_hole context_line reported_core_prefix core_section interval_cm depth_mbsf depth_mcd interpretation age_ma comments'.split()
