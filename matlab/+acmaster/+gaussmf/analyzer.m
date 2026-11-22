function [retval,id] = analyzer(params,id)
% gaussmf.analyzer parameters: x params.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/gaussmf.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('gaussmf-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[y] = gaussmf(p.x, p.params);
r = struct();
r.y = y;
end
