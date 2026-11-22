function [retval,id] = analyzer(params,id)
% interpolate_rand.analyzer parameters: data interpolate_rate.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/interpolate_rand.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('interpolate_rand-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[data_even] = interpolate_rand(p.data, p.interpolate_rate);
r = struct();
r.data_even = data_even;
end
