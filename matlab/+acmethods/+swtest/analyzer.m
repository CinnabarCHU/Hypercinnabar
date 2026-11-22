function [retval, id] = analyzer(params, id)
% swtest.analyzer parameters: x alpha.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/univariate/swtest.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('swtest-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[H, pValue, W] = swtest(p.x, p.alpha);
r = struct();
r.H = H;
r.pValue = pValue;
r.W = W;
end
