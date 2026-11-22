function [retval,id] = analyzer(params,id)
% findnpk.analyzer parameters: dat n o.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/findnpk.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('findnpk-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[loc, val] = findnpk(p.dat, p.n, p.o);
r = struct();
r.loc = loc;
r.val = val;
end
