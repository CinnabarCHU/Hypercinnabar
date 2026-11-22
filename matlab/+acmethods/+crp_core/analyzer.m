function [retval, id] = analyzer(params, id)
% crp_core.analyzer parameters: x y m tau e method normFlag.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/recurrence/crp_core.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('crp_core-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[xout] = crp_core(p.x, p.y, p.m, p.tau, p.e, p.method, p.normFlag);
r = struct();
r.xout = xout;
end
