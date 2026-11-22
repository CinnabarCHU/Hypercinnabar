function [retval, id] = analyzer(params, id)
% getBerger89Period.analyzer parameters: t.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/getBerger89Period.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('getBerger89Period-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[BP89PP] = getBerger89Period(p.t);
r = struct();
r.BP89PP = BP89PP;
end
