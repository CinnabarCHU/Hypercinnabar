function test_scientific_methods()
% Compare portable methods with the pinned files, independent kernels and GUIDE choices.
root=fileparts(fileparts(mfilename('fullpath')));
addpath(root); setup_migration;
old=getenv('ACYCLE_LOG_DIR');
folder=tempname; mkdir(folder);
setenv('ACYCLE_LOG_DIR',folder);
guard=onCleanup(@() restoreJournal(folder,old));
t=(0:127)'; d=[t,sin(2*pi*t/16)+.32*cos(2*pi*t/9)+.08*sin(t)];
result=acmethods.ExampleSvalbardPETM.analyzer(struct());
reference=load(fullfile(root,'upstream','acycle','data','Examples','Example-SvalbardPETM-logFe.txt'));
assert(isequal(result.data,reference));
q=acmethods.AstronomicalSolution.helper(struct()); q.t2=65; q.parameter='Eccentricity';
r=acmethods.AstronomicalSolution.analyzer(q);
la=load(fullfile(root,'upstream','acycle','data','La04.mat')); expected=select_interval(la.data,0,65);
assert(isequal(r.dat,expected(:,1:2)));
q=acmethods.FixedMovingMedian.helper(struct('data',d));
assert(isequal([q.window,q.step,q.halfwindow,q.alpha],[38.1,1,0,.05]));
q=acmethods.ColumnManipulation.helper(struct('dataCell',{{d,[t,-d(:,2)]}}));
q.colman1=[2,2;5,-.5]; r=acmethods.ColumnManipulation.analyzer(q);
assert(isequal(r.series,[t,2*d(:,2)+.5*d(:,2)]));
q=acmethods.WaveletSpectrum.helper(struct('data',d));
r=acmethods.WaveletSpectrum.analyzer(q);
s0=2*mean(diff(t));
j1=round(log2(q.pt2))/q.dss;
[w,period,scale,coi]=wavelet(d(:,2),mean(diff(t)),q.pad,q.dss,s0,j1,q.mother,q.param);
assert(isequaln(r.wave,w) && isequaln(r.period,period) && isequaln(r.coi,coi));
expected=abs(w).^2./scale(:);
assert(max(abs(expected(:)-r.power(:))) < 1e-12);
q=struct('data',d,'method','Periodogram','padtimes',2,'nzeropad',256);
r=acmethods.PowerSpectrum.analyzer(q);
[po,fr]=periodogram(d(:,2),[],256,1);
assert(isequal(r.po,po) && isequal(r.fd1,fr));
q=struct('data',d,'window',40,'step',3,'pad',2,'srmean',0,'smoothmodel','poly','padedge',0);
r=acmethods.spectralmoments.analyzer(q);
assert(isempty(r.sr) && isempty(r.Bwtrend));
first=detrend(d(1:40,2)); [px,f]=periodogram(first,[],80,1);
uf=sum(f.*px/sum(px)); bw=sqrt(sum((f-uf).^2.*px/sum(px)));
assert(abs(uf-r.uf(1))<1e-12 && abs(bw-r.Bw(1))<1e-12);
oldFolder=pwd;
folderGuard=accompat.swaWorkspace({'acycle_test_swa_workspace'});
scratchDir=pwd; assert(~strcmp(scratchDir,oldFolder));
fid=fopen('scratch.dat','w'); fclose(fid); assignin('base','acycle_test_swa_workspace',47);
clear folderGuard;
assert(strcmp(pwd,oldFolder) && ~isfolder(scratchDir) && ~evalin('base','exist(''acycle_test_swa_workspace'',''var'')'));
if ~exist('OCTAVE_VERSION','builtin')
    testMatlabWorkflows(d);
end
fprintf('Scientific checks passed for reference data, orbital solutions, windows, spectra, wavelets and SWA isolation.\n');
end

function testMatlabWorkflows(d)
t=d(:,1);
q=acmethods.Recurrence.helper(struct('data_s',d)); q.showdet=1;
r=acmethods.Recurrence.analyzer(q);
z=(d(:,2)-mean(d(:,2)))/std(d(:,2));
assert(max(abs(r.S-abs(z-z.')),[],'all') < 1e-12);
assert(~isempty(r.DETx) && numel(r.DETx)==numel(r.DETy));
p=acmethods.PowerDecomposition.helper(struct('data',d)); p.window=42; p.pad=128;
p.step=4; p.ftmin=.005; p.fterm=.4; p.f3=[.04,.1]; p.padtype=0;
a=acmethods.PowerDecomposition.analyzer(p);
assert(isequaln(a.pow,pdan(a.data,p.f3,p.window,p.nw,p.ftmin,p.fterm,p.step,p.pad)));
p=struct('data',d,'sampa',.85,'sampb',1.15,'parmhat',[1,2],'window1',38,'window2',44, ...
    'nw1',2,'nw2',2,'pad',128,'step',4,'nout',24,'shiftwin',1,'padwin',1, ...
    'f',[.05,.1],'fza',.9,'fzb',1.1,'ftmin',.01,'ftmax',.4,'nmc',4,'percent',[2.5,50,97.5]);
rng(483); [a,id]=acmethods.DYNOT.analyzer(p); again=aclog.replay(id);
assert(isequaln(a,again) && any(isfinite(a.powy(:))));
i=1; xi=(t(1):a.samplez(i):t(end))'; si=[xi,interp1(t,d(:,2),xi,'pchip')];
si(:,2)=si(:,2)-polyval(polyfit(si(:,1),si(:,2),1),si(:,1)); si=zeropad2(si,a.windowz(i),p.padwin);
pow=pdan(si,a.f3m(i,:),a.windowz(i),a.nwz(i),p.ftmin,p.ftmax,p.step,p.pad);
assert(isequaln(a.powy(:,i),interp1(pow(:,1),pow(:,2),a.y_grid)));
w=acmethods.WaveletSpectrum.helper(struct('data',d)); a=acmethods.WaveletSpectrum.analyzer(w);
fields=fieldnames(a);
for i=1:numel(fields), w.(fields{i})=a.(fields{i}); end
w.unit='kyr'; w.unit_type=2;
before=findall(groot,'Type','figure'); closeFigures=onCleanup(@() close(setdiff(findall(groot,'Type','figure'),before)));
acmethods.WaveletSpectrum.plotter(w);
assert(numel(findall(groot,'Type','figure'))==numel(before)+1);
end

function restoreJournal(folder,old)
setenv('ACYCLE_LOG_DIR',old);
rmdir(folder,'s');
end
