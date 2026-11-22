function [retval,id] = analyzer(params,id)
% cocoResolvedDetrendedVariance.analyzer parameters: originalValues detrendedValues.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cocoResolvedDetrendedVariance.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cocoResolvedDetrendedVariance-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[resolved, residualStd, relativeResidualRms, tolerance] = cocoResolvedDetrendedVariance( ...
    p.originalValues, p.detrendedValues);
r = struct();
r.resolved = resolved;
r.residualStd = residualStd;
r.relativeResidualRms = relativeResidualRms;
r.tolerance = tolerance;
end
