function [retval, id] = analyzer(params, id)
% chisquare_inv.analyzer parameters: P V.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/chisquare_inv.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('chisquare_inv-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[X] = chisquare_inv(p.P, p.V);
r = struct();
r.X = X;
end
