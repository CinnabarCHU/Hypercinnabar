function [retval, id] = analyzer(params, id)
% cyclecorr5.analyzer parameters: xx yy targetf targetp lax orbit7 rayleigh sr1 sr2 srstep sr0 adjust.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/cyclecorr5.m#L29
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('cyclecorr5-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[corry] = cyclecorr5(p.xx, p.yy, p.targetf, p.targetp, ...
    p.lax, p.orbit7, p.rayleigh, p.sr1, ...
    p.sr2, p.srstep, p.sr0, p.adjust);
r = struct();
r.corry = corry;
end
