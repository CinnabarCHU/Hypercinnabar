function [retval,id] = analyzer(params,id)
% strAssign.analyzer parameters: in1 r1 r2 rhs.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/swa/strAssign.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('strAssign-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[in1] = strAssign(p.in1, p.r1, p.r2, p.rhs);
r = struct();
r.in1 = in1;
end
