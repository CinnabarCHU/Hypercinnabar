"""Physical reading order and verified glyph changes for the other Site 846 leaves."""
def layout(*items):
    roles = dict(r="running_header", h="heading", b="body", c="caption", n="notice",
                 a="byline", f="folio", t="footnote", x="reference")
    return [(roles[item[0]], item[1:]) for item in items]

PLAN = {
    1: layout("n0-1","h2-3","a4-7","h8","b9-14","b15-22","h23","b24-46",
              "h47","b48-63","b68-78","b79-108","b109-118","t64-65","t66-67","f119"),
    2: layout("r0","c1","n623-624","b625-642","b643-661","b662-673","b674-687","b688-698","f699"),
    4: layout("r0","c1","n911-915","n916","f917"),
    7: layout("r0","c1-2","n406-409","n410-411","c403-405","n576-577","f578"),
    8: layout("r0","c48-50","f51"),
    9: layout("r2","c48-52","b53-56","b57-71","b72-80","f81"),
    10:layout("r0","c47-50","f51"), 11:layout("r0","c47","f48"),
    12:layout("r0","b1-3","b4-9","b10-19","b20-29","h30","b31-45","b46-70","b71-91",
              "h92","h93","b94-116","h117","b118-125","b126-145","f146"),
    13:layout("r0","c154-155","b156-163","h164","b165-180","b181-189","b190-200","f201"),
    14:layout("r0","c18-23","b24-25","b26-53","b54-61","f62"),
    15:layout("r5","c28-33","b34-68","f69"),
    16:layout("r0","c3-6","c24-27","b28-48","h49","b50-69","h70","b71-86","f87"),
    17:layout("r0","h1","x2-3","x4-5","x6-9","x10-11","x12-13","x14","x15-17","x18-21",
              "x22-24","x25-27","x28-32","x33-34","x35-36","x37-39","x40-41","x42-43",
              "x44-46","x47-49","x50-51","x52-54","x55-57","x58-60","x61-63","x64-67",
              "x68-69","x70-72","x73-76","x77-79","x80-81","x82-85","x86-89","x90-92",
              "x93-96","x97-98","t99-101","n102","n103","n104","f105"),
    18:layout("r0","c1-3","n262-263","c264","n365-366","f367"),
    19:layout("r0","c1-2","n712-717","f718"),
}
OVERLAY = {2: (1,), 4: (3,), 7: (5,6), 18:(7,8), 19:(9,)}
FIGS = {5:(1,),6:(2,),8:(3,),9:(4,),10:(5,),11:(6,),13:(7,),14:(8,),15:(9,),16:(10,11)}
SCOPE={}
for p in PLAN:
    scope = "Complete printed article text, captions, notes and running matter on this leaf."
    if p in OVERLAY:
        scope += " Table " + "/".join(str(t) for t in OVERLAY[p]) + " cell contents outside this reading; native text remains accessible."
    if p in FIGS:
        scope += " Figure " + "/".join(str(f) for f in FIGS[p]) + " interiors with axes and labels outside the transcription."
    SCOPE[p]=scope
CARRY = {
    1:"Final word is divided between pp. 337 and 338 (diox-/ide).",
    2:"First text completes the word continuing from p. 337. Last paragraph continues on p. 339.",
    4:"Table leaf between pp. 339 and 341.", 7:"Table leaf interrupts the narrative continuing from p. 342.",
    8:"Figure leaf. The narrative from p. 342 resumes on p. 345.",
    9:"Opens with the sentence continuing from p. 342. Last sentence resumes on p. 348.",
    10:"Figure leaf. Narrative from p. 345 resumes on p. 348.",11:"Figure leaf. Narrative resumes on p. 348.",
    12:"Starts with the reference continuing from p. 345. Last sentence continues on p. 349.",
    13:"Opens with the final alternative from p. 348. Last paragraph continues on p. 350.",
    14:"Opens with the sentence continuing from p. 349. Last sentence continues on p. 351.",
    15:"Opens with the parenthesized figure reference continuing from p. 350. Last sentence continues on p. 352.",
    16:"Opens with the obliquity discussion continuing from p. 351. Conclusions and acknowledgments end on this leaf.",
    17:"References and submission details in full.",18:"Printed time series and spectral results.",19:"Printed Site 677 data listing and its note.",
}
SAME_LINE={
    1:{3,5,6,7,13,16,22,25,29,32,36,39,61,82,84,87,92,94,99,100,108},
    2:{634,635,638,639,653,654,685},12:{15,17,40,42,47,49,52,57,60,65,72,76,78,80,83,100,145},
    13:{168},14:{19,27,31,36,41,56,61},15:{29,39,47,49,52,56},16:{25,32,37,46,56,57},
    18:{2,3},19:{714,715},
}
# Digit/letter distinctions, footnote markers, and symbols inspected on the image.
CHANGES={
 1:{3:[("1","¹")],5:[("2 ","² ")],6:[("2 ","² ")],7:[("2","²")],13:[("EaruYs","Earth’s")],
    27:[("et al,","et al.,")],44:[("EartiYs","Earth’s")],
    46:[("3°5.8O'S, 90°49.07'W","3°5.80′S, 90°49.07′W")],61:[("3 samples","³ samples")],
    64:[("Pisias,","¹ Pisias,")],66:[("2 University","² University")],82:[("I8O","¹⁸O")],
    94:[("I3C","¹³C")]},
 2:{632:[("-2.20%","−2.20%")],687:[("45-47 cm","45–47 cm")]},
 4:{915:[("δ O","δ¹⁸O")]},7:{406:[("δ O","δ¹⁸O")],407:[("δ ' C","δ¹³C")]},
 9:{53:[("stage Kl","stage K1")],68:[("purp°se","purpose")]},
 10:{48:[("baling","having")],49:[("saπspfe","sample"),("inteΦolation","interpolation")],
     50:[("asaty•sès","analysis")]},
 12:{6:[("Stage Gl","Stage G1")],7:[("3 A","3A")],21:[("Gil to Gi22","Gi1 to Gi22")],
     24:[("stage NI","stage N1")],26:[("and Sil","and Si1")],28:[("TI to T8","T1 to T8"),("Stage TGI","Stage TG1")],
     39:[("in the 6","in the δ")],66:[("65 °N","65°N")]},
 13:{174:[("5 52A","552A")],190:[("stage Gl7","stage G17")],200:[("203-204","203–204")]},
 14:{30:[("benthic 6","benthic δ")],39:[("DS DP","DSDP")],40:[("fluctuations in 5","fluctuations in δ")]},
 15:{29:[("1 3θ","¹³O"),("frofn","from")],34:[("deglàciation","deglaciation")],40:[("65 °N","65°N")],
     47:[("same Core","same core")]},
 16:{31:[("the 5","the δ")],80:[("Ray mo","Raymo")]},
 17:{1:[("REFERENCES","REFERENCES*")],2:[("1988./Voc. ODP, Init.","1988. Proc. ODP, Init.")],
     7:[("Snelling, NJ.","Snelling, N.J.")],10:[("CM.","C.M.")],13:[("Sect)","Sect.)")],
     14:[("C,","C.,"),("J. Geol,","J. Geol.,")],17:[("RL","RI.")],20:[("Janecek, T,","Janecek, T.,")],
     25:[("FJ.","F.J.")],31:[("Antarc. Res. Sen","Antarc. Res. Ser.")],50:[("T, et al,","T., et al.,")],
     52:[("Rugh, W,","Rugh, W.,"),("Lopez, C,","Lopez, C.,")],54:[("CO2","CO₂")],60:[("413^446","413–446")],
     62:[("CO2","CO₂")],66:[("Ruddiman, W,","Ruddiman, W.,"),("et al,","et al.,")],80:[("818O","δ¹⁸O")],
     81:[("Clint. Change","Clim. Change")],84:[("I05","10⁵"),("I06","10⁶")],88:[("CO2","CO²")],
     94:[("Valuer","Vallier")],99:[("Abbreviations","* Abbreviations")]},
 18:{2:[("1 8 θ","¹⁸O")],3:[("I 3C","¹³C")],262:[("δ O","δ¹⁸O")]},
}

# One cell may span two/three native segments. Empty tuples are observed blank
# cells in the print witness, including continuations of vertically shared labels.
T8 = []
field_names = (((),(290,),(330,),(355,)), ((),(276,),(291,),(305,),(316,),(331,),(341,),(356,)))
T8.extend(("table_header", row) for row in field_names)
p41 = [306,307,308,309,310,311,312,None,313,314,None,None,315]
p23 = [332,333,334,335,336,337,338,None,339,None,None,None,340]
p19 = [357,358,359,360,361,None,362,363,None,None,None,None,364]
labels = {0:(265,266),4:(267,268,269),8:(270,271,272),12:(273,274,275)}
def cell(idx):
    return (idx,) if idx is not None else ()
for row in range(13):
    T8.append(("table_row", (labels.get(row,()),(277+row,),(292+row,),cell(p41[row]),
               (317+row,),cell(p23[row]),(342+row,),cell(p19[row]))))
t8_spec = {" ".join(str(n) for field in cells for n in field):cells for role,cells in T8}
PLAN[18][4:4]=[(role, " ".join(str(n) for field in cells for n in field)) for role,cells in T8]
SCOPE[18]="Complete captions and printed notes to Tables 7 and 8, the two-tier Table 8 header, all thirteen Table 8 rows, running heading and folio. Table 7 printed excerpt cells outside the reading."
for n in (312,333,334,335,337,339,358,359):
    CHANGES[18][n]=[("+","±")]
CHANGES[18][289]=[("3.5^.5","3.5–4.5")]

def table8_row(s,readings):
    numbers=[n for field in t8_spec[s] for n in field]
    by_ordinal=dict(zip(numbers,readings))
    fields=[]
    for field in t8_spec[s]:
        if field in ((267,268,269),(270,271,272),(273,274,275)):
            terms=[by_ordinal[field[0]]+by_ordinal[field[1]],by_ordinal[field[2]]]
        else:
            terms=[by_ordinal[n] for n in field]
        fields.append(" ".join(terms))
    return fields

def reflow_text(lines,pn,spec):
    text=""
    for line in lines:
        if text.endswith("–"):
            text+=line
        elif text.endswith("-"):
            keep=text.endswith(("138-846B-","one-"))
            text=(text if keep else text[:-1])+line
        elif text.endswith("/"):
            text+=line
        else:
            text=(text+" "+line).strip()
    # Leading tab denotes a genuinely blank, vertically shared table field.
    if pn==18 and len(lines)==1 and "\t" in lines[0]:
        return lines[0]
    return text
def print_styles(text,role,pn,spec):
    import re
    terms = []
    if pn==17 and role=="reference":
        terms = ["In","Proc. ODP, Init. Repts.","Proc. ODP, Sci. Results","Quat. Sci. Rev.","J. Geol.",
                 "The Chronology of the Geological Record","Chem. Geol. (Isotope Geosci. Sect.)",
                 "Geol. Soc. Am. Bull.","Earth Planet. Sci. Lett.","The Antarctic Paleoenvironment: A Perspective on Global Change",
                 "Climate Change: The IPCC Scientific Assessment","Spectral Analysis and Its Applications",
                 "Paleoceanography","Nature","Init. Repts. DSDP","Science","Philos. Trans. R. Soc. London",
                 "Trans. R. Soc. Edinburgh, Earth Sci.","Clim. Change","Quat. Res. (N.Y.)",
                 "The Carbon Cycle and Atmospheric CO²: Natural Variations Archean to Present",
                 "GEOMAR Rep."]
    if pn==1 and spec=="0-1":
        terms=["Proceedings of the Ocean Drilling Program, Scientific Results"]
    if pn==1 and spec=="64-65":
        terms=["Proc. ODP, Sci. Results"]
    if pn==17 and spec=="99-101":
        terms=["Chemical Abstracts Service Source Index"]
    result=[]
    for term in terms:
        for m in re.finditer(r'(?<![\w])'+re.escape(term)+r'(?![\w])',text):
            result.append(dict(begin=m.start(),end=m.end(),style="italic"))
    if pn==17 and role=="notice":
        result.append(dict(begin=0,end=len(text),style="bold"))
    if pn==17 and role in ("heading","footnote"):
        i=text.index("*")
        result.append(dict(begin=i,end=i+1,style="superscript"))
    if pn in (9,14,15) and role=="caption":
        for m in re.finditer(r"\b[ABCD]\.(?= [1-5])",text):
            result.append(dict(begin=m.start(),end=m.end(),style="bold"))
    return result
