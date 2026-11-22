function [retval, id] = analyzer(params, id)
% smoothwavelet.analyzer parameters: wave dt period dj scale.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/smoothwavelet.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('smoothwavelet-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[swave] = smoothwavelet(p.wave, p.dt, p.period, p.dj, p.scale);
r = struct();
r.swave = swave;
end
