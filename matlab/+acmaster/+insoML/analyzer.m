function [retval,id] = analyzer(params,id)
% insoML.analyzer parameters: t day lat qinso author res L.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/insoML.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('insoML-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[I, T, xorb, yorb, veq, ...
    Insol_a_m, Ix, II] = insoML(p.t, p.day, p.lat, p.qinso, p.author, p.res, p.L);
r = struct();
r.I = I;
r.T = T;
r.xorb = xorb;
r.yorb = yorb;
r.veq = veq;
r.Insol_a_m = Insol_a_m;
r.Ix = Ix;
r.II = II;
end
