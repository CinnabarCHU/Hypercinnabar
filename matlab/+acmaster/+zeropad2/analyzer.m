function [retval,id] = analyzer(params,id)
% zeropad2.analyzer parameters: data win padding ensureHalfWindowCoverage.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/zeropad2.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('zeropad2-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[dataX] = zeropad2(p.data, p.win, p.padding, p.ensureHalfWindowCoverage);
r = struct();
r.dataX = dataX;
end
