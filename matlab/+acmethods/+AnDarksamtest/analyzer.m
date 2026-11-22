function [retval, id] = analyzer(params, id)
% AnDarksamtest.analyzer parameters: X alpha.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/univariate/AnDarksamtest.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('AnDarksamtest-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[AnDarksamtest1] = AnDarksamtest(p.X, p.alpha);
r = struct();
r.AnDarksamtest1 = AnDarksamtest1;
end
