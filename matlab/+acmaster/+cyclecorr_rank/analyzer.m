function [retval,id] = analyzer(params,id)
% cyclecorr_rank.analyzer parameters: data targetf targetp target orbit7 rayleigh sr1 sr2 srstep sr0 adjust.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cyclecorr_rank.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cyclecorr_rank-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[corrx, corry, corrpy, nmi] = cyclecorr_rank(p.data, p.targetf, p.targetp, p.target, ...
    p.orbit7, p.rayleigh, p.sr1, p.sr2, ...
    p.srstep, p.sr0, p.adjust);
r = struct();
r.corrx = corrx;
r.corry = corry;
r.corrpy = corrpy;
r.nmi = nmi;
end
