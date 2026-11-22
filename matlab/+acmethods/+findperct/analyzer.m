function [retval, id] = analyzer(params, id)
% findperct.analyzer parameters: va m.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/findperct.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('findperct-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[perct] = findperct(p.va, p.m);
r = struct();
r.perct = perct;
end
