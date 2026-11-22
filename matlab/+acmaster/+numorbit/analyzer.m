function [retval,id] = analyzer(params,id)
% numorbit.analyzer parameters: orbit7 nyquist rayleigh sr_range mpts.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/numorbit.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('numorbit-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[norbit] = numorbit(p.orbit7, p.nyquist, p.rayleigh, p.sr_range, p.mpts, 0);
r = struct();
r.norbit = norbit;
end
