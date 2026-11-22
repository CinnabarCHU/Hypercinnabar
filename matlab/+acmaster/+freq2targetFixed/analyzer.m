function [retval,id] = analyzer(params,id)
% freq2targetFixed.analyzer parameters: dat pad orbit9 lax sr_i.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/freq2targetFixed.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('freq2targetFixed-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[la] = freq2targetFixed(p.dat, p.pad, p.orbit9, p.lax, p.sr_i);
r = struct();
r.la = la;
end
