function [retval,id] = analyzer(params,id)
% recplot.analyzer parameters: x threshold t labelx labely.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/recurrence/recplot.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('recplot-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[S] = recplot(p.x, p.threshold, p.t, 0, p.labelx, p.labely);
r = struct();
r.S = S;
end
