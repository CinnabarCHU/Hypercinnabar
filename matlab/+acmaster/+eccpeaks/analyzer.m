function [retval,id] = analyzer(params,id)
% eccpeaks.analyzer parameters: X ecc eci norbit corrcoef ci sh_norb n dim a.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/eccpeaks.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('eccpeaks-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[Yp, locat] = eccpeaks(p.X, p.ecc, p.eci, p.norbit, p.corrcoef, p.ci, p.sh_norb, p.n, p.dim, p.a);
r = struct();
r.Yp = Yp;
r.locat = locat;
end
