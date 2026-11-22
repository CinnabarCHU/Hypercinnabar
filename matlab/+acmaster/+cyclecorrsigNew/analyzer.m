function [retval,id] = analyzer(params,id)
% cyclecorrsigNew.analyzer parameters: data dat pad target orbit9 rayleigh sr1 sr2 srstep sr0 adjust method targetMode.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cyclecorrsigNew.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cyclecorrsigNew-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[corry] = cyclecorrsigNew( ...
    p.data, p.dat, p.pad, [], p.target, p.orbit9, p.rayleigh, p.sr1, p.sr2, p.srstep, p.sr0,  ...
    p.adjust, p.method, p.targetMode);
r = struct();
r.corry = corry;
end
