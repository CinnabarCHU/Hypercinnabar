function [retval, id] = analyzer(params, id)
% prewhitening.analyzer parameters: data rho.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/prewhitening.m#L2
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('prewhitening-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[datp] = prewhitening(p.data, p.rho);
r = struct();
r.datp = datp;
end
