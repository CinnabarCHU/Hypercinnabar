function [retval, id] = analyzer(params, id)
% eccpeaks.analyzer parameters: X ecc eci norbit corrcoef ci sh_norb n dim a.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/eccpeaks.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('eccpeaks-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[Yp, locat] = eccpeaks(p.X, p.ecc, p.eci, p.norbit, p.corrcoef, p.ci, p.sh_norb, p.n, p.dim, p.a);
r = struct();
r.Yp = Yp;
r.locat = locat;
end
