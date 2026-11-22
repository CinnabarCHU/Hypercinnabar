function [retval, id] = analyzer(params, id)
% smoothbestSpan.analyzer parameters: t y method alpha beta.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/smoothbestSpan.m#L2
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('smoothbestSpan-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[bestSpan] = smoothbestSpan(p.t, p.y, p.method, p.alpha, p.beta);
r = struct();
r.bestSpan = bestSpan;
end
