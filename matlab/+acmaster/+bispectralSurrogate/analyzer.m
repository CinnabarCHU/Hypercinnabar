function [retval,id] = analyzer(params,id)
% bispectralSurrogate.analyzer parameters: y type iterations.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralSurrogate.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('bispectralSurrogate-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[surrogate, meta] = bispectralSurrogate(p.y, p.type, p.iterations);
r = struct();
r.surrogate = surrogate;
r.meta = meta;
end
