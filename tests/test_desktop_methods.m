function test_desktop_methods()
root = fileparts(fileparts(mfilename('fullpath')));
addpath(root); setup_migration;
folder = tempname; mkdir(folder);
prior = getenv('ACYCLE_LOG_DIR'); setenv('ACYCLE_LOG_DIR',folder);
guard = onCleanup(@() restore(folder,prior));
data=[(0:40)',sin((0:40)'*0.3)];
r=acmethods.Derivative.analyzer(acmethods.Derivative.helper(struct('data',data)));
assert(isequal(r.data1,[data(1:end-1,1),diff(data(:,2))]));
r=acmethods.Clipping.analyzer(struct('data',data,'clip_high',1,'clip_value',0.25,'clip_set',2));
assert(isequal(r.data1(:,2),max(data(:,2),.25)));
r=acmethods.Extrema.analyzer(struct('data',data,'t1',0,'t2',40,'ind',2,'maxmin',1));
assert(isequal(r.row,data(data(:,2)==max(data(:,2)),:)));
s=acmethods.SummaryStatistics.analyzer(struct('data',data(:,2)));
assert(str2double(s.stats{1,2})==size(data,1));
p=acmethods.InterpolationPro.helper(struct('data',data(end:-1:1,:)));
p.dt=.5; p.method=5;
r=acmethods.InterpolationPro.analyzer(p);
assert(isequaln(r.vq,interp1(data(:,1),data(:,2),r.xq,'pchip')));
p=acmethods.CircularSpectrum.helper(struct('dat',[0;1;2.6;3.7;5.1;8.4]));
p.clmodel=1; p.mcn=13; p.pn=31;
rng(27); [s,id]=acmethods.CircularSpectrum.analyzer(p);
rng(263); before=rng; replayed=aclog.replay(id); after=rng;
assert(isequaln(before,after) && isequaln(s,replayed));
assert(isequal(s.R,circularPower(p)));
dirs=dir(fullfile(root,'matlab','+acmethods','+*'));
for i=1:numel(dirs)
    files=dir(fullfile(dirs(i).folder,dirs(i).name,'*.m'));
    for j=1:numel(files)
        [~,role]=fileparts(files(j).name);
        assert(~isempty(which(['acmethods.',dirs(i).name(2:end),'.',role])));
    end
end
if ~exist('OCTAVE_VERSION','builtin')
    d=[(0:255)',sin((0:255)'*2*pi/20)+.2*cos((0:255)'*2*pi/5)];
    p=acmethods.Bandpass.helper(struct('data',d));
    assert(strcmp(p.filter,'Gaussian') && isequal(p.data(:,1),d(:,1)));
    [g,~,~]=gaussfilter(p.data(:,2),1,(p.flow+p.fhigh)/2,p.flow,p.fhigh);
    a=acmethods.Bandpass.analyzer(p);
    assert(isequaln(a.data_filterout,[d(:,1),g,abs(hilbert(g))]));
    startFigures=findall(groot,'Type','figure');
    figs=onCleanup(@() close(setdiff(findall(groot,'Type','figure'),startFigures)));
    p.result=a; p.unit='m'; acmethods.Bandpass.plotter(p);
    assert(numel(findall(groot,'Type','figure'))==numel(startFigures)+1);
end
fprintf('Desktop extraction, all method names and stochastic replay passed.\n');
end

function R=circularPower(p)
[~,R,~]=circularspec(p.data,p.p1,p.p2,p.pn,p.linlog,0);
end

function restore(folder,prior)
setenv('ACYCLE_LOG_DIR',prior);
rmdir(folder,'s');
end
