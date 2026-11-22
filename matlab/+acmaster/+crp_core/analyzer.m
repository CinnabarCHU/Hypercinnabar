function [retval,id] = analyzer(params,id)
% crp_core.analyzer parameters: x y m tau e method normFlag.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/recurrence/crp_core.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('crp_core-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[xout] = crp_core(p.x, p.y, p.m, p.tau, p.e, p.method, p.normFlag);
r = struct();
r.xout = xout;
end
