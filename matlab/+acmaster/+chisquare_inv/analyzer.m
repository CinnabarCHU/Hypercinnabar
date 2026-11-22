function [retval,id] = analyzer(params,id)
% chisquare_inv.analyzer parameters: P V.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/chisquare_inv.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('chisquare_inv-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[X] = chisquare_inv(p.P, p.V);
r = struct();
r.X = X;
end
