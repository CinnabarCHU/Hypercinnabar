function [retval,id] = analyzer(params,id)
% AmplitudeModulation.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleAmplitudeModulation.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('AmplitudeModulation-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[result, meta] = acycleAmplitudeModulation(p.data);
r = struct();
r.result = result;
r.meta = meta;
end
