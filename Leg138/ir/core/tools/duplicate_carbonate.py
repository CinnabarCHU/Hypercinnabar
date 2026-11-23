"""Transcribe the eleven carbonate replicate tables without merging the individual runs.

Nine PDF text layers are read by page-space column. The patches below are readings
of the page images. Site 846 uses the earlier collated edition. Site 850 has an ASCII file.
"""
import csv
import re
import fitz
from collections import Counter
from native import C, P, write

# Page-space word-centre selection and numeric column centres (PDF points).
LAYOUT = {
    844: ((160,450,106,233), [260,296,333,372,None,419]),
    845: ((128,425,106,225), [221,257,296,336,None,384]),
    847: ((282,550,111,374), [360,393,420,447,474,505]),
    848: ((150,455,490,649), [269,306,345,387,None,435]),
    849: ((118,422,110,474), [215,245,277,316,356,402]),
    851: ((171,450,467,681), [269,305,343,381,None,428]),
    852: ((137,461,114,407), [243,279,316,356,None,405]),
    853: ((166,431,524,688), [243,276,313,351,None,390]),
    854: ((164,458,655,724), [267,302,338,378,None,424]),
}
PATCHES = {
    844: {'48^9':'48-49','39-tt)':'39-40'},
    845: {'40-^2':'40-42'},
    847: {'IH':'1H','-I,':'-1,','-I1H':'-11H','-I2H':'-12H','-I3H':'-13H','-I4H':'-14H','16XA':'16X-4,','0.7?':'0.75'},
    849: {'LOS':'1.08','0.0(1':'0.00','41^3':'41-43'},
    853: {'43-15':'43-45','4FM':'4H-4','5HA':'5H-4','6H^':'6H-4'},
}
# PDF text layer omits several right-hand values. Transcribed from p. 363.
DIFF_847 = '0.50 0.25 0.06 0.84 0.92 0.01 0.08 1.92 0.00 0.09 0.00 2.58 2.08 1.42 0.92 0.66 0.17 1.33 1.75 0.08 0.00 0.09 0.16 1.25 0.08 1.42 1.08 0.17 0.75 0.33 0.08 1.75 0.17 0.75 0.16 0.09 0.17 0.42 0.92 0.00 0.34 0.33 1.09'.split()


def printed(site, entry):
    (left,right,top,bottom), centres = LAYOUT[site]
    words_by_row=[]
    with fitz.open(P/entry['pdf_path']) as doc:
        words=doc[int(entry['pdf_page'])-1].get_text('words')
    words=sorted(words,key=lambda w:(w[1]+w[3])/2)
    for word in words:
        x,y=(word[0]+word[2])/2,(word[1]+word[3])/2
        if not (left<x<right and top<y<bottom):continue
        if not words_by_row or y-words_by_row[-1][0]>2.8:
            words_by_row.append((y,[]))
        words_by_row[-1][1].append((x,word[4]))
    hole={849:'849B',853:'853B'}.get(site,'')
    for num,(y,words) in enumerate(words_by_row,1):
        cells=['']*6;label=[];kind='sample'
        for x,t in sorted(words):
            for old,new in PATCHES.get(site,{}).items():t=t.replace(old,new)
            if t=='Average':kind='mean_difference';continue
            if x<centres[0]-14:label.append(t);continue
            idx=min((i for i,c in enumerate(centres) if c is not None),key=lambda i:abs(centres[i]-x))
            assert abs(centres[idx]-x)<8 and not cells[idx],(site,num,x,t,cells)
            cells[idx]=t
        label=' '.join(label)
        if site==847 and kind=='sample':
            if num==1:cells[:2]=['4.84','4.84']
            if num==2:cells[1]='6.85'
            if cells[-1]:assert cells[-1]==DIFF_847[num-1],(num,cells)
            cells[-1]=DIFF_847[num-1]
        if kind=='sample':
            prefix=re.search(rf'{site}([A-E])-',label)
            if prefix:hole=f'{site}{prefix[1]}'
            assert hole and re.search(r'\d+[HX]-\d',label),(site,num,label)
            assert all(re.fullmatch(r'\d+\.\d+',v) for v in cells if v),(site,num,cells)
            assert all(cells[i] for i in (0,1,2,3,5)),(site,num,cells)
        yield num,kind,hole if kind=='sample' else '',label,cells,'chapter_page',entry['pdf_path'],'',f'{y:.1f}'


def prior_846(entry):
    with (C/'site846_prior/table-11.csv').open(newline='') as f:
        for num,r in enumerate(csv.DictReader(f),1):
            values=[r[k] for k in ['depth_mbsf','depth_mcd','run_1_carbonate_pct','run_2_carbonate_pct','run_3_carbonate_pct','printed_absolute_difference_pct']]
            kind='sample' if r['row_kind']=='data' else 'mean_difference'
            yield num,kind,'846'+r['hole'] if r['hole'] else '',r['sample'],values,'chapter_page_via_collated_site846',entry['pdf_path'],'',''


def native_850(entry):
    lines=(P/entry['native_path']).read_text(encoding='latin1').splitlines()
    row=0;hole=''
    for ln,line in enumerate(lines,1):
        fields=line.split()
        if line.rstrip()=='850A-':hole='850A';continue
        if not fields:continue
        if fields[0]=='Average':
            row+=1;yield row,'mean_difference','','',['','','','','',fields[-1]],'disc_ascii',entry['native_path'],ln,''
        elif re.match(r'^\d+[HX]-\d',fields[0]):
            assert len(fields)==7 and hole
            row+=1;yield row,'sample',hole,' '.join(fields[:2]),fields[2:6]+['',fields[6]],'disc_ascii',entry['native_path'],ln,''


def main():
    with (C/'chapter_items.csv').open(newline='') as f:
        entries=[r for r in csv.DictReader(f) if r['kind']=='table' and r['title'].lower().startswith('duplicate analyses')]
    assert len(entries)==11
    out=[];runs=[];directory=[]
    for r in entries:
        site=int(r['site']);sid=r['item_id'];stats=Counter()
        data=prior_846(r) if site==846 else native_850(r) if site==850 else printed(site,r)
        for num,kind,hole,label,values,witness,path,line,y in data:
            sample=f'{sid}:r{num:03}';stats[kind]+=1
            out.append([sample,sid,site,num,kind,hole,label,*values,witness,path,line,r['pdf_page'],r['printed_page'],y])
            for run,value in enumerate(values[2:5],1):
                if value:
                    runs.append([f'{sample}:run{run}',sample,sid,site,run,value,witness,path,line,r['pdf_page'],r['printed_page'],num,y]);stats['runs']+=1
        assert stats['mean_difference']==1
        directory.append([sid,site,r['pdf_path'],r['pdf_page'],r['printed_page'],'narrative_reference_to_cd_rom' if site==850 else 'printed_table',r['native_path'],witness,stats['sample'],stats['runs'],stats['mean_difference']])
    write(C/'carbonate_repeat_samples.csv',['sample_row_id','item_id','site','source_row','row_kind','reported_hole','sample_label','depth_mbsf','depth_mcd','run_1_carbonate_pct','run_2_carbonate_pct','run_3_carbonate_pct','published_absolute_difference_pct','witness','source_path','source_line','chapter_pdf_page','printed_page','pdf_row_y_pt'],out)
    write(C/'carbonate_repeat_runs.csv',['run_record_id','sample_row_id','item_id','site','published_run_number','carbonate_pct','witness','source_path','source_line','chapter_pdf_page','printed_page','source_row','pdf_row_y_pt'],runs)
    write(C/'carbonate_repeat_sources.csv',['item_id','site','chapter_pdf','chapter_pdf_page','printed_page','chapter_locator_role','native_path','chosen_witness','sample_rows','individual_runs','published_mean_difference_rows'],directory)
    print('replicate carbonate records',len(runs),'sample rows',len(out)-len(entries),'published means',len(entries));print(directory)

if __name__=='__main__':main()
