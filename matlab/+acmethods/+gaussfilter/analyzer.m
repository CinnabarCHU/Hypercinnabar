function [retval, id] = analyzer(params, id)
% gaussfilter.analyzer parameters: datax dt fc fl fh.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/gaussfilter.m#L2
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('gaussfilter-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[gaussbandx, filter, f] = gaussfilter(p.datax, p.dt, p.fc, p.fl, p.fh);
r = struct();
r.gaussbandx = gaussbandx;
r.filter = filter;
r.f = f;
end
