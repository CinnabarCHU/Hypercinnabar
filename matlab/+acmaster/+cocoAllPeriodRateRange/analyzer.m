function [retval,id] = analyzer(params,id)
% cocoAllPeriodRateRange.analyzer parameters: periods sampleSpacing sampleCount.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cocoAllPeriodRateRange.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cocoAllPeriodRateRange-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[rateRange] = cocoAllPeriodRateRange(p.periods, p.sampleSpacing, p.sampleCount);
r = struct();
r.rateRange = rateRange;
end
