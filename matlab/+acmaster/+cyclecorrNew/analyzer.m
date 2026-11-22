function [retval,id] = analyzer(params,id)
% cyclecorrNew.analyzer parameters: data dat pad target orbit9 rayleigh sr1 sr2 srstep sr0 adjust method targetMode.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cyclecorrNew.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cyclecorrNew-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[corrx, corry, corrpy, nmi] = cyclecorrNew( ...
    p.data, p.dat, p.pad, [], p.target, p.orbit9, p.rayleigh, p.sr1, p.sr2, p.srstep, p.sr0,  ...
    p.adjust, p.method, p.targetMode);
r = struct();
r.corrx = corrx;
r.corry = corry;
r.corrpy = corrpy;
r.nmi = nmi;
end
