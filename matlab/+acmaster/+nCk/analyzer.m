function [retval,id] = analyzer(params,id)
% nCk.analyzer parameters: n k.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bayes_changepoint/nCk.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('nCk-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[n_k] = nCk(p.n, p.k);
r = struct();
r.n_k = n_k;
end
