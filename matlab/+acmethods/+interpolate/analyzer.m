function [retval, id] = analyzer(params, id)
% interpolate.analyzer parameters: data interpolate_rate.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/interpolate.m#L3
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('interpolate-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[data_even] = interpolate(p.data, p.interpolate_rate);
r = struct();
r.data_even = data_even;
end
