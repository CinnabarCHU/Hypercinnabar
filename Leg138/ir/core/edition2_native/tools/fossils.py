"""Read the specimen ranges and two depth columns in the electronic biostratigraphy tables."""
import re
from numeric import tok
# Reported boreholes and normal interval starts (byte offsets), set from each file's heading and full rows.
LAYOUT={
 'IR09.T03':(5,'844B 844C',[31,76]),'IR09.T04':(5,'844B',[35]),'IR09.T05':(5,'844B 844C 844D',[30,71,107]),'IR09.T06':(5,'844B 844C',[32,74]),
 'IR10.T03':(6,'845A 845B',[36,85]),'IR10.T04':(5,'845A 845B',[31,74]),'IR10.T05':(5,'845A 845B',[30,72]),
 'IR12.T03':(6,'847B 847C 847D',[38,91,136]),'IR12.T04':(5,'847B',[35]),'IR12.T05':(5,'847B 847C 847D',[31,77,121]),
 'IR13.T03':(4,'848B 848C 848D',[36,81,126]),'IR13.T04':(5,'848B 848C 848D',[30,67,103]),'IR13.T05':(4,'848B 848C 848D',[27,65,103]),
 'IR14.T03':(5,'849B 849C 849D',[36,90,139]),'IR14.T04':(4,'844B',[32]),'IR14.T05':(4,'849B 849C 849D',[31,76,123]),'IR14.T06':(5,'849B 849C 849D',[42,88,132]),
 'IR15.T03':(5,'850A 850B',[36,88]),'IR15.T04':(5,'hole_unspecified',[32]),'IR15.T05':(6,'850A 850B',[33,72]),'IR15.T06':(6,'850A 850B',[37,76]),
 'IR16.T03':(6,'851B 851C 851E',[37,91,139]),'IR16.T04':(5,'851B',[34]),'IR16.T05':(4,'851B 851C 851E',[31,80,128]),'IR16.T06':(7,'851B 851C 851E',[40,89,138]),
 'IR17.T04':(6,'852B 852C 852D',[38,92,146]),'IR17.T05':(5,'852B',[33]),'IR17.T06':(6,'852B 852C 852D',[33,73,115]),'IR17.T07':(5,'852B 852C 852D',[29,69,115]),
 'IR18.T02':(4,'853B',[36]),'IR18.T03':(5,'853B',[36]),'IR18.T04':(4,'853B',[32]),'IR19.T02':(5,'854B',[30]),'IR19.T03':(5,'854B',[31])}
SAMPLE=re.compile(r'(?<!\S)(?:[<>?]+\s*)?(?:0-)?(?:\d+[HX](?:[-,.]|\s*CC)|\d+-CC)')
DEPTH=re.compile(r'^[<>~?]*-?\d+(?:\.\d*)?(?:[-_](?:[<>~]*\d+(?:\.\d*)?)?)?[?*]?$')
FOOTER=re.compile(r'^\s*(?:T\s*(?:=|\s+top)|Note:)',re.I)

def decode(id,site,ls,emit,mark):
    start,hole_text,anchors=LAYOUT[id];holes=hole_text.split();fields=['event_as_written','event_group_first_line','event_display_joined','row_kind','previous_body_line']+[hole+'_'+field for hole in holes for field in ('sample_interval','depth_mbsf','depth_mcd')];last='';records={}
    for i,line in enumerate(ls,1):
        if i<start or not line.strip() or FOOTER.match(line):continue
        notes=[];parts=[];excess=[];row={};candidates=list(SAMPLE.finditer(line))
        for m in candidates:
            rank=min(range(len(anchors)), key=lambda k:abs(m.start()-anchors[k]));distance=abs(m.start()-anchors[rank]);
            if distance>15 or rank in [p[0] for p in parts]:
                # A displaced source fragment can contain a second copy of a sample range.
                # Keep it in its original position for targeted inspection.
                if parts and m.start()-parts[-1][1]<25:continue
                excess.append(m.start());continue
            parts.append((rank,m.start()))
        breaks=sorted(set([x for h,x in parts]+excess+[len(line)]));event=line[:breaks[0]].strip();row['event_as_written']=event
        if excess:notes.append('extra_or_displaced_sample_group');row['unresolved_source_fragment']=' | '.join(line[x:next(b for b in breaks if b>x)].strip() for x in excess)
        for h,pos in parts:
            segment=line[pos:next(b for b in breaks if b>pos)];tt=tok(segment);a=[t.group() for t in tt];prefix=holes[h]+'_';
            if len(tt)>=3 and all(DEPTH.fullmatch(v) for v in a[-2:]):
                row[prefix+'sample_interval']=segment[:tt[-2].start()].strip();row[prefix+'depth_mbsf']=a[-2];row[prefix+'depth_mcd']=a[-1]
                if re.search(r'[<>]|[-._]$',a[-2]+a[-1]):
                    if a[-2].endswith(('-','.')) or a[-1].endswith(('-','.')):notes.append('truncated_depth_string')
                if any(v.count('.')>2 or re.fullmatch(r'\d+\.\d{4,}\.\d+',v) for v in a[-2:]):notes.append('irregular_depth_lexeme')
            elif len(tt)>=2 and DEPTH.fullmatch(a[-1]) and ('.' in a[-1] or a[-1].endswith('-')):
                row[prefix+'sample_interval']=segment[:tt[-1].start()].strip();row[prefix+'depth_mbsf']=a[-1];notes.append('only_one_depth_token_check_alignment')
            else:
                row[prefix+'sample_interval']=segment.strip();notes.append('depth_tokens_not_separable_from_sample_range')
        if not parts:
            if re.search(r'\d[HX][-,]|\d\.\d',event):row['row_kind']='data_fragment';notes.append('source_line_with_unresolved_columns')
            else:row['row_kind']='event_text_only'
        elif not event or not re.match(r'^(?:T |B |TT |BB |[A-Z])',event):row['row_kind']='continuation_or_unmarked_event';notes.append('verify_event_line_continuation')
        else:row['row_kind']='event_and_constraints'
        if (id,i)==('IR09.T06',8):
            row.update({'844C_sample_interval':'2H-CC-3H-CC','844C_depth_mbsf':'18.62-28.66','844C_depth_mcd':'19.92 -31.01'})
        if (id,i)==('IR10.T04',29):
            row.update({'845B_sample_interval':'7H-CC-8H-CC','845B_depth_mbsf':'69.85.57','845B_depth_mcd':'76.46-87.95'});notes=['irregular_depth_lexeme']
        if (id,i)==('IR12.T04',12):
            row.update({'847B_sample_interval':'12H-CC-13H-CC','847B_depth_mbsf':'111.59121.05','847B_depth_mcd':'124.61-135.05'});notes=['irregular_depth_lexeme']
        if (id,i)==('IR13.T04',30):
            row.update({'848B_sample_interval':'6H-5-6H-CC','848B_depth_mbsf':'47.30-50.17','848B_depth_mcd':'53.00-55.87','848D_depth_mcd':'61.40-71.87'});notes=['isolated_depth_in_final_hole_group']
        if (id,i)==('IR12.T03',6):
            row.update({'847C_sample_interval':'2H-1  140-2H-1 145','847C_depth_mbsf':'12.90-12.95','847C_depth_mcd':'14.58-14.63','unresolved_source_fragment':line[151:].rstrip()});notes=['truncated_event_and_displaced_or_duplicated_source_cells']
        if (id,i)==('IR16.T03',6):
            row.update({'851B_sample_interval':'1H-5, 95-1H-5, 140','851B_depth_mbsf':'6.95-7.40','851B_depth_mcd':''});notes=['mcd_continues_on_following_source_line']
        if (id,i)==('IR16.T03',7):
            row.update({'event_as_written':'','851B_depth_mcd':line.strip(),'row_kind':'depth_continuation'});notes=['continuation_of_preceding_constraint']
        if id=='IR14.T04':notes.append('header_hole_844B_in_site_849_chapter')
        if id=='IR15.T04':notes.append('no_hole_identifier_in_native_header')
        row['previous_body_line']=last;last=i;records[i]=(row,notes)
    continuations={'IR09.T03':[21],'IR09.T05':[33,44,61],'IR09.T06':[12,29,33,45,50],
        'IR10.T04':[34,44,62],'IR12.T04':[6],'IR12.T05':[34],'IR13.T04':[34],
        'IR14.T05':[36,47],'IR15.T05':[39],'IR16.T03':[7],'IR16.T05':[35,46],
        'IR17.T06':[38],'IR17.T07':[13,22],'IR18.T03':[6]}.get(id,[])
    groups={}
    for ln,(row,notes) in records.items():
        leader=ln-1 if ln in continuations else ln;assert leader in records
        groups.setdefault(leader,[]).append(ln)
    for leader,group in groups.items():
        joined=' '.join(records[k][0]['event_as_written'] for k in group).strip()
        for ln in group:
            row,notes=records[ln];row['event_group_first_line']=leader;row['event_display_joined']=joined
            if 'verify_event_line_continuation' in notes and ln in continuations:notes.remove('verify_event_line_continuation')
            if (id,ln)==('IR09.T05',33):notes.append('sample_under_first_hole_on_continuation_line_location_uncertain')
            for name,value in row.items():
                if not name.endswith(('_depth_mbsf','_depth_mcd')) or not value:continue
                if m:=re.fullmatch(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)',value):
                    if float(m[2])<float(m[1]):notes.append('depth_range_descends_in_source')
            emit(ln,row,notes)
    return fields
