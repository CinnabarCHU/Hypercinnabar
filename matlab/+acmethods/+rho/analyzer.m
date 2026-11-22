function [retval, id] = analyzer(params, id)
% rho.analyzer parameters: x nData varx.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/swa/rho.m#L6
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('rho-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[rho1] = rho(p.x, p.nData, p.varx);
r = struct();
r.rho1 = rho1;
end
