function [retval, id] = analyzer(params, id)
% select_interval.analyzer parameters: data t1 t2.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/select_interval.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('select_interval-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[select_inter] = select_interval(p.data, p.t1, p.t2);
r = struct();
r.select_inter = select_inter;
end
