function [retval, id] = analyzer(params, id)
% smoothbestSpanRand.analyzer parameters: t y method num_iterations.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/smoothbestSpanRand.m#L2
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('smoothbestSpanRand-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[bestSpan, bestAlpha, bestBeta] = smoothbestSpanRand(p.t, p.y, p.method, p.num_iterations, 0);
r = struct();
r.bestSpan = bestSpan;
r.bestAlpha = bestAlpha;
r.bestBeta = bestBeta;
end
