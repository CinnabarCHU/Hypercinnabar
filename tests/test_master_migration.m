function test_master_migration()
% Compare revision-sensitive features on the same inputs; exercise replay, graphics and exports.
root = fileparts(fileparts(mfilename('fullpath')));
addpath(root);
setup_migration;
journal = tempname; mkdir(journal);
oldLog = getenv('ACYCLE_LOG_DIR');
oldVisibility = get(groot,'defaultFigureVisible');
cleanup = onCleanup(@() restore(journal,oldLog,oldVisibility)); %#ok<NASGU>
setenv('ACYCLE_LOG_DIR',journal);
set(groot,'defaultFigureVisible','off');
initialPath = path;
legacyKernel = which('gaussfilter');
t = (0:255)';
d = [t,sin(2*pi*t/32)+0.2*cos(2*pi*t/8)];
p = acmaster.Bandpass.helper(struct('data',d));
assert(strcmp(p.options.method,'gaussian'));
p.options.lower_frequency = 1/40; p.options.upper_frequency = 1/24;
[v,id] = acmaster.Bandpass.analyzer(p);
assert(isequal(size(v.result.filtered),size(t)) && isequaln(v,aclog.replay(id)));
guard = accompat.masterPath();
assert(contains(which('gaussfilter'),fullfile('upstream','master')));
[reference,refMeta] = acycleBandpassFilter(p.data,p.options);
assert(isequaln(v.result,reference) && isequaln(v.meta,refMeta));
clear guard
assert(strcmp(path,initialPath) && strcmp(which('gaussfilter'),legacyKernel));
assert(contains(fileread(id),'Bandpass-v3.1.1+dcba427/analyzer'));
bp = acmethods.Bandpass.helper(struct('data',d));
bp.flow = p.options.lower_frequency; bp.fhigh = p.options.upper_frequency;
[b,bid] = acmethods.Bandpass.analyzer(bp);
assert(isequaln(aclog.replay(bid),b) && contains(fileread(bid),'Bandpass-v1.0/analyzer'));
bad = p; bad.options.method='taner_hilbert'; failedID=aclog.newId();
try
    acmaster.Bandpass.analyzer(bad,failedID);
    error('test:ExpectedFailure','Missing rolloff should fail.');
catch err
    assert(strcmp(err.identifier,'Acycle:Method:MissingOption'));
end
assert(strcmp(path,initialPath) && contains(fileread(failedID),'cancelled'));
q = acmaster.SamplingGrid.helper(struct('coordinate',[0;1;2.000001;3]));
g = acmaster.SamplingGrid.analyzer(q); assert(~g.isUneven && q.relativeTolerance==1e-5);
q.coordinate=[0;1;2.001;3]; g=acmaster.SamplingGrid.analyzer(q); assert(g.isUneven);
v = acmaster.MovingMean.analyzer(struct('data',[t(1:5),(1:5)'],'windowPoints',2));
assert(isequal(v.result(:,2),[1.5;2.5;3.5;4.5;5]) && isequal(v.result(:,3),[2;2;2;2;1]));
v = acmaster.dynotPercentilePlan.analyzer(struct('selection',[0 0 0 0 1 0]));
assert(isequal(v.plan.percentiles,[5 50 95]) && v.plan.medianIndex==2);
p = acmaster.RegularInterpolation.helper(struct('data',d(1:6,:),'samplingInterval',2));
[v,id] = acmaster.RegularInterpolation.analyzer(p);
assert(isequal(v.interpolated(:,1),[0;2;4]) && isequaln(aclog.replay(id),v));
p = acmaster.PowerSpectrum.helper(struct('data',d)); assert(p.nfft==numel(t));
p.method='Periodogram'; p.nfft=333;
v = acmaster.PowerSpectrum.analyzer(p); assert(numel(v.power)==167 && v.dof==2);
acmaster.PowerSpectrum.plotter(struct('result',v,'fmin',0,'fmax',.49,'usePeriod',true,'logFrequency',true));
p=acmaster.PowerSpectrum.helper(struct('data',[t(1:8)+[0;0;0;.02;0;0;0;0],d(1:8,2)]));
assert(strcmp(p.method,'Lomb-Scargle spectrum'));
p=acmaster.DigitizeTrace.helper(struct('image',uint8(255*ones(70,100)),'seeds',[44 35], ...
    'calibration',struct('pixels',[10 60;90 60;10 60;10 10],'limits',[0 10 0 5],'logX',false,'logY',false)));
p.image(35,10:90)=0;
[v,id]=acmaster.DigitizeTrace.analyzer(p);
assert(size(v.pixels,1)==81 && isequaln(v,aclog.replay(id)));
assert(max(abs(v.data(:,2)-2.5))<1e-12);
v=acmaster.LinearRegression.analyzer(struct('data',[0 1;1 3;2 5;NaN 5]));
assert(norm(v.coefficients-[2 1])<1e-10 && size(v.stats,1)==7);
v=acmaster.OneSampleT.analyzer(struct('data',1e6+[1;3;2;5;7],'miu',0,'option_cal',1));
acmaster.OneSampleT.plotter(struct('result',v));
ax=findall(groot,'Tag','TTestAxes'); limits=xlim(ax(1));
assert(limits(1)==-limits(2) && limits(2)<=11 && contains(ax(1).XLabel.String,'t statistic'));
p=acmaster.Bispectral.helper(struct('data',d));
assert(strcmp(p.options.SignificanceMethod,'none'));
[v,id]=acmaster.Bispectral.analyzer(p); v2=aclog.replay(id);
assert(isequaln(v.BicoherenceSquared,v2.BicoherenceSquared) && any(isfinite(v.BicoherenceSquared(:))));
p=acmaster.BispectralView.helper(struct('result',v)); p.settings.Visible='off';
acmaster.Bispectral.plotter(p);
% Verify every concrete role is visible to MATLAB's parser.
rows=readtable(fullfile(root,'migration','master','methods.tsv'),'FileType','text','Delimiter','tab','TextType','string');
for k=1:height(rows)
    assert(~isempty(which(char("acmaster."+rows.package(k)+"."+rows.role(k)))));
end
fprintf('Master/guide resolution, numerical behavior, figures and journal replay verified.\n');
end

function restore(directory,oldLog,visibility)
close all force
set(groot,'defaultFigureVisible',visibility);
setenv('ACYCLE_LOG_DIR',oldLog);
if isfolder(directory), rmdir(directory,'s'); end
end
