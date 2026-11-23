"""Reading-order and glyph decisions for additional Site 846 pages."""
CAPTIONS = {
    8:'r0 c113 f117', 9:'r0 c58 f59', 10:'c0', 11:'r0 c2 f18', 12:'r0 c237 f236',
    13:'c3', 14:'r0 c3 f4', 15:'r0 c33 f34', 16:'r0 c11+12 f13',
    17:'r0 c4 c15 f19', 18:'r0 c12 c23+24 f29',19:'r0 c18 c19 f21',
    20:'r0 c10 c19 f20', 22:'r0 c1 c28 f53',23:'c0',24:'c0',25:'c0',
    26:'r0 c269 f270',27:'r0 c161 f168',
    37:'r0 c1 f59',38:'r0 c4 f15',39:'r0 c16 f19',40:'r0 c1 f132',
    41:'r0 c14 f15',42:'r0 c4 f13',43:'r0 c6 f15',44:'r0 c27 f43',
    45:'r0 c14 f20',46:'r0 c13 f20',47:'r0 c5 f14',48:'r0 c12 f19',
    49:'r0 c8 f14',50:'r0 c12 c16 c17 f26',51:'r0 c18 c43 f47',52:'r0 c10 c18 f21',
    53:'r0 c4 f37',54:'r0 n1 c17 f18',55:'r0 c21 c22 f23',56:'r0 c6 f7',
    57:'r0 c1:1 c1:2 f101',58:'r0 c4 f5',59:'r0 c12 f13',60:'r0 c17 f18',
    61:'r1 h0 f38',62:'r0 h1 f48',63:'h0',64:'r0 h1 f43',65:'r0 h1 f48',
    66:'r0 h3 f31',67:'r0 h1 f35',68:'h0',69:'h1'
}
ADDITIONAL_EXCLUSIONS = {
    8:'Figure 5 interior',9:'Figure 5 interior',12:'Figure 7 interior',14:'Figure 7 interior',
    15:'Figure 8 interior',26:'Figure 18 interior',41:'Figure 30 interior',
    54:'Figure 46 interior',55:'Figures 47 and 48 interiors',56:'Figure 49 interior',
    58:'Figure 50 interior',59:'Figure 51 interior',60:'Figure 52 interior',
    **{n:'log-summary interiors' for n in (61,62,64,65,66,67)},
}
PARTIAL_SCOPE = {
    n:('log-summary title only' if n>=61 else
       'figure or table captions only' + ('; also running head and folio' if g.startswith('r') else ''))
    for n,g in CAPTIONS.items() if n not in ADDITIONAL_EXCLUSIONS
}
ADDITIONAL_EDITS = {
    16:{(12,1):[('30-150','30–150')],(12,2):[('450-500','450–500'),('650-', '650–')],(12,3):[('850-900','850–900')]},
    17:{(4,1):[('650-700','650–700')],(15,2):[('57-87','57–87')]},
    18:{(12,2):[('846B-3H-lat50-96cm.', '846B-3H-1 at 50–96 cm.')],(24,1):[('20-62','20–62')]},
    19:{(18,2):[('95-148','95–148')],(19,2):[('63-84','63–84')]},
    20:{(10,1):[('41-80','41–80')],(19,2):[('Subunit HB','Subunit IIB')],(19,3):[('4-27','4–27')]},
    23:{(0,1):[('846-','846.')]},26:{(269,1):[('rnbsf','mbsf')],(269,3):[('A=abundant','A = abundant')]},
    37:{(1,1):[('CaCO3','CaCO₃')]},38:{(4,1):[('CaCO3','CaCO₃')]},
    39:{(16,1):[('CaCO3 and C','CaCO₃ and Corg')]},
    41:{(14,1):[('CaCO3 (B)','CaCO₃ (B)'),('non-CaCO3','non-CaCO₃'),('C o r g','Corg')]},
    42:{(4,1):[('C. CaCO3','C. CaCO₃'),('Non-CaCO3','Non-CaCO₃')],(4,3):[('3 IB','31B')]},
    44:{(27,1):[('U37','UK′37')]},
    52:{(10,3):[('262-320','262–320')]},53:{(4,5):[('=1:1','= 1:1')]},
    54:{(1,1):[('"barrel sheets"','“barrel sheets”')]},55:{(21,4):[('lef t','left')]}
}
ADDITIONAL_ITALIC={17:{'c15':['Zoophycos']},20:{'c10':['Chondrites']}}
ADDITIONAL_HYPHENS={(18,12,1),(19,18,1),(55,22,3)}

def complete_body(n,groups,excludes):
    CAPTIONS[n] = groups
    PARTIAL_SCOPE.pop(n,None)
    ADDITIONAL_EXCLUSIONS[n] = excludes

def add_edits(n,items):
    ADDITIONAL_EDITS.setdefault(n,{}).update(items)

complete_body(37,'r0 c1 p51+52 p53+54 h55+56 p57+58 f59','Table 11 body and headers')
complete_body(38,'r0 c4 h5 p6 p7+8 p9 p10+11 h12+13 p14 f15','Figure 28 interior')
complete_body(39,'r0 c16 p17+18 f19','Figure 29 interior')
complete_body(40,'r0 c1 n120+121:1-2 n121:3 p122 p123+124+125 h126 h127 p128 p129 h130 p131 f132','Table 12 body and headers')
add_edits(37,{(51,2):[('%CaCO3','%CaCO₃')],(53,3):[('CaCO3','CaCO₃')],(57,3):[('CaCO3','CaCO₃')],
              (58,1):[('CaCO3','CaCO₃')],(58,2):[('de sity','density')],(58,3):[('CdCO3','CaCO₃')],
              (58,11):[('the CaCO3','the CaCO₃'),('non-CaCO3','non-CaCO₃')],(58,12):[("MAR's",'MAR’s')],
              (58,16):[('CaCO3','CaCO₃')]})
add_edits(38,{(6,2):[('cm3','cm³')],(6,3):[('"Explanatory Notes"','“Explanatory Notes”')],
              (7,5):[('"Inorganic','“Inorganic')],(7,6):[('Geochemistry"','Geochemistry”')],
              (13,1):[('Uf7','UK′37')],(14,12):[('"Explanatory Notes"','“Explanatory Notes”')]})
add_edits(39,{(17,2):[('"alkenones"','“alkenones”')],(18,1):[("U^'","UK′37")]})
add_edits(40,{(120,1):[('"Sedimentation Rates"','“Sedimentation Rates”')],
              (122,4):[('U^','UK′37')],(122,5):[("U^'","UK′37")],(122,7):[('Ufj','UK′37')],
              (122,11):[('Phyloge-','phyloge-')],(123,3):[('3,','³,')],(123,5):[('Vfη','UK′37')],
              (124,5):[('3.','³.'),('u £','UK′37')],(124,20):[('U|C','UK′37')],(125,1):[('U37','UK′37')],
              (131,6):[('"Organic Geochemistry"','“Organic Geochemistry”')],
              (131,11):[('3,','³,')],(131,13):[('3 (','³ (')]})
ADDITIONAL_ITALIC[40]={'p122':['Emiliania huxleyi','E. huxleyi']}
ADDITIONAL_HYPHENS.update({(40,123,7),(40,124,2),(40,128,2)})
complete_body(11,'r0 c2 p3 h4 h5 p6:1 p6:2 p6:3 p7 h8 h9 p10:1 p10:2 p10:3 p11+12 h13 h14 p15:1 p15:2 p15:3 p16 p17 f18','Figure 6 interior')
complete_body(16,'r0 c11+12 p1 h2 p3 p4 h5 p6 p7 f13','Figure 9 interior')
complete_body(17,'r0 c4 c15 h5 p6 p7 p16 p17 p18 f19','Figures 10 and 11 interiors')
complete_body(18,'r0 c12 c23+24 p25+26+27 p28 f29','Figures 12 and 13 interiors')
complete_body(19,'r0 c18 c19 p20 f21','Figures 14 and 15 interiors')
complete_body(20,'r0 c10 c19 p11 p12 p13 f20','Figures 16 and 17 interiors')
complete_body(21,'r0 p1 h2 p3 p4 p5 h6 p7 h8 p9+10 p11 p12 p13 p14 k15+16:1+16:3+16:2+16:4+16:5 '+
    ' '.join('q'+'+'.join(f'{b}:{j}' for b in range(17,22)) for j in range(1,6))+
    ' n22 p23 h24 p25 f26','')
CAPTIONS[23]+=' n56'
CAPTIONS[24]+=' n30'
for n in (23,24):
    PARTIAL_SCOPE[n]='table caption and table note only'
add_edits(11,{
 (6,1):[('4,110','4, 110')],(6,2):[('317.0-419.2','317.0–419.2')],(6,3):[('10.6-16.5','10.6–16.5')],
 (7,2):[('HA','IIA')],(7,3):[('HB','IIB')],(7,6):[('HB','IIB')],(8,1):[('HA','IIA')],
 (10,1):[('4,110','4, 110')],(10,2):[('317.0-370.5','317.0–370.5')],(10,3):[('10.6-14.1','10.6–14.1')],
 (11,1):[('DA','IIA')],(11,6):[('30%-70%','30%–70%')],(11,7):[('60%-80%','60%–80%')],
 (12,2):[('HA','IIA')],(12,3):[('1,20','1, 20')],(12,4):[('< 1 %','<1%')],(13,1):[('HB','IIB')],
 (15,2):[('370.5-419.2','370.5–419.2')],(15,3):[('14.1-16.5','14.1–16.5')],(16,1):[('HB','IIB')],
 (16,6):[('"Downhole Measurements"','“Downhole Measurements”')],(17,2):[('HB','IIB')],(17,3):[('5 YR','5YR')]
})
add_edits(16,{(1,2):[('Plagioclase','plagioclase')],(1,4):[('0-63','0–63')],(4,12):[('Unit HB','Unit IIB')],
              (6,2):[('0.1-10','0.1–10')],(6,5):[('1,30-150','1, 30–150')],(7,3):[('1-10','1–10')],
              (7,7):[('1-10','1–10')],(7,8):[('"Milankovitch"','“Milankovitch”')]})
add_edits(17,{(7,8):[('10-30','10–30'),('40-50','40–50')],(16,2):[('1-2','1–2')],(16,4):[('10-40','10–40')],
              (16,5):[('15-25','15–25')],(18,3):[('0.5-1.0','0.5–1.0')]})
add_edits(18,{(28,5):[('< 3 mm','<3 mm')]})
add_edits(19,{(20,6):[('through-3 IX','through-31X')]})
add_edits(21,{(1,3):[('"Organic','“Organic')],(1,4):[('chemistry"','chemistry”')],(3,5):[('"Liesegang"','“Liesegang”')],
              (4,2):[('40X-l,0-20cm,-41X-l,0-5','40X-1, 0–20 cm, -41X-1, 0–5')],(4,3):[('1,0-5','1, 0–5')],
              (4,7):[('Subunit HB','Subunit IIB')],(7,13):[('50-80','50–80')],(7,14):[('262.7-317','262.7–317')],
              (7,16):[('200-262.7','200–262.7')],(7,17):[('317-408.9','317–408.9')],(7,19):[('-39 m','~39 m')]})
ADDITIONAL_ITALIC[11]={'h4':['Unit II'],'h8':['Subunit IIA'],'h13':['Subunit IIB']}
ADDITIONAL_ITALIC[17].update({'p16':['Zoophycos'],'p18':['Planolites','Skolithos','Zoophycos']})
ADDITIONAL_ITALIC[18]={'p25+26+27':['Zoophycos','Chondrites','Planolites'],'p28':['Planolites','Zoophycos','Chondrites']}
ADDITIONAL_ITALIC[19]={'p20':['Planolites','Chondrites','Zoophycos']}
ADDITIONAL_ITALIC[20].update({'p11':['Skolithos','Planolites'],'p12':['Planolites','and Chondrites','Zoophycos','Skolithos']})
ADDITIONAL_ITALIC[21]={'p1':['Zoophycos','Chondrites']}
for j,taxon in enumerate(['Gephyrocapsa oceanica','Reticulofenestra pseudoumbilicus','Discoaster quinqueramus','Craspedodiscus coscinodiscus','Helicosphaera ampliaperta'],1):
    ADDITIONAL_ITALIC[21]['q'+'+'.join(f'{b}:{j}' for b in range(17,22))]=[taxon]
ADDITIONAL_HYPHENS.update({(11,3,1),(11,12,1),(11,17,2),(18,26,2),(19,20,5),(20,11,1),(21,1,2),(21,10,1)})
complete_body(22,'r0 c1 n27 c28 n42 p43 p44 p45+46 p47+48+49 p50 p51 p52 f53','Tables 3 and 4 interiors')
complete_body(27,'r0 c161 p162 p163 h164 p165+166 p167 f168','Figure 18 interior')
complete_body(28,'r0 p1 p2+3 p4+5+6 h7 p8 p9+10 p11 p12 h13 p14 p15+16 p17 p18 p19 f20','')
add_edits(22,{(44,9):[('2,40','2, 40'),('2,120','2, 120')],(45,7):[('6,40','6, 40')],(47,4):[('discoastends','discoasterids')],
              (48,3):[('. the Pliocene','the Pliocene')],(49,4):[('4,50cm,and-21H-5,50cm.', '4, 50 cm, and -21H-5, 50 cm.')],
              (50,9):[('(NNlO/NNll)','(NN10/NN11)')],(51,5):[('5,60','5, 60')],(52,1):[('NN7-NN6','NN7–NN6')]})
add_edits(27,{(163,6):[('et al,','et al.,')],(166,3):[('-UH','-11H')]})
add_edits(28,{(1,9):[('{Globorotalia','(Globorotalia')],(4,2):[("Blow's (","Blow’s ("),("Blow's zonal","Blow’s zonal")],
              (5,1):[('NI8','N18')],(5,4):[('Globorotaliaplesiotumida','Globorotalia plesiotumida'),('NI7','N17')],
              (8,4):[('Dorcadospyrisalata','Dorcadospyris alata')],(8,6):[('{Collosphaera','(Collosphaera')],
              (10,1):[('Spongasterpentas','Spongaster pentas')],(12,8):[('"Sedimentation Rates"','“Sedimentation Rates”')],
              (14,2):[('846A-846D','846A–846D')],(19,1):[('2,90','2, 90'),('4,90','4, 90')],
              (19,2):[('-1 OH-CC','-10H-CC')],(19,3):[('theft praebergonii','the R. praebergonii'),('2,90','2, 90')]})
ADDITIONAL_ITALIC[22]={
    'p44':['Pseudoemiliania lacunosa','helicoliths','Gephyrocapsa','placoliths','P. lacunosa'],
    'p45+46':['Gephyrocapsa','Calcidiscus macintyrei','oceanica'],
    'p47+48+49':['Discoaster pentaradiatus','Discoaster quinqueramus','Discoaster berggreni','Discoaster neohamatus','Discoaster hamatus'],
    'p50':['Reticulofenestra','Coccolithus','Amaurolithus','D. berggreni'],'p51':['D. hamatus','Coccolithus miopelagicus','Catinaster coalitus'],
    'p52':['Discoaster bollii','Discoaster musicus','Discoaster brouweri','Discoaster kugleri','Cyclicargolithus floridanus','Sphenolithus heteromorphus','S. heteromorphus']}
ADDITIONAL_ITALIC[27]={'p162':['Reticulofenestra pseudoumbilicus'],
    'p163':['Sphenolithus heteromorphus','Helicosphaera ampliaperta','Discoaster deflandrei','Discoaster signus']}
ADDITIONAL_ITALIC[28]={
 'p1':['Neogloboquadrina-continuosa-acostaensis-humerosa- dutertrei','Globigerinoides sacculifer','Globigerinoides ruber','Globorotalia tumida','Globorotalia menardii','Globorotalia limbata','Pulleniatina','Globigerina bulloides','Neogloboquadrina pachyderma','Globorotalia inflata-Globorotalia puncticulata'],
 'p2+3':['Globigerinoides ruber','Globorotalia acostaensis'],'p4+5+6':['Globorotalia limbata','Sphaeroidinellopsis','Globorotalia tumida','Globorotalia plesiotumida','subdehiscens','Praeorbulina glomerosa circularis','Praeorbulina sicana','Globorotalia mayeri','Globoquadrina dehiscens','Globoquadrina venezuelana','Globigerinoides subquadratus','Globigerinoides sacculifer','Praeorbulina glomerosa circular ','Catpsydrax dissimilis'],
 'p8':['Collosphaera tuberosa','Dorcadospyris alata','Buccinosphaera invaginata','Stylatractus universus','C. tuberosa','D. alata'],
 'p9+10':['Amphirhopalum ypsilon','Spongaster tetras','Spongaster berminghami','Spongaster pentas'],
 'p12':['Didymocyrtis penultima','Solenosphaera omnitubus','Calocycletta caepa','Acrobotrys tritubus','Lithopera thornburgi','L. thornburgi'],
 'p15+16':['Actinocyclus ellipticus','Azpeitia nodulifer','Hemidiscus cuneiformis','Nitzschia fossilis','Nitzschia jouseae','Nitzschia marina','Nitzschia reinholdii','Pseudoeunotia doliolus','Rhizosolenia bergonii','Rhizosolenia praebergonii','Roperia tesselata','Thalassionema nitzschioides','parva','Thalassiosira convexa','Thalassiosira oestrupii','Thalassiothrix longissima'],
 'p17':['Actinocyclus ellipticus','Cestodiscus pulchellus','Coscinodiscus lewisianus','Craspedodiscus coscinodiscus','Crucidenticula nicobarica','Denticulopsis hustedtii','Hemidiscus cuneiformis','Nitzschia cylindrica','Nitzschia miocenica','Rossiella praepaleacea','Thalassionema nitzschioides','Thalassiosira yabei','Thalassiothrix longissima'],
 'p18':['P. doliolus','N. reinholdii','R. praebergonii'],'p19':['R. praebergonii']}
ADDITIONAL_HYPHENS.update({(27,166,5),(28,1,6),(28,4,6),(28,5,8),(28,5,16),(28,19,1)})
complete_body(42,'r0 c4 p5 h6 p7+8 h9 p10 h11 p12 f13','Figure 31 interior')
complete_body(43,'r0 c6 p7 h8 p9 h10 h11 p12 h13 p14 f15','Figure 32 interior')
complete_body(44,'r0 c27 p28 h29 p30 h31 p32 h33+34 p35 h36+37 p38 p39 p40 h41 p42 f43','Figure 33 interior')
complete_body(45,'r0 c14 p15 h16 p17 p18+19 f20','Figure 34 interior')
complete_body(46,'r0 c13 p14 h15 p16+17 p18 p19 f20','Figure 35 interior')
add_edits(42,{(10,4):[('203-207','203–207'),('272-283','272–283')],(10,5):[('312-322','312–322')],
              (10,6):[('40%-60%','40%–60%'),('"Biostratigraphy"','“Biostratigraphy”')],(12,2):[('m K','m • K')]})
add_edits(43,{(12,4):[('278.2-278.7','278.2–278.7'),('281-281.5','281–281.5')],
              (14,4):[('"Lithostratigraphy"','“Lithostratigraphy”')]})
add_edits(44,{(29,1):[('0-262','0–262'),('0-7','0–7')],(31,1):[('262-320','262–320'),('7.0-10.5','7.0–10.5')],
              (32,5):[('"Lithostratigraphy"','“Lithostratigraphy”')],(33,1):[('mbsf-base','mbsf–base')],
              (34,1):[('Ma-about','Ma–about')],(38,5):[('CORP AC','CORPAC')]})
add_edits(46,{(14,8):[('shows mat','shows that')]})
ADDITIONAL_ITALIC[44]={'p40':['in-situ']}
ADDITIONAL_HYPHENS.add((43,9,14))
complete_body(47,'r0 c5 p6 h7 h8 p9 p10+11 p12 p13 f14','Figure 36 interior')
complete_body(48,'r0 c12 p13 h14 p15 p16 p17 p18 f19','Figure 37 interior')
complete_body(49,'r0 c8 p9 h10 p11+12 p13 f14','Figure 38 interior')
complete_body(50,'r0 c12 c16 c17 n22+23 p24 p25 f26','Figures 39 and 40 interiors; Table 19 body and column headers')
complete_body(51,'r0 c18 c43 p19 p20+44 p45+46 f47','Figures 41 and 42 interiors')
complete_body(52,'r0 c10 c18 p19 p20 f21','Figures 43 and 44 interiors')
REF_GROUPS = ['p8+9:1-2','p9:3+10+11','p12+13:1','p13:2+14:1','p14:2+15:1-2',
              'p15:3+16:1','p16:2+17:1','p17:2+18:1-2','p18:3+19:1-5','p19:6+20:1',
              'p20:2+21:1','p21:2+22:1-3','p22:4+23:1-3','p23:4+24:1-2','p24:3+25:1-3',
              'p25:4+26:1-2','p26:3+27:1','p27:2+28:1-3','p28:4+29:1','p29:2+30:1-2',
              'p30:3+31:1-2','p31:3+32:1-2','p32:3+33:1-2','p33:3+34:1-2','p34:3+35']
complete_body(53,'r0 c4 p5 p6 h7 '+' '.join(REF_GROUPS)+' n36 f37','Figure 45 interior')
add_edits(47,{(6,5):[('848-854','848–854')],(10,4):[('77.4-391.2','77.4–391.2'),('75.4-390.5','75.4–390.5'),
             ('"Downhole Measurements"','“Downhole Measurements”')],(10,6):[('-0.7','−0.7')],(11,1):[('0-75.4','0–75.4')],
             (11,3):[('g/cm3','g/cm³')],(12,2):[('72.4-390.6','72.4–390.6')],(12,8):[('390.6-422.4','390.6–422.4')]})
add_edits(48,{(13,3):[('g/cm3','g/cm³')],(13,8):[('70-250','70–250')],(18,3):[('1-8','1–8')]})
add_edits(49,{(11,1):[("138's","138’s")],(12,4):[("APC's","APC’s")]})
add_edits(50,{(23,3):[('Chern','Chem')],(24,9):[('Zone-Hey','Zone–Hey')]})
add_edits(52,{(19,5):[('"dissolution event"','“dissolution event”')],(19,7):[('Miocene-a','Miocene–a')],
              (20,2):[('40-60','40–60')],(20,11):[('H2S','H₂S')]})
add_edits(53,{(6,3):[('10.5-7','10.5–7')],(9,1):[('Theyer, E,','Theyer, F.,')],(9,2):[('413-456','413–456')],
 (11,1):[('199-421','199–421')],(12,1):[('S. C,','S. C.,'),('I. T,','I. T.,')],(13,1):[('129-133','129–133')],
 (13,2):[('E. C,','E. C.,')],(14,1):[('218-232','218–232')],(15,2):[('99-140','99–140')],
 (16,1):[('493-497','493–497')],(17,1):[('433-394','433–394')],(18,2):[('Lett,','Lett.,'),('229-235','229–235')],
 (19,5):[('603-613','603–613')],(20,1):[('Bull,','Bull.,'),('1404-1420','1404–1420')],(21,1):[('1385-1403','1385–1403')],
 (21,2):[('J. C,','J. C.,')],(22,3):[('623-632','623–632')],(23,1):[('andEthington','and Ethington')],
 (23,3):[('87-110','87–110')],(23,4):[('I. T,','I. T.,'),('S. C,','S. C.,'),('J. C,','J. C.,')],
 (24,2):[('Chern. Geol.','Chem. Geol.'),('349-375','349–375')],(24,3):[('J. C,','J. C.,')],(25,3):[('633-638','633–638')],
 (26,2):[('739-785','739–785')],(26,3):[('Menke, W,','Menke, W.,')],(27,1):[('/. Geophys.','J. Geophys.'),('4807-4818','4807–4818')],
 (28,2):[('Theyer, E,', 'Theyer, F.,')],(28,3):[('947-970','947–970')],(29,1):[('Oceanographic','oceanographic'),('761-764','761–764')],
 (30,2):[('1705—1713','1705–1713')],(31,2):[('321-325','321–325')],(32,2):[('434-437','434–437')],
 (33,2):[('2303-2310','2303–2310')],(35,2):[('L. C,','L. C.,')],(35,3):[('175-235','175–235')]})
ADDITIONAL_ITALIC[47]={'p10+11':['in-situ'],'p12':['in-situ']}
ADDITIONAL_ITALIC[48]={'p13':['Thomas Washington']}
REF_ITALICS=[
 ['In Mayer|0:2','Init. Repts. DSDP'],['Proc. First Int. Conf. Planktonic Microfossils'],['Nature'],
 ['In Hill|0:2','The Sea'],['In Kaplan|0:2','Natural Gases in Marine Sediments'],['Nature'],['Annu. Rev. Earth Planet. Sci.'],
 ['Earth Planet. Sci. Lett.'],['In Aubouin|0:2','Init. Repts. DSDP'],['Geol. Soc. Am. Bull.'],['Geol. Soc. Am. Bull.'],
 ['In Suess|0:2','Proc. ODP, Sci. Results'],['In Zenger|0:2','Concepts and Models of Dolomitization'],
 ['Chem. Geol.'],['In Suess|0:2','Proc. ODP, Sci. Results'],['In Farinacci|0:2','Proc. 2nd Planktonic Conf. Roma'],
 ['J. Geophys. Res.'],['In Mayer|0:2','Init. Repts. DSDP'],['Science'],['Geochim. Cosmochim. Acta'],
 ['Mar. Micropaleontol.'],['Nature'],['Geochim. Cosmochim. Acta'],['In Van|0:2','Final Repts., IGCP Project'],
 ['In Duncan|0:2','Proc. ODP, Sci. Results']]
ADDITIONAL_ITALIC[53]=dict(zip(REF_GROUPS,REF_ITALICS,strict=True))
# The publisher text layer omitted these running heads and folios. Negative block
# numbers are edition-local scan anchors, never publisher block or line ordinals.
MARGINS={
    10:((53,28,84,34),(53,760,67,767)),13:((496,28,527,35),(516,760,529,768)),
    23:((761,498,767,529),(28,515,35,528)),24:((761,50,767,81),(30,50,37,64)),
    25:((500,29,531,36),(518,760,532,768)),63:((499,29,530,36),(517,758,530,766)),
    68:((56,32,87,38),(55,759,69,767)),69:((497,31,528,38),(517,761,531,768))}
for n,exclusion in [(10,'Figure 5 interior'),(13,'Figure 7 interior'),(23,'Table 5 body and column headings'),
                    (24,'Table 6 body and column headings'),(25,'Figure 18 interior'),
                    (63,'log-summary interior'),(68,'log-summary interior'),(69,'log-summary interior')]:
    complete_body(n,'r-1 '+CAPTIONS[n]+' f-2',exclusion)
complete_body(54,'r0 n1 n2 c17 f18','Figure 46 interior')
complete_body(57,'r0 c1:1 c1:2 n98+99:1-2 n99:3+100 f101','Tables 20 and 21 bodies and column headings')
add_edits(57,{(98,1):[('0-12','0–12')],(99,1):[('12-17','12–17')],(99,3):[('-O.75','-0.75')]})
