function [retval,id] = analyzer(params,id)
% dynotPercentilePlan.analyzer parameters: selection.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/dynotPercentilePlan.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('dynotPercentilePlan-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[plan] = dynotPercentilePlan(p.selection);
r = struct();
r.plan = plan;
end
