function [retval, id] = analyzer(params, id)
% moveMedian.analyzer parameters: x w.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/moveMedian.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('moveMedian-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[y] = moveMedian(p.x, p.w);
r = struct();
r.y = y;
end
