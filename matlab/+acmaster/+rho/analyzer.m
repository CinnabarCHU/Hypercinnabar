function [retval,id] = analyzer(params,id)
% rho.analyzer parameters: x nData varx.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/swa/rho.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('rho-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[rho1] = rho(p.x, p.nData, p.varx);
r = struct();
r.rho1 = rho1;
end
