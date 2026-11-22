function [retval, id] = analyzer(params, id)
% partition_fn.analyzer parameters: Py k_max N.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/bayes_changepoint/partition_fn.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('partition_fn-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[P] = partition_fn(p.Py, p.k_max, p.N);
r = struct();
r.P = P;
end
