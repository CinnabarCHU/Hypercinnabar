function [retval,id] = analyzer(params,id)
% wtcsignif.analyzer parameters: mccount ar1 dt n pad dj s0 j1 mother cutoff.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/wtcsignif.m
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/wavelet.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('wtcsignif-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
mccount = p.mccount;
ar1 = p.ar1;
dt = p.dt;
n = p.n;
pad = p.pad;
dj = p.dj;
s0 = p.s0;
j1 = p.j1;
mother = p.mother;
cutoff = p.cutoff;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/wavelet/wtcsignif.m:L73-L78
ms=s0*(2^(j1*dj))/dt; %maxscale in units of samples
n=ceil(ms*6);

warned=0;
%precalculate stuff that's constant outside the loop
d1=rednoise(n,ar1(1),1);
%% End copied source
[W1,period,scale,coi] = wavelet(d1,dt,pad,dj,s0,j1,mother,-1);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/wavelet/wtcsignif.m:L80-L89
outsidecoi=zeros(size(W1));
for s=1:length(scale)
    outsidecoi(s,:)=(period(s)<=coi);
end
sinv=1./(scale');
sinv=sinv(:,ones(1,size(W1,2)));

if mccount<1
    wtcsig=scale';
    wtcsig(:,2)=.71; %pretty good
%% End copied source
    r=struct('wtcsig',wtcsig);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/wavelet/wtcsignif.m:L90-L113
    return
end

sig95=zeros(size(scale));

maxscale=1;
for s=1:length(scale)
    if any(outsidecoi(s,:)>0)
        maxscale=s;
    else
        sig95(s)=NaN;
        if ~warned
            warning('Long wavelengths completely influenced by COI. (suggestion: set n higher, or j1 lower)'); warned=1;
        end
    end
end

%PAR1=1./ar1spectrum(ar1(1),period');
%PAR1=PAR1(:,ones(1,size(W1,2)));
%PAR2=1./ar1spectrum(ar1(2),period');
%PAR2=PAR2(:,ones(1,size(W1,2)));

nbins=1000;
wlc=zeros(length(scale),nbins);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/wavelet/wtcsignif.m:L117-L119
for ii=1:mccount
    d1=rednoise(n,ar1(1),1);
    d2=rednoise(n,ar1(2),1);
%% End copied source
[W1,period,scale,coi] = wavelet(d1,dt,pad,dj,s0,j1,mother,-1);
[W2,period,scale,coi] = wavelet(d2,dt,pad,dj,s0,j1,mother,-1);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/wavelet/wtcsignif.m:L123-L133
    sWxy=smoothwavelet(sinv.*(W1.*conj(W2)),dt,period,dj,scale);
    Rsq=abs(sWxy).^2./(smoothwavelet(sinv.*(abs(W1).^2),dt,period,dj,scale).*smoothwavelet(sinv.*(abs(W2).^2),dt,period,dj,scale));

    for s=1:maxscale
        cd=Rsq(s,find(outsidecoi(s,:)));
        cd=max(min(cd,1),0);
        cd=floor(cd*(nbins-1))+1;
        for jj=1:length(cd)
            wlc(s,cd(jj))=wlc(s,cd(jj))+1;
        end
    end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/wavelet/wtcsignif.m:L135-L151
end


for s=1:maxscale
    rsqy=((1:nbins)-.5)/nbins;
    ptile=wlc(s,:);
    idx=find(ptile~=0);
    ptile=ptile(idx);
    rsqy=rsqy(idx);
    ptile=cumsum(ptile);
    ptile=(ptile-.5)/ptile(end);
    sig95(s)=interp1(ptile,rsqy,.95);
end
wtcsig=[scale' sig95'];

if any(isnan(sig95))&(~warned)
    warning('Sig95 calculation failed. (Some NaNs)')
%% End copied source
end
r = struct();
r.wtcsig = wtcsig;
end
