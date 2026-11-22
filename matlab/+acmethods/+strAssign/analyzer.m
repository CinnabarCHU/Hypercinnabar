function [retval, id] = analyzer(params, id)
% strAssign.analyzer parameters: in1 r1 r2 rhs.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/swa/strAssign.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('strAssign-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[in1] = strAssign(p.in1, p.r1, p.r2, p.rhs);
r = struct();
r.in1 = in1;
end
