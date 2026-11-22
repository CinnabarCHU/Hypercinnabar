function [retval, id] = analyzer(params, id)
% ar1nv.analyzer parameters: x.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/ar1nv.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ar1nv-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[g, a] = ar1nv(p.x);
r = struct();
r.g = g;
r.a = a;
end
