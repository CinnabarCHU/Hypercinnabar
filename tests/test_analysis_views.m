function test_analysis_views()
root=fileparts(fileparts(mfilename('fullpath'))); addpath(root); setup_migration;
old=getenv('ACYCLE_LOG_DIR'); journal=tempname; mkdir(journal); setenv('ACYCLE_LOG_DIR',journal);
cleanup=onCleanup(@() restore(journal,old)); t=(0:255)'; d=[t,sin(2*pi*t/23)+.4*cos(2*pi*t/13)];
img=uint8(255*ones(60,65)); center=round(29+4*cos((1:65)/8));
for x=1:65, img(center(x),x)=0; end
img(:,30)=255;
q=acmethods.DigitizeTrace.helper(struct('image',img,'seeds',[10,center(10)])); q.engine='ecocotrackn';
r=acmethods.DigitizeTrace.analyzer(q);
expect=(1:65)'; expect(30)=[]; assert(isequal(r.pixels,[expect,reshape(center(expect),[],1)]));
q=acmethods.Detrending.helper(struct('data',d)); q.method='quadratic'; z=acmethods.Detrending.analyzer(q);
assert(isequaln(z.trend,polyval(polyfit(t,d(:,2),2),t)));
if exist('OCTAVE_VERSION','builtin'), return; end
before=findall(groot,'type','figure'); graphicsGuard=onCleanup(@() close(setdiff(findall(groot,'type','figure'),before)));
q=acmethods.EvolutionarySpectrum.helper(struct('data',d)); q.window=60; q.step=15;
q.result=acmethods.EvolutionarySpectrum.analyzer(q); acmethods.EvolutionarySpectrum.plotter(q);
q=acmethods.WaveletSpectrum.helper(struct('data',d)); r=acmethods.WaveletSpectrum.analyzer(q);
q=withResult(q,r); q.unit='cm'; q.unit_type=1; q.plot_spectrum=1;
acmethods.WaveletSpectrum.plotter(q);
assert(numel(findall(gcf,'type','axes'))>=3);
second=[t,d(:,2)+.2*sin(2*pi*t/31)];
q=acmethods.MatlabWaveletCoherence.helper(struct('dat1',d,'dat2',second));
q.result=acmethods.MatlabWaveletCoherence.analyzer(q); acmethods.MatlabWaveletCoherence.plotter(q);
q=acmethods.WaveletCoherence.helper(struct('dat1',d,'dat2',second)); q.MonteCarloCount=0;
q.result=acmethods.WaveletCoherence.analyzer(q); acmethods.WaveletCoherence.plotter(q);
assert(~isempty(findall(groot,'type','figure','name','Acycle: Cross-wavelet')));
testSpectra(d);
testUndatable(root,journal);
testEcoco();
end

function q=withResult(q,r)
names=fieldnames(r);
for i=1:numel(names), q.(names{i})=r.(names{i}); end
end

function testSpectra(d)
p=acmethods.PowerSpectrum.helper(struct('data',d)); p.unit='m'; p.nw=2;
p.noise.classic=true; p.noise.ftest=true; p.noise.swa=true;
p.noise.biascorr=false; p.noise.powerlaw=true;
initial=findall(groot,'type','figure');
r=acmethods.PowerSpectrum.analyzer(p);
assert(isequal(initial,findall(groot,'type','figure')));
[f,sp,red,~,c95,~,~]=redconfchi2(p.data(:,2),p.nw,r.dt,p.nzeropad,2);
assert(isequaln(r.models.classic.fd,f) && isequaln(r.models.classic.po,sp) && isequaln(r.models.classic.theored,red) && isequaln(r.models.classic.tabtchi95,c95));
assert(isfield(r.models,'swa') && isfield(r.models,'ftest') && isfield(r.models,'powerlaw'));
p.result=r; acmethods.PowerSpectrum.plotter(p); p.plot_x_period=1; acmethods.PowerSpectrum.plotter(p);
p=acmethods.BootstrapSmooth.helper(struct('data',d)); p.bootn=9;
rng(9); initial=findall(groot,'type','figure'); [b,id]=acmethods.BootstrapSmooth.analyzer(p);
assert(isequaln(b,aclog.replay(id)) && isequal(initial,findall(groot,'type','figure')));
p.result=b; acmethods.BootstrapSmooth.plotter(p);
end

function testUndatable(root,folder)
source=fullfile(root,'upstream','acycle','code','package','undatable','udinput_template2.txt');
inputFile=fullfile(folder,'dates.txt'); copyfile(source,inputFile);
q=acmethods.Undatable.helper(struct('inputfile',inputFile,'nsim',50,'xfactor',.1,'bootpc',0));
q.run1nsim=50; q.printme=0; delete(inputFile);
rng(12); [r,id]=acmethods.Undatable.analyzer(q); again=aclog.replay(id);
assert(isequaln(r.udoutput,again.udoutput) && size(r.udoutput,2)==7);
q.result=r; acmethods.Undatable.plotter(q);
end

function testEcoco()
t=(0:.2:40)'; data=[t,sin(t*2*pi/2)+.6*cos(t*2*pi/4)+.22*cos(t*2*pi/.9)];
f=(0:.00025:.08)'; periods=[405 125 100 41 23 19]; power=zeros(size(f));
for k=1:numel(periods), power=power+exp(-.5*((f-1/periods(k))/.0006).^2); end
q=struct('data',data,'target',[f,power],'orbit7',periods,'window',16,'dt',.2,'step',23,'delinear',1,'red',1,'pad',256,'sr1',1,'sr2',4,'srstep',.5,'nsim',0,'adjust',0,'slices',1);
[r,id]=acmethods.ecoco.analyzer(q);
entries=regexp(strtrim(fileread(id)),'\r?\n','split'); last=jsondecode(entries{end});
assert(strcmp(last.info.status,'incomplete') && isempty(r.out_eci) && isempty(r.sr_p));
assert(size(r.out_ecc,2)==numel(r.out_depth) && isequal(size(r.out_norbit),size(r.out_ecc)));
s=rmfield(q,{'data','delinear','window','step'}); s.dat=data(1:80,:); s.dat(:,2)=detrend(s.dat(:,2),0); s.method='Pearson';
slice=acmethods.corrcoefslices_rank.analyzer(s);
assert(isequaln(r.out_ecc(:,1),slice.corrCI(:,2)));
end

function restore(folder,prior)
setenv('ACYCLE_LOG_DIR',prior); rmdir(folder,'s');
end
