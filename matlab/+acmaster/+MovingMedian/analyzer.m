function [retval,id] = analyzer(params,id)
% MovingMedian.analyzer parameters: data windowPoints.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleFixedCountMovingSummary.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('MovingMedian-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[result, meta] = acycleFixedCountMovingSummary(p.data, 'median', p.windowPoints);
r = struct();
r.result = result;
r.meta = meta;
end
