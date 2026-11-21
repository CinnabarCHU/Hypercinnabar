function compute_wtc(k,core,reference,dest)
% WTCPlot.m supplies the pair order and numerical options.
if ~exist(dest,'dir'), mkdir(dest); end
q=compute_inputs(core,reference); t=q(1).t;
a=[q(1).y q(2).y interp1(q(3).t,q(3).y,t) interp1(q(4).t,q(4).y,t)];
pairs=[3 1;4 1;3 2;4 2;1 2]; pair=pairs(k,:);
vendor=fullfile(fileparts(mfilename('fullpath')),'grinsted');
addpath(vendor,'-begin');
rng(260425+k,'twister');
[r,p,~,co,sig,wt,ph]=wtc([t,a(:,pair(1))],[t,a(:,pair(2))], ...
    'Mother','Morlet','Dj',1/12,'S0',2*3.413,'MaxScale',5000,'Pad',1, ...
    'MonteCarloCount',300,'AR1','auto','MakeFigure',0,'ArrowDensity',[100 60]);
ix=unique([1:4:length(wt),length(wt)]); j=p>=60 & p<=5300;
dx=round(length(wt)/100); dy=round(length(p)/60);
ia=max(floor(dx/2),1):dx:length(wt); ja=max(floor(dy/2),1):dy:length(p);
ja=ja(p(ja)>=64 & p(ja)<=5000);
phase=ph(ja,ia); phase(r(ja,ia)<.5)=NaN;
wtcdata=struct('t',wt(ix),'period',p(j),'coi',co(ix), ...
    'r2',single(r(j,ix)),'sig',single(sig(j,ix)), ...
    'arrow_age',wt(ia),'arrow_period',p(ja),'phase',phase,'pair',pair, ...
    'ar1',[ar1nv(a(:,pair(1))) ar1nv(a(:,pair(2)))],'seed',260425+k,'mc',300);
save(fullfile(dest,sprintf('pair%d.mat',k)),'-struct','wtcdata','-v7');
end
