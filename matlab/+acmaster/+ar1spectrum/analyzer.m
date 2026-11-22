function [retval,id] = analyzer(params,id)
% ar1spectrum.analyzer parameters: ar1 period.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/ar1spectrum.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ar1spectrum-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[P] = ar1spectrum(p.ar1, p.period);
r = struct();
r.P = P;
end
