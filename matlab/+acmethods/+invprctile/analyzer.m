function [retval, id] = analyzer(params, id)
% invprctile.analyzer parameters: x xq dim plot_pos.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/invprctile.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('invprctile-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[p] = invprctile(p.x, p.xq, p.dim, p.plot_pos);
r = struct();
r.p = p;
end
