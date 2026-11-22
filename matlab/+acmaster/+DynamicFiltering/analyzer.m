function [retval,id] = analyzer(params,id)
% DynamicFiltering.analyzer parameters: data lowerControlPoints upperControlPoints options.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleDynamicFilter.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('DynamicFiltering-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[result, windows, meta] = acycleDynamicFilter(p.data, p.lowerControlPoints, p.upperControlPoints, p.options);
r = struct();
r.result = result;
r.windows = windows;
r.meta = meta;
end
