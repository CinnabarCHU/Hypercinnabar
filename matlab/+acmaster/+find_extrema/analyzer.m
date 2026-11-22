function [retval,id] = analyzer(params,id)
% find_extrema.analyzer parameters: y.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/find_extrema.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('find_extrema-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[max_p, max_v, min_p, min_v] = find_extrema(p.y);
r = struct();
r.max_p = max_p;
r.max_v = max_v;
r.min_p = min_p;
r.min_v = min_v;
end
