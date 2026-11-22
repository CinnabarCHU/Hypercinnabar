function [retval,id] = analyzer(params,id)
% hpsort.analyzer parameters: arr.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/swa/hpsort.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('hpsort-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[arr] = hpsort(p.arr);
r = struct();
r.arr = arr;
end
