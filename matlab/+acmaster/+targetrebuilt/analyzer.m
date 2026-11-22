function [retval,id] = analyzer(params,id)
% targetrebuilt.analyzer parameters: target.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/targetrebuilt.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('targetrebuilt-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[targetnew] = targetrebuilt(p.target);
r = struct();
r.targetnew = targetnew;
end
