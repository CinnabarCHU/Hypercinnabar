function [retval, id] = analyzer(params, id)
% solve.analyzer parameters: A B N N1 ZERO.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/swa/solve.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('solve-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[A, B, N] = solve(p.A, p.B, p.N, p.N1, p.ZERO);
r = struct();
r.A = A;
r.B = B;
r.N = N;
end
