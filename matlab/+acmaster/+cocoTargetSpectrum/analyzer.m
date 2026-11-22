function [retval,id] = analyzer(params,id)
% cocoTargetSpectrum.analyzer parameters: dat pad dataPower orbit9 lax sr_i targetMode.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cocoTargetSpectrum.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cocoTargetSpectrum-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[la] = cocoTargetSpectrum(p.dat, p.pad, p.dataPower, p.orbit9, p.lax, p.sr_i, p.targetMode);
r = struct();
r.la = la;
end
