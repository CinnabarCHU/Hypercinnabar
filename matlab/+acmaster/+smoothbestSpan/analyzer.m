function [retval,id] = analyzer(params,id)
% smoothbestSpan.analyzer parameters: t y method alpha beta.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/smoothbestSpan.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('smoothbestSpan-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[bestSpan] = smoothbestSpan(p.t, p.y, p.method, p.alpha, p.beta);
r = struct();
r.bestSpan = bestSpan;
end
