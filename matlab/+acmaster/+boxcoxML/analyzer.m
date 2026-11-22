function [retval,id] = analyzer(params,id)
% boxcoxML.analyzer parameters: y lambda.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/boxcoxML.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('boxcoxML-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[y_trans] = boxcoxML(p.y, p.lambda);
r = struct();
r.y_trans = y_trans;
end
