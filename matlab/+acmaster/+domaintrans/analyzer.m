function [retval,id] = analyzer(params,id)
% domaintrans.analyzer parameters: x1 t.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/domaintrans.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('domaintrans-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[x] = domaintrans(p.x1, p.t);
r = struct();
r.x = x;
end
