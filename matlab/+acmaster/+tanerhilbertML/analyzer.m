function [retval,id] = analyzer(params,id)
% tanerhilbertML.analyzer parameters: data fc fl fh c.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/tanerhilbertML.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('tanerhilbertML-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[tanhilb, ifaze, ifreq, filter, responseFrequency, ifreqCoordinate] = tanerhilbertML(p.data, p.fc, p.fl, p.fh, p.c);
r = struct();
r.tanhilb = tanhilb;
r.ifaze = ifaze;
r.ifreq = ifreq;
r.filter = filter;
r.responseFrequency = responseFrequency;
r.ifreqCoordinate = ifreqCoordinate;
end
