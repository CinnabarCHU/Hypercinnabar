function [retval, id] = analyzer(params, id)
% rmse4leadlag.analyzer parameters: target series ll step timedir.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/rmse4leadlag.m#L31
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('rmse4leadlag-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[llgrid, RMSE] = rmse4leadlag(p.target, p.series, p.ll, p.step, p.timedir, 0);
r = struct();
r.llgrid = llgrid;
r.RMSE = RMSE;
end
