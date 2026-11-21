"""Pack numerical inputs losslessly and recompute the author's orbital analyses."""
from pathlib import Path
import argparse, io, lzma
import numpy as np
from scipy.io import loadmat, savemat
import author_methods as author

NAMES = ['ZB18a','ZB20a','ZB20b','La10a','La10b','La10c','La2004','La10d']

def pack(source, reference, lad, target):
    raw={}
    for i,name in enumerate(NAMES):
        if i<3:
            a=np.loadtxt(source/(name+'.dat'), comments='%')
        elif i<6:
            a=np.loadtxt(source/('La2010'+name[-1]+'_ecc3L.dat'))
        elif i==6:
            a=loadmat(reference/'data/La04.mat')['data']
        else:
            a=np.loadtxt(lad)
        age=np.abs(a[:,0]); e=a[:,1]
        dt=np.round(np.median(np.diff(age)),5)
        assert np.array_equal(age,np.round(np.arange(len(age))*dt,5))
        scale=10**9
        quant=np.rint(e*scale).astype(np.int32)
        assert np.array_equal(quant/scale,e)
        raw[name+'_de']=np.diff(quant,prepend=np.int32(0)).astype(np.int32)
        raw[name+'_dt']=dt
    zb=np.loadtxt(source/'ems-plan3.dat',skiprows=17,usecols=(0,2,4))
    t=np.abs(zb[:,0])/365.25/1000
    use=((t>=37990)&(t<=67010))|(t==0)
    raw['zb_elements']=zb[use]
    la=np.loadtxt(source/'La2010c_alkhqp3.dat',usecols=(0,4))
    t=np.abs(la[:,0]);raw['la_elements']=la[((t>=37990)&(t<=67010))|(t==0)]
    buf=io.BytesIO();np.savez(buf,**raw);target.write_bytes(lzma.compress(buf.getvalue(),preset=5))

def calculate(bundle,target):
    raw=np.load(io.BytesIO(lzma.decompress(bundle.read_bytes())),allow_pickle=False)
    out={}
    for name in NAMES:
        e=np.cumsum(raw[name+'_de'],dtype=np.int64)/1e9
        dt=float(raw[name+'_dt']); age=np.round(np.arange(len(e))*dt,5)/1000
        t=-age[::-1]; y=e[::-1]
        filt=author.bandpass(y,np.median(np.diff(t)),1.8,5.5)
        # Actual 2 Myr Gaussian filter in the comparison cited for panel 8a.
        # Define +/-60% in frequency with half-amplitude edges; save this convention.
        f=np.fft.rfftfreq(len(e),d=dt/1000)
        transfer=np.exp(-np.log(2)*((f-.5)/.3)**2);transfer[0]=0
        gauss=np.fft.irfft(np.fft.rfft(e-e.mean())*transfer,n=len(e))
        use=(age>=40)&(age<=65)
        out[name]=np.column_stack((age[use],e[use],(4.2*filt+y.mean())[::-1][use],gauss[use]))
    zb=raw['zb_elements'];la=raw['la_elements']
    inp=[(np.abs(zb[:,0])/365.25/1000,zb[:,1]*np.sin(zb[:,2]/(180/np.pi))), (np.abs(la[:,0]),la[:,1])]
    for i,(t,h) in enumerate(inp):
        tw,s,w,per,coi=author.prepare_cwt(t,h)
        arcs=author.black_arc(tw,per,w)
        xx=unique_indices(len(tw),3)
        out['h'+str(i+1)]=dict(t=tw[xx]/1000,signal=np.interp(tw,t,h)[xx],scale=s,period=per,
            logpower=np.log2(np.abs(w[:,xx])**2).astype('float32'),coi=np.interp(tw[xx],tw[:len(coi)],coi),
            arc_age=np.vstack([a for a,b in arcs]),arc_period=np.vstack([b for a,b in arcs]))
    # Extend scale grid for the 20-100 kyr crop in panel 8b. Same Morlet routine.
    old=author.S0_FAC
    try:
        author.S0_FAC=3
        tw,s,w,per,_=author.prepare_cwt(*inp[0])
    finally:
        author.S0_FAC=old
    xx=unique_indices(len(tw),3)
    out['h8']=dict(t=tw[xx]/1000,period=per,logpower=np.log2(np.abs(w[:,xx])**2).astype('float32'))
    savemat(target,out,do_compression=True)

def unique_indices(n,step):
    return np.unique(np.r_[np.arange(0,n,step),n-1])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--supp-data',type=Path);p.add_argument('--reference',type=Path);p.add_argument('--la2010d',type=Path);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.supp_data: pack(a.supp_data,a.reference,a.la2010d,a.bundle)
    calculate(a.bundle,a.output)
