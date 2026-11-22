function [retval, id] = analyzer(params, id)
% gentarget.analyzer parameters: laskar t1 t2 f1 f2 ne nt np pad method.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/gentarget.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('gentarget-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[target] = gentarget(p.laskar, p.t1, p.t2, p.f1, p.f2, p.ne, p.nt, p.np, p.pad, p.method);
r = struct();
r.target = target;
end
