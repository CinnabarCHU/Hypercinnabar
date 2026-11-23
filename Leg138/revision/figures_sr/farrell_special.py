"""Additional Farrell et al. panels, with explicit source and processing choices."""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

SOURCE = {
    2: (4, ["SR.C35.APPENDIXB"], "age_ma|opal_pct|opal_source"),
    26: (33, ["SR.C35.APPENDIXB"], "hole|age_ma|opal_mar"),
    27: (34, ["SR.C35.APPENDIXA","SR.C35.APPENDIXB"],
         "hole|age_ma|lsr_cm_kyr|caco3_pct|caco3_mar|dbd_g_cm3|opal_pct|opal_mar"),
}
CAPTIONS = {
    2: "Comparison of Site 847 %opal data from three laboratories shows the same general pattern, but offsets in absolute values, as discussed in the text.",
    26: "Opal MAR records from the Galápagos region (Sites 846) and the equatorial zone of the 110°W transect (Site 850) show the shift in the locus of maximum opal accumulation at 4.4 Ma. At that time, which has been associated with the final closure of the Panamanian seaway, opal MARs declined sharply in the Pacific Basin and increased in the Galápagos region. The records have been smoothed with a five-point moving average. Histogram (inset) shows the opal shift between 3–4 and 4–5 Ma, when the data are expressed as 1-m.y. averages.",
    27: "Sedimentary records show that the “opal shift” at 4.4 Ma (F) resulted from a relative increase in both sedimentation rate (A) and opal percentage (E) at Site 846 compared to Site 850. CaCO₃ MAR variations (C) at the two sites have remained similar since 7 Ma. No intersite CaCO₃ MAR difference began at 4.4 Ma because the relative decrease in sedimentation rates at Site 850 was offset by relatively higher %CaCO₃ (B) and DBD (D) values at Site 850.",
}
PANELS = [
    ("lsr_cm_kyr","A","Sedimentation rate (cm/k.y.)", (0,12),2),
    ("caco3_pct","A","%CaCO₃",(0,90),20),
    ("caco3_mar","A","CaCO₃ MAR (g/cm² k.y.)",(0,5),1),
    ("dbd_g_cm3","A","Dry bulk density (g/cm³)",(.3,1),.1),
    ("opal_pct","B","%opal",(0,50),10),
    ("opal_mar","B","Opal MAR (g/cm² k.y.)",(0,2),.5),
]


def five_point(x,y):
    return x[2:-2],np.convolve(y,np.ones(5)/5,"valid")


def draw(data,pairs,caption,save):
    fig,ax=plt.subplots(figsize=(5.8,3.72))
    fig.subplots_adjust(left=.13,right=.96,top=.95,bottom=.22)
    ds="SR.C35.APPENDIXB"
    x,y,ordinal=pairs(data,ds,"age_ma","opal_pct",847)
    source=np.array([data[ds][int(n)-1][1]["opal_source"] for n in ordinal])
    for lab,color,lw,style,marker in [("Murray",".3",.45,"-",None),
            ("Janecek","black",.9,"-",None),("Levitan","black",0,"none","s")]:
        sel=(source==lab)&(x<=3)
        ax.plot(x[sel],y[sel],lw=lw,ls=style,marker=marker,ms=2.4,color=color,
                label=lab+(" (this study)" if lab=="Janecek" else " et al. (this volume)"))
    ax.set(xlim=(0,3),ylim=(0,51),xlabel="Age (Ma)",ylabel="%opal")
    ax.text(.985,.97,"Site 847",transform=ax.transAxes,ha="right",va="top",fontsize=8)
    ax.tick_params(direction="in",top=True,right=True,labelsize=7)
    ax.legend(loc="upper left",fontsize=6.3,edgecolor="black",framealpha=1)
    caption(fig,"Figure 2. "+CAPTIONS[2],width=85,size=7.2)
    save(fig,"SR.C35.FIGURE2")
    fig,ax=plt.subplots(figsize=(6.15,4.5))
    fig.subplots_adjust(left=.13,right=.965,top=.97,bottom=.275)
    inset=ax.inset_axes([.066,.585,.36,.39])
    for j,site in enumerate((846,850)):
        x,y,_=pairs(data,ds,"age_ma","opal_mar",site)
        a,b=five_point(x,y)
        ax.plot(a,b,ls="-" if j==0 else (0,(.9,1.45)),color="black",lw=.58,
                label=f"Site {site}")
        means=[y[(x>=i)&(x<i+1)].mean() for i in range(12)]
        inset.bar(np.arange(12)+(-.22 if j==0 else .22),means,.44,edgecolor="black",
                  linewidth=.36,color="white" if j==0 else ".62",label=str(site))
    ax.set(xlim=(0,12),ylim=(0,2),xlabel="Age (Ma)",ylabel="opal MAR (g/cm² k.y.)")
    ax.xaxis.set_major_locator(MultipleLocator(1));ax.yaxis.set_major_locator(MultipleLocator(.5))
    ax.tick_params(direction="in",top=True,right=True,labelsize=7.2)
    ax.legend(loc="upper right",fontsize=6.8,frameon=False)
    ax.annotate("higher MAR at Galápagos Site 846 after 4.4 Ma",
                xy=(4.4,.24),xytext=(5.1,.025),ha="center",fontsize=6.3,
                arrowprops={"arrowstyle":"-|>","lw":.6,"color":"black"})
    ax.set_xlabel("Age (Ma)",fontsize=8);ax.set_ylabel("opal MAR (g/cm² k.y.)",fontsize=8)
    inset.set(xlim=(-.5,11.5),ylim=(0,1.4),xticks=np.arange(12))
    inset.set_xticklabels([f"{i}–{i+1}" for i in range(12)],rotation=90)
    inset.yaxis.set_major_locator(MultipleLocator(.4))
    inset.set_xlabel("Age interval (Ma)",fontsize=4.9,labelpad=1)
    inset.set_ylabel("opal MAR (g/cm² k.y.)",fontsize=4.5,labelpad=1)
    inset.tick_params(labelsize=4.4,length=1.5,pad=1)
    inset.legend(fontsize=4.2,frameon=False,loc="upper left")
    caption(fig,"Figure 26. "+CAPTIONS[26],width=98,size=6.9)
    save(fig,"SR.C35.FIGURE26")
    fig,axes=plt.subplots(3,2,figsize=(7.5,5.9),sharex=True)
    fig.subplots_adjust(top=.97,left=.10,right=.98,bottom=.18,hspace=.11,wspace=.22)
    for i, (ax,(field,appendix,ylabel,ylim,step)) in enumerate(zip(axes.T.ravel(),PANELS)):
        for j,site in enumerate((846,850)):
            x,y,_=pairs(data,"SR.C35.APPENDIX"+appendix,"age_ma",field,site)
            a,b=five_point(x,y)
            ax.plot(a,b,ls="-" if j==0 else (0,(.9,1.4)),color="black",lw=.57,
                    label=f"Site {site}")
        ax.set(xlim=(0,12),ylim=ylim)
        ax.xaxis.set_major_locator(MultipleLocator(2));ax.yaxis.set_major_locator(MultipleLocator(step))
        ax.tick_params(direction="in",top=True,right=True,labelsize=6.4,pad=1,length=2)
        ax.set_ylabel(ylabel,fontsize=6.7,labelpad=2)
        ax.text(-.15,.95,chr(65+i),ha="center",fontsize=8,fontweight="bold",transform=ax.transAxes)
        if i==0:ax.legend(fontsize=6,loc="upper right",frameon=False)
        if i%3==2:ax.set_xlabel("Age (Ma)",fontsize=7.1,labelpad=1)
    caption(fig,"Figure 27. "+CAPTIONS[27],width=112,size=7.2,x=.075)
    save(fig,"SR.C35.FIGURE27")
