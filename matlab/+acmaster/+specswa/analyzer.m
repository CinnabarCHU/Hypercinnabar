function [retval,id] = analyzer(params,id)
% specswa.analyzer parameters: freq xlogp ndata verbose.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/swa/specswa.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('specswa-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[swa, winfinal, diagnostics] = specswa(p.freq, p.xlogp, p.ndata, p.verbose);
r = struct();
r.swa = swa;
r.winfinal = winfinal;
r.diagnostics = diagnostics;
end
