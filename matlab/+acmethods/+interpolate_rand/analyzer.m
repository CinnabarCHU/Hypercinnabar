function [retval, id] = analyzer(params, id)
% interpolate_rand.analyzer parameters: data interpolate_rate.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/interpolate_rand.m#L4
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('interpolate_rand-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[data_even] = interpolate_rand(p.data, p.interpolate_rate);
r = struct();
r.data_even = data_even;
end
