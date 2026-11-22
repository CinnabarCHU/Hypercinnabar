function [retval,id] = analyzer(params,id)
% CE_NS70.analyzer parameters: data model.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/CE_NS70.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('CE_NS70-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[ce] = CE_NS70(p.data, p.model);
r = struct();
r.ce = ce;
end
