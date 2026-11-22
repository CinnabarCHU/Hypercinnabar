function [retval,id] = analyzer(params,id)
% findduplicate.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/findduplicate.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('findduplicate-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[data] = findduplicate(p.data);
r = struct();
r.data = data;
end
