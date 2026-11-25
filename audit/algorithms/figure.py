"""Render the comparison from the algorithm-evidence Actions artifact."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.stats import binomtest

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("evidence", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
folder = args.evidence
report = json.loads((folder/"summary.json").read_text())
mpl.rcParams.update({"svg.fonttype":"none", "svg.hashsalt":"acycle-audit-v1",
                     "axes.spines.top":False, "axes.spines.right":False,
                     "font.size":9, "axes.titlesize":10})
fig, axes = plt.subplots(1, 3, figsize=(12.3,3.85), layout="constrained")

def read(name, skip=0):
    return np.loadtxt(folder/name, delimiter=",", skiprows=skip)

colors = ["#263c52", "#b84e2c", "#217c79"]
ax = axes[0]
for f, label, color in zip(["master-lomb.csv","master-mtm-pad1.csv","master-mtm-pad5.csv"],
        ["Lomb + 3× Hanning","MTM, NFFT = N","MTM, NFFT = 5N"], colors):
    x = read(f)
    nearby = (x[:,0]>=.55) & (x[:,0]<=2.1)
    ax.plot(x[nearby,0], x[nearby,1]/x[nearby,2], color=color, label=label, lw=1.6)
ax.axvline(1/.81,color=".5",ls=":",lw=1.2)
ax.set(xlabel="Frequency (cycles/m)", ylabel="Power / fitted background",
       title="Lavernock magnetic susceptibility")
ax.legend(frameon=False, fontsize=8, loc="upper right")

ax = axes[1]
null = report["null_calibration"]
labels = ["0.4, 1×","0.4, 5×","0.8, 1×","0.8, 5×"]
for arr, dx, color, label in [
    (null["production_background_counts"],-.09,colors[1],"MTM + fitted SWA"),
    (null["known_background_counts"],.09,colors[0],"MTM + known AR(1)")]:
    for i,k in enumerate(np.asarray(arr).ravel()):
        n = null["trials"]
        ci = binomtest(int(k),n).proportion_ci(method="wilson")
        val = k/n
        ax.errorbar(i+dx,val*100,yerr=[[100*(val-ci.low)],[100*(ci.high-val)]],
                    fmt="o",color=color,capsize=3,label=label if i==0 else None)
ax.axhline(5,color=".36",ls="--",lw=1)
ax.set_xticks(range(4),labels)
ax.set(xlabel="AR(1) coefficient, NFFT / N", ylabel="Records with ≥1 discovery (%)",
       title="Null simulations, nominal FDR 5%", ylim=(0,30),xlim=(-.4,3.4))
ax.legend(frameon=False,fontsize=8,loc="upper left")

ax = axes[2]
for f, skip, color, label in [("odp926b-astrochron.csv",1,colors[0],"Meyers / astrochron 1.8"),
                             ("odp926b-acycle.csv",0,colors[1],"Acycle / recovered v2.8")]:
    a = read(f,skip)
    ax.plot(a[:,0],a[:,3],color=color,label=label,lw=1.6)
    i = np.argmax(a[:,3]);ax.plot(a[i,0],a[i,3],"o",color=color,ms=4)
ax.axvline(3.02,color=".5",ls=":",lw=1.2)
ax.set(xlabel="Sedimentation rate (cm/kyr)",ylabel=r"$R^2_{\rm opt}$",
       title=r"ODP 926B benthic $\delta^{18}$O")
ax.legend(frameon=False,fontsize=8)
for ax in axes:
    ax.grid(axis="y",alpha=.17)
args.output.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(args.output, metadata={"Date":None} if args.output.suffix==".svg" else None)

if args.output.suffix == ".svg":
    xml = args.output.read_text()
    args.output.write_text("\n".join(line.rstrip() for line in xml.splitlines()) + "\n")
