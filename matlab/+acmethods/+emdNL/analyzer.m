function [retval, id] = analyzer(params, id)
% emdNL.analyzer parameters: y goal.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/emdNL.m#L4
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('emdNL-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[c] = emdNL(p.y, p.goal);
r = struct();
r.c = c;
end
