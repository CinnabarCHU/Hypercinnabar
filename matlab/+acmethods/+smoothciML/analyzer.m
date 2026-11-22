function [retval, id] = analyzer(params, id)
% smoothciML.analyzer parameters: X Y method span bootn.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/smoothciML.m#L35
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('smoothciML-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
X = p.X;
Y = p.Y;
method = p.method;
span = p.span;
bootn = p.bootn;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/seriesanalysis/smoothciML.m:L35-L42
f = @(xy) smoothci(xy,X,span,method);
yboot2 = bootstrp(bootn,f,[X,Y])';

meanboot = mean(yboot2,2);
bootstd = std(yboot2,0,2);
%percentile
%bootprt = prctile(yboot2, [.5,2.275,15.865,50,84.135,97.725,99.5],2);
bootprt = prctile(yboot2, [0.5,2.5,5,25,50,75,95,97.5,99.5],2);
%% End copied source
r = struct();
r.meanboot = meanboot;
r.bootstd = bootstd;
r.bootprt = bootprt;
end
