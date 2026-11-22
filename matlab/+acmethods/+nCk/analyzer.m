function [retval, id] = analyzer(params, id)
% nCk.analyzer parameters: n k.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/bayes_changepoint/nCk.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('nCk-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[n_k] = nCk(p.n, p.k);
r = struct();
r.n_k = n_k;
end
