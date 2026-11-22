function [retval,id] = analyzer(params,id)
% RegularInterpolation.analyzer parameters: data samplingInterval options(MaximumPoints,MaximumElements).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleInterpolateSeries.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('RegularInterpolation-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'MaximumPoints','MaximumElements'});
[interpolated, meta] = acycleInterpolateSeries( ...
    p.data, p.samplingInterval, 'MaximumPoints',p.options.MaximumPoints,  ...
    'MaximumElements',p.options.MaximumElements);
r = struct();
r.interpolated = interpolated;
r.meta = meta;
end
