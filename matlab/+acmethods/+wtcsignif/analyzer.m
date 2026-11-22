function [retval, id] = analyzer(params, id)
% wtcsignif.analyzer parameters: mccount ar1 dt n pad dj s0 j1 mother cutoff.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/wtcsignif.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('wtcsignif-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[wtcsig] = wtcsignif(p.mccount, p.ar1, p.dt, p.n, p.pad, p.dj, p.s0, p.j1, p.mother, p.cutoff);
r = struct();
r.wtcsig = wtcsig;
end
