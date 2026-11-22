function [retval,id] = analyzer(params,id)
% dl_all.analyzer parameters: x.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/recurrence/dl_all.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('dl_all-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[a_out, b_out] = dl_all(p.x);
r = struct();
r.a_out = a_out;
r.b_out = b_out;
end
