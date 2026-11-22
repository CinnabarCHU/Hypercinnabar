function [retval, id] = analyzer(params, id)
% gaussmf.analyzer parameters: x params.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/gaussmf.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('gaussmf-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[y] = gaussmf(p.x, p.params);
r = struct();
r.y = y;
end
