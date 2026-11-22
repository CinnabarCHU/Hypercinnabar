function [retval,id] = analyzer(params,id)
% SedimentationRateToAge.analyzer parameters: data depthUnit firstAgeKyr.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleSedimentationRateAgeModel.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('SedimentationRateToAge-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[result, meta] = acycleSedimentationRateAgeModel(p.data, p.depthUnit, p.firstAgeKyr);
r = struct();
r.result = result;
r.meta = meta;
end
