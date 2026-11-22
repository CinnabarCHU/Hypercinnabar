function [retval, id] = analyzer(params, id)
% smoothciML.analyzer parameters: X Y method span bootn.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/smoothciML.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('smoothciML-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[meanboot, bootstd, bootprt] = smoothciML(p.X, p.Y, p.method, p.span, p.bootn);
r = struct();
r.meanboot = meanboot;
r.bootstd = bootstd;
r.bootprt = bootprt;
end
