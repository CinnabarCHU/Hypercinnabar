function [retval, id] = analyzer(params, id)
% depthtotime.analyzer parameters: depth agemodel.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/depthtotime.m#L20
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('depthtotime-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[time, sr] = depthtotime(p.depth, p.agemodel);
r = struct();
r.time = time;
r.sr = sr;
end
