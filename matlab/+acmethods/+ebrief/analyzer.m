function [retval, id] = analyzer(params, id)
% ebrief.analyzer parameters: X dim a.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/ebrief.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ebrief-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[Y] = ebrief(p.X, p.dim, p.a);
r = struct();
r.Y = Y;
end
