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
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L1130-L1132
        timex = timex + abs(min(timex));
        %[po,fd1,pth] = plomb(datax,timex,fmax,'normalized','Pd',pd);
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
if isfield(p,'noise')
    r.models=backgrounds(p,r);
end
end

function m=backgrounds(p,r)
o=p.noise; m=struct();
data=p.data; datax=data(:,2); timex=data(:,1); dt=r.dt; fd1=r.fd1; po=r.po;
nw=p.nw; nzeropad=p.nzeropad; smoothwin=o.smoothwin; fmax=p.fmax;
if strcmp(p.method,'Multi-taper method')
    if o.classic
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L878-L879
        [fd,po,theored,tabtchi90,tabtchi95,tabtchi99,tabtchi999]=redconfchi2(datax,nw,dt,nzeropad,2);
        rho = rhoAR1(datax);
%% End copied source
        m.classic=struct('fd',fd,'po',po,'theored',theored,'tabtchi90',tabtchi90, ...
            'tabtchi95',tabtchi95,'tabtchi99',tabtchi99,'tabtchi999',tabtchi999,'rho',rho);
    end
    if o.robust
        if o.biascorr, valid=p.ValidNyqFreqR; else, valid=p.ValidNyqFreq; end
        [rhoM,s0M,a,b]=redconfML(datax,dt,nw,nzeropad,o.linlog,smoothwin,valid,0);
        m.robust=struct('rhoM',rhoM,'s0M',s0M,'redconfAR1',a,'redconfML96',b);
    end
    if o.ftest
        m.ftest=acmethods.ftestmtmML.analyzer(struct('data',data,'NW',nw,'npad',p.padtimes));
    end
    if o.swa
        m.swa=acmethods.spectralswafdr.analyzer(struct('data',data,'method','mtm','nw',nw,'padtimes',p.padtimes));
    end
elseif strcmp(p.method,'Lomb-Scargle spectrum')
    if o.robust
        [pr,fr,thresholds]=plomb_robustar1(datax,timex,fmax,smoothwin,0);
        m.robust=struct('po',pr,'f',fr,'pth',thresholds);
    end
    if o.classic, m.false_alarm=r.pth; end
elseif o.classic
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/spectrum.m:L1567-L1570
            [theored]=theoredar1ML(datax,fd1,mean(po),dt);
            tabtchired90 = theored * chi2inv(90/100,2)/2;
            tabtchired95 = theored * chi2inv(95/100,2)/2;
            tabtchired99 = theored * chi2inv(99/100,2)/2;
%% End copied source
    m.classic=struct('theored',theored,'tabtchired90',tabtchired90,'tabtchired95',tabtchired95,'tabtchired99',tabtchired99);
end
q=struct('datax',datax,'fd1',fd1,'po',po,'method',p.method,'nw',nw);
if o.powerlaw, m.powerlaw=acmethods.SpectralPowerLaw.analyzer(q); end
if o.bending, m.bending=acmethods.SpectralBendingPowerLaw.analyzer(q); end
end
