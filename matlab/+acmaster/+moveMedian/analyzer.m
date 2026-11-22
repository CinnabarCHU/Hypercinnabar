function [retval,id] = analyzer(params,id)
% moveMedian.analyzer parameters: x w.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/moveMedian.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('moveMedian-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[y] = moveMedian(p.x, p.w);
r = struct();
r.y = y;
end
