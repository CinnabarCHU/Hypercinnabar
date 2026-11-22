function [retval,id] = analyzer(params,id)
% MovingGaussian.analyzer parameters: data windowPoints.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleGaussianMovingAverage.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('MovingGaussian-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[result, meta] = acycleGaussianMovingAverage(p.data, p.windowPoints);
r = struct();
r.result = result;
r.meta = meta;
end
