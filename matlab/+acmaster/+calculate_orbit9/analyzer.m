function [retval,id] = analyzer(params,id)
% calculate_orbit9.analyzer parameters: ageMa.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/secular_periods/calculate_orbit9.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('calculate_orbit9-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[orbit9] = calculate_orbit9(p.ageMa);
r = struct();
r.orbit9 = orbit9;
end
