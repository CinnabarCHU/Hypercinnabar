function [retval,id] = analyzer(params,id)
% gaussfilter.analyzer parameters: datax dt fc fl fh.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/gaussfilter.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('gaussfilter-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[gaussbandx, filter, f] = gaussfilter(p.datax, p.dt, p.fc, p.fl, p.fh);
r = struct();
r.gaussbandx = gaussbandx;
r.filter = filter;
r.f = f;
end
