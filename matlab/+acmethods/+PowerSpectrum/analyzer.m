function [retval, id] = analyzer(params, id)
% PowerSpectrum.analyzer parameters: data method nw(MTM) padtimes(MTM/Periodogram) nzeropad(MTM/Periodogram) pd(Lomb) fmax(Lomb).
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/spectrum.m#L422
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/spectrum.m#L1125
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/spectrum.m#L1512
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('PowerSpectrum-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
method = p.method;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L382-L385
datax = data(:,2);
timex = data(:,1);
diffx = diff(timex);
dt = median(diff(timex));
%% End copied source
switch method
case 'Multi-taper method'
    nw=p.nw; padtimes=p.padtimes; nzeropad=p.nzeropad;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L560-L573
    if padtimes > 1
        if nw == 1
            [po,w]=pmtm(datax,nw,nzeropad,'DropLastTaper',false);
        else
            [po,w]=pmtm(datax,nw,nzeropad);
        end
    else
        if nw == 1
            [po,w]=pmtm(datax,nw,'DropLastTaper',false);
        else
            [po,w]=pmtm(datax,nw);
        end
    end
    fd1=w/(2*pi*dt);
%% End copied source
case 'Lomb-Scargle spectrum'
    fmax=p.fmax; pd=p.pd;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L1132-L1132
        [po,fd1,pth] = plomb(datax,timex,fmax,'Pd',pd);
%% End copied source
case 'Periodogram'
    padtimes=p.padtimes; nzeropad=p.nzeropad;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L1514-L1518
    if padtimes > 1
        [po,fd1] = periodogram(datax,[],nzeropad,1/dt);
    else 
        [po,fd1]=periodogram(datax,[],[],1/dt);
    end
%% End copied source
otherwise, error('Acycle:Spectrum:Method','Unknown spectral estimator.'); end
r = struct();
r.po = po;
r.fd1 = fd1;
r.dt = dt;
if exist('pth','var'), r.pth=pth; end
end
