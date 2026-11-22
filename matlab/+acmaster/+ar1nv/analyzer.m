function [retval,id] = analyzer(params,id)
% ar1nv.analyzer parameters: x.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/ar1nv.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ar1nv-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[g, a] = ar1nv(p.x);
r = struct();
r.g = g;
r.a = a;
end
