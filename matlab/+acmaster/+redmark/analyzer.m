function [retval,id] = analyzer(params,id)
% redmark.analyzer parameters: alfa n.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/redmark.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('redmark-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[yred] = redmark(p.alfa, p.n);
r = struct();
r.yred = yred;
end
