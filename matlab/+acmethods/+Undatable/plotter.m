function [retval, id] = plotter(params, id)
% Undatable.plotter parameters: result plotsar printme vcloud writedir.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/undatable/undatable.m#L242
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/undatable/udplot.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Undatable-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
q=p.result.plotdata;
depth=q.depth;
depth1=q.depth1;
depth2=q.depth2;
age=q.age;
ageerr=q.ageerr;
datetype=q.datetype;
probtoplot=q.probtoplot;
p95_4=q.p95_4;
p68_2=q.p68_2;
medians=q.medians;
depthrange=q.depthrange;
summarymat=q.summarymat;
shadingmat=q.shadingmat;
sarsummarymat=q.sarsummarymat;
sarshadingmat=q.sarshadingmat;
debugme=q.debugme;
if debugme, agedepmat=q.agedepmat; end
inputfile=p.result.input_name;
plotsar=p.plotsar; printme=p.printme; vcloud=p.vcloud; writedir=p.writedir;
if ~isempty(writedir), writedir=[writedir,filesep]; end
guimode=0;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/undatable/undatable.m:L242-L242
	udplot
%% End copied source
r=[];
end
