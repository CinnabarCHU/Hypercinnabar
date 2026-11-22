function [retval, id] = analyzer(params, id)
% pick_k1.analyzer parameters: k.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/bayes_changepoint/pick_k1.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('pick_k1-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[num_chgpts] = pick_k1(p.k);
r = struct();
r.num_chgpts = num_chgpts;
end
