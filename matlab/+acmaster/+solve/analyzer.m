function [retval,id] = analyzer(params,id)
% solve.analyzer parameters: A B N N1 ZERO.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/swa/solve.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('solve-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[A, B, N] = solve(p.A, p.B, p.N, p.N1, p.ZERO);
r = struct();
r.A = A;
r.B = B;
r.N = N;
end
