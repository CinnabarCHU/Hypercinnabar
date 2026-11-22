function [retval,id] = analyzer(params,id)
% cocoGetPowerNew.analyzer parameters: data_pow orbit9 sr dat.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cocoGetPowerNew.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cocoGetPowerNew-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[targetp] = cocoGetPowerNew(p.data_pow, p.orbit9, p.sr, p.dat);
r = struct();
r.targetp = targetp;
end
