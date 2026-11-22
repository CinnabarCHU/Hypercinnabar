function [retval,id] = analyzer(params,id)
% ecocoPhysicalCenters.analyzer parameters: depth window stepDepth centerLimits.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocoPhysicalCenters.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocoPhysicalCenters-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[centers, info] = ecocoPhysicalCenters(p.depth, p.window, p.stepDepth, p.centerLimits);
r = struct();
r.centers = centers;
r.info = info;
end
