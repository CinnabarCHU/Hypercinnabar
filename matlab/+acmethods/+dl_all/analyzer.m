function [retval, id] = analyzer(params, id)
% dl_all.analyzer parameters: x.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/recurrence/dl_all.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('dl_all-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[a_out, b_out] = dl_all(p.x);
r = struct();
r.a_out = a_out;
r.b_out = b_out;
end
