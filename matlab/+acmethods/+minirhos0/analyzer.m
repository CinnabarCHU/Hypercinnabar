function [retval, id] = analyzer(params, id)
% minirhos0.analyzer parameters: s0 fn ft pxxsmooth linlog.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/minirhos0.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('minirhos0-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[rho, s0] = minirhos0(p.s0, p.fn, p.ft, p.pxxsmooth, p.linlog, 0);
r = struct();
r.rho = rho;
r.s0 = s0;
end
