function [retval, id] = analyzer(params, id)
% chisquare_solve.analyzer parameters: XGUESS P V.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/chisquare_solve.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('chisquare_solve-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[PDIFF] = chisquare_solve(p.XGUESS, p.P, p.V);
r = struct();
r.PDIFF = PDIFF;
end
