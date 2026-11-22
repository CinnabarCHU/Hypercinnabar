function [retval,id] = analyzer(params,id)
% wavelet.analyzer parameters: Y dt pad dj s0 J1 mother param.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/wavelet.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('wavelet-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[wave, period, scale, coi] = wavelet(p.Y, p.dt, p.pad, p.dj, p.s0, p.J1, p.mother, p.param);
r = struct();
r.wave = wave;
r.period = period;
r.scale = scale;
r.coi = coi;
end
