function [retval, id] = analyzer(params, id)
% recplot.analyzer parameters: x threshold t labelx labely.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/recurrence/recplot.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('recplot-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[S] = recplot(p.x, p.threshold, p.t, 0, p.labelx, p.labely);
r = struct();
r.S = S;
end
