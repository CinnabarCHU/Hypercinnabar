function [retval,id] = analyzer(params,id)
% freq2targetNew.analyzer parameters: dat pad data_pow orbit9 lax sr_i.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/freq2targetNew.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('freq2targetNew-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[la] = freq2targetNew(p.dat, p.pad, p.data_pow, p.orbit9, p.lax, p.sr_i);
r = struct();
r.la = la;
end
