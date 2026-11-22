function [retval, id] = analyzer(params, id)
% norbits.analyzer parameters: target f power orbit7 rayleigh sr.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/norbits.m#L14
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('norbits-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[nm] = norbits(p.target, p.f, p.power, p.orbit7, p.rayleigh, p.sr);
r = struct();
r.nm = nm;
end
