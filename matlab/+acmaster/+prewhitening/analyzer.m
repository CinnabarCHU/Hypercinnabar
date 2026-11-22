function [retval,id] = analyzer(params,id)
% prewhitening.analyzer parameters: data rho.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/prewhitening.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('prewhitening-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[datp] = prewhitening(p.data, p.rho);
r = struct();
r.datp = datp;
end
