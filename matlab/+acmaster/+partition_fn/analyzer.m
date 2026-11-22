function [retval,id] = analyzer(params,id)
% partition_fn.analyzer parameters: Py k_max N.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bayes_changepoint/partition_fn.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('partition_fn-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[P] = partition_fn(p.Py, p.k_max, p.N);
r = struct();
r.P = P;
end
