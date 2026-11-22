function [retval, id] = analyzer(params, id)
% cyclecorr4.analyzer parameters: data targetf targetp target orbit7 rayleigh sr1 sr2 srstep sr0 adjust.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/cyclecorr4.m#L25
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('cyclecorr4-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[corrx, corry, corrpy, corrlo, corrup, ...
    nmi] = cyclecorr4(p.data, p.targetf, p.targetp, p.target, ...
    p.orbit7, p.rayleigh, p.sr1, p.sr2, ...
    p.srstep, p.sr0, p.adjust);
r = struct();
r.corrx = corrx;
r.corry = corry;
r.corrpy = corrpy;
r.corrlo = corrlo;
r.corrup = corrup;
r.nmi = nmi;
end
