function [retval,id] = analyzer(params,id)
% getBerger89Period.analyzer parameters: t.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/getBerger89Period.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('getBerger89Period-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[BP89PP] = getBerger89Period(p.t);
r = struct();
r.BP89PP = BP89PP;
end
