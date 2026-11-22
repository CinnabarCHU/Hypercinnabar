function [retval, id] = analyzer(params, id)
% insoML.analyzer parameters: t day lat qinso author res L.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/insoML.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('insoML-v1.0/analyzer', params, id, @execute);
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
