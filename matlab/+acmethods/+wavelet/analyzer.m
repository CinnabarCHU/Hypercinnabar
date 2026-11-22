function [retval, id] = analyzer(params, id)
% wavelet.analyzer parameters: Y dt pad dj s0 J1 mother param.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/wavelet.m#L93
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('wavelet-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[wave, period, scale, coi] = wavelet(p.Y, p.dt, p.pad, p.dj, p.s0, p.J1, p.mother, p.param);
r = struct();
r.wave = wave;
r.period = period;
r.scale = scale;
r.coi = coi;
end
