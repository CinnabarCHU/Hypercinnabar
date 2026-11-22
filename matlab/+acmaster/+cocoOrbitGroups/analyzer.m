function [retval,id] = analyzer(params,id)
% cocoOrbitGroups.analyzer parameters: orbitPeriods.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cocoOrbitGroups.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cocoOrbitGroups-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[groups] = cocoOrbitGroups(p.orbitPeriods);
r = struct();
r.groups = groups;
end
