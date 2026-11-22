function [retval, id] = analyzer(params, id)
% domaintrans.analyzer parameters: x1 t.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/domaintrans.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('domaintrans-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[x] = domaintrans(p.x1, p.t);
r = struct();
r.x = x;
end
