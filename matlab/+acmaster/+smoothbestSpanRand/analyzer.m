function [retval,id] = analyzer(params,id)
% smoothbestSpanRand.analyzer parameters: t y method num_iterations.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/smoothbestSpanRand.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('smoothbestSpanRand-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[bestSpan, bestAlpha, bestBeta] = smoothbestSpanRand(p.t, p.y, p.method, p.num_iterations, 0);
r = struct();
r.bestSpan = bestSpan;
r.bestAlpha = bestAlpha;
r.bestBeta = bestBeta;
end
