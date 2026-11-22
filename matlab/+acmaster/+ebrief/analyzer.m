function [retval,id] = analyzer(params,id)
% ebrief.analyzer parameters: X dim a.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ebrief.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ebrief-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[Y] = ebrief(p.X, p.dim, p.a);
r = struct();
r.Y = Y;
end
