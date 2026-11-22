function [retval, id] = analyzer(params, id)
% crp_pdist.analyzer parameters: x w ws theiler_window lmin threshold method_use normFlag m tau.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/recurrence/crp_pdist.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('crp_pdist-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[Y, testi] = crp_pdist(p.x, p.w, p.ws, p.theiler_window, p.lmin, 0, p.threshold, p.method_use, p.normFlag, p.m, p.tau);
r = struct();
r.Y = Y;
r.testi = testi;
end
