function [retval,id] = analyzer(params,id)
% findperct.analyzer parameters: va m.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/findperct.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('findperct-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[perct] = findperct(p.va, p.m);
r = struct();
r.perct = perct;
end
