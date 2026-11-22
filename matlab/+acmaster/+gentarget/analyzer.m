function [retval,id] = analyzer(params,id)
% gentarget.analyzer parameters: laskar t1 t2 f1 f2 ne nt np pad method.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/gentarget.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('gentarget-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[target] = gentarget(p.laskar, p.t1, p.t2, p.f1, p.f2, p.ne, p.nt, p.np, p.pad, p.method);
r = struct();
r.target = target;
end
