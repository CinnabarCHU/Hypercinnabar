function [retval,id] = analyzer(params,id)
% rednoise.analyzer parameters: N g a.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/rednoise.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('rednoise-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[yred] = rednoise(p.N, p.g, p.a);
r = struct();
r.yred = yred;
end
