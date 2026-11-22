function [retval,id] = analyzer(params,id)
% norbits.analyzer parameters: target f power orbit7 rayleigh sr.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/norbits.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('norbits-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[nm] = norbits(p.target, p.f, p.power, p.orbit7, p.rayleigh, p.sr);
r = struct();
r.nm = nm;
end
