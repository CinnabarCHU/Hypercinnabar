function [retval,id] = analyzer(params,id)
% getpks.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/getpks.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('getpks-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[datapks, m] = getpks(p.data);
r = struct();
r.datapks = datapks;
r.m = m;
end
