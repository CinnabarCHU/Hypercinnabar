"""Transcribe the entire printed list of 37 biohorizons in Chapter 21 Table 2."""
import argparse,csv,json
from pathlib import Path
import fitz
from build import baselines,united,rounded
TEXT="""Discoaster quinqueramus LO
Amaurolithus amplificus LO
Amaurolithus amplificus FO
Amaurolithus primus FO
Discoaster surculus FCO
Discoaster berggrenii FO
Discoaster pentaradiatus FO
Discoaster neorectus FO
Discoaster loeblichii FO
Discoaster bollii LO
Mynilitha convallis FO
Discoaster hamatus LO
Discoaster neohamatus FO
Discoaster prepentaradiatus FO
Catinaster calyculus LO
Catinaster coalitus LO
Discoaster hamatus FO
Catinaster calyculus FO
Coccolithus miopelagicus LO
Discoaster bellus group FO
Discoaster exilis LCO
Discoaster calcaris FO
Catinaster coalitus FO
Discoaster kugleri LO
Discoaster kugleri LCO
Discoaster bollii FO
Discoaster kugleri FCO
Discoaster kugleri FO
Calcidiscus macintyrei FO
Coronocyclus nitescens LO
Triquetrorhabdulus serratus LO
Calcidiscus premacintyrei LCO
Triquetrorhabdulus rugosus FCO
Discoaster signus LO
Cyclicargolithus floridanus LCO
Reticulofenestra pseudoumbilicus FO
Sphenolithus heteromorphus LO"""
def main():
    ap=argparse.ArgumentParser();ap.add_argument('core',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args()
    file='official/VOLUME/CHAPTERS/sr138_21.pdf';pg=fitz.open(a.core.parent/'primary'/file)[2]
    words=[(*w[:4],w[4]) for w in pg.get_text('words',clip=fitz.Rect(351,410,493,684))]
    rowset=baselines(words);parsed=TEXT.splitlines()
    assert len(rowset)==len(parsed)==37
    with (a.out/'verified_c21_table2.csv').open('w',newline='') as out:
        dest=csv.writer(out,lineterminator='\n');dest.writerow(['item_id','source','pdf_page','print_page','row_in_print','horizon_number_printed','taxon_label_printed','event_code_printed','event_definition_in_note','row_bbox_pt','status'])
        for n,(ww,txt) in enumerate(zip(rowset,parsed),1):
            name,event=txt.rsplit(' ',1)
            dest.writerow(['SR.C21.TABLE2',file,3,481,n,38-n,name,event,{'LO':'last occurrence','FO':'first occurrence','LCO':'last common occurrence','FCO':'first common occurrence'}[event],json.dumps(rounded(united(ww))),'visually_read_and_field_mapped'])
    pg.get_pixmap(clip=fitz.Rect(291,391,505,687),matrix=fitz.Matrix(2,2)).save(a.out/'verified_c21_table2.png')
if __name__=='__main__':main()
