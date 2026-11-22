function [retval,id] = analyzer(params,id)
% bispectralPreprocess.analyzer parameters: data options.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bispectral/bispectralPreprocess.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('bispectralPreprocess-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[processed, meta] = bispectralPreprocess(p.data, p.options);
r = struct();
r.processed = processed;
r.meta = meta;
end
