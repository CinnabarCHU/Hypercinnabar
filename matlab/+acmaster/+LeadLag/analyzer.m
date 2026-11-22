function [retval,id] = analyzer(params,id)
% LeadLag.analyzer parameters: reference target maximumLag lagStep coordinateDirection.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/acycleLeadLagRmse.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('LeadLag-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[result, meta] = acycleLeadLagRmse(p.reference, p.target, p.maximumLag, p.lagStep, p.coordinateDirection);
r = struct();
r.result = result;
r.meta = meta;
end
