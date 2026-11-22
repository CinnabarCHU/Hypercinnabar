function [retval,id] = analyzer(params,id)
% cocoGetPower.analyzer parameters: theoredML96_pow orbit9 sr.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cocoGetPower.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cocoGetPower-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[targetp] = cocoGetPower(p.theoredML96_pow, p.orbit9, p.sr);
r = struct();
r.targetp = targetp;
end
