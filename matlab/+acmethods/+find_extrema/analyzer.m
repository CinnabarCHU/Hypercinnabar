function [retval, id] = analyzer(params, id)
% find_extrema.analyzer parameters: y.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/find_extrema.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('find_extrema-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[max_p, max_v, min_p, min_v] = find_extrema(p.y);
r = struct();
r.max_p = max_p;
r.max_v = max_v;
r.min_p = min_p;
r.min_v = min_v;
end
