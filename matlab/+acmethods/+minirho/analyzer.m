function [retval, id] = analyzer(params, id)
% minirho.analyzer parameters: s0 fn ft pxxsmooth linlog.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/minirho.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('minirho-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[rho, s0] = minirho(p.s0, p.fn, p.ft, p.pxxsmooth, p.linlog, 0);
r = struct();
r.rho = rho;
r.s0 = s0;
end
