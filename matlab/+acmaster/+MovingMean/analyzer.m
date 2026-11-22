function [retval,id] = analyzer(params,id)
% MovingMean.analyzer parameters: data windowPoints.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleFixedCountMovingSummary.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('MovingMean-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[result, meta] = acycleFixedCountMovingSummary(p.data, 'mean', p.windowPoints);
r = struct();
r.result = result;
r.meta = meta;
end
