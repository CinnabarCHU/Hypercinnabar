function [retval,id] = analyzer(params,id)
% formatts.analyzer parameters: d.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/formatts.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('formatts-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[d, dt] = formatts(p.d);
r = struct();
r.d = d;
r.dt = dt;
end
