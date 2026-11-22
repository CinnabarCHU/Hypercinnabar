function [retval,id] = analyzer(params,id)
% AR1Prewhitening.analyzer parameters: data options.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acyclePrewhitenSeries.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('AR1Prewhitening-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[result, meta] = acyclePrewhitenSeries(p.data, p.options);
r = struct();
r.result = result;
r.meta = meta;
end
