function [retval,id] = analyzer(params,id)
% spectralswafdr.analyzer parameters: data method nw padtimes.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/swa/spectralswafdr.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('spectralswafdr-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[outputdata] = spectralswafdr(p.data, p.method, p.nw, p.padtimes, 0);
r = struct();
r.outputdata = outputdata;
end
