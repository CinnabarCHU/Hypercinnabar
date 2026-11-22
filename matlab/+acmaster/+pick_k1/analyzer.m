function [retval,id] = analyzer(params,id)
% pick_k1.analyzer parameters: k.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/bayes_changepoint/pick_k1.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('pick_k1-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[num_chgpts] = pick_k1(p.k);
r = struct();
r.num_chgpts = num_chgpts;
end
