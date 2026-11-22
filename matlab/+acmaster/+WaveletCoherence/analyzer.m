function [retval,id] = analyzer(params,id)
% WaveletCoherence.analyzer parameters: dat1 dat2 pad dss param MonteCarloCount.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/wtcML.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('WaveletCoherence-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
dat1 = p.dat1;
dat2 = p.dat2;
pad = p.pad;
dss = p.dss;
param = p.param;
MonteCarloCount = p.MonteCarloCount;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/wavelet/wtcML.m:L68-L145
[x,dt]=formatts(dat1);
[y,dty]=formatts(dat2);
if dt~=dty
    error('timestep must be equal between time series')
end
t=(max(x(1,1),y(1,1)):dt:min(x(end,1),y(end,1)))'; %common time period
if length(t)<4
    error('The two time series must overlap.')
end

n=length(t);

S0 = 2*dt;
MaxScale=(n*.17)*2*dt; %auto maxscale
J1=round(log2(MaxScale/S0)/dss);
mother = 'Morlet';
%MonteCarloCount = 300;
AR1=[ar1nv(x(:,2)) ar1nv(y(:,2))];
if any(isnan(AR1))
    disp('Automatic AR1 estimation failed. Specify it manually (use arcov or arburg).')
    AR1=[rhoAR1ML(x(:,2)) rhoAR1ML(y(:,2))];
end
ArrowDensity = [30 30];
ArrowSize = 1;
ArrowHeadSize= 1;

ad=mean(ArrowDensity);
ArrowSize=ArrowSize*30*.03/ad;
ArrowHeadSize=ArrowHeadSize*120/ad;

nx=size(x,1);

ny=size(y,1);

%-----------:::::::::::::--------- ANALYZE ----------::::::::::::------------

[X,period,scale,coix] = wavelet(x(:,2),dt,pad,dss,S0,J1,mother,param);%#ok
[Y,period,scale,coiy] = wavelet(y(:,2),dt,pad,dss,S0,J1,mother,param);

%Smooth X and Y before truncating!  (minimize coi)
sinv=1./(scale');

sX=smoothwavelet(sinv(:,ones(1,nx)).*(abs(X).^2),dt,period,dss,scale);
sY=smoothwavelet(sinv(:,ones(1,ny)).*(abs(Y).^2),dt,period,dss,scale);


% truncate X,Y to common time interval (this is first done here so that the coi is minimized)
dte=dt*.01; %to cricumvent round off errors with fractional timesteps
idx=find((x(:,1)>=(t(1)-dte))&(x(:,1)<=(t(end)+dte)));
X=X(:,idx);
sX=sX(:,idx);
coix=coix(idx);

idx=find((y(:,1)>=(t(1))-dte)&(y(:,1)<=(t(end)+dte)));
Y=Y(:,idx);
sY=sY(:,idx);
coiy=coiy(idx);

coi=min(coix,coiy);

% -------- Cross wavelet -------
Wxy=X.*conj(Y);
%
Pkx=ar1spectrum(AR1(1),period./dt);
Pky=ar1spectrum(AR1(2),period./dt);

sigmax=std(x(:,2));

sigmay=std(y(:,2));

V=2;
Zv=3.9999;
signif=sigmax*sigmay*sqrt(Pkx.*Pky)*Zv/V;
sig95 = (signif')*(ones(1,n));  % expand signif --> (J+1)x(N) array
sig95 = abs(Wxy) ./ sig95;
% ----------------------- Wavelet coherence ---------------------------------
sWxy=smoothwavelet(sinv(:,ones(1,n)).*Wxy,dt,period,dss,scale);
Rsq=abs(sWxy).^2./(sX.*sY);
%% End copied source
q=struct('mccount',MonteCarloCount,'ar1',AR1,'dt',dt,'n',length(t)*2, ...
    'pad',pad,'dj',dss,'s0',S0,'j1',J1,'mother',mother,'cutoff',.6);
confidence=acmaster.wtcsignif.analyzer(q);
wtcsig=confidence.wtcsig;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/package/wavelet/wtcML.m:L149-L150
wtcsig=(wtcsig(:,2))*(ones(1,n));
wtcsig=Rsq./wtcsig;
%% End copied source
r = struct();
r.sigmax=sigmax; r.sigmay=sigmay;
r.datax=t; r.dat1y=x(ismember(x(:,1),t),2); r.dat2y=y(ismember(y(:,1),t),2);
r.t = t;
r.dt = dt;
r.period = period;
r.scale = scale;
r.coi = coi;
r.Rsq = Rsq;
r.Wxy = Wxy;
r.wtcsig = wtcsig;
r.sig95 = sig95;
r.X = X;
r.Y = Y;
r.ArrowDensity = ArrowDensity;
r.ArrowSize = ArrowSize;
r.ArrowHeadSize = ArrowHeadSize;
end
