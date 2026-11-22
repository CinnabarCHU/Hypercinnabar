function [retval, id] = analyzer(params, id)
% wave_bases.analyzer parameters: mother k scale param.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/wave_bases.m#L33
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('wave_bases-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[daughter, fourier_factor, coi, dofmin] = wave_bases(p.mother, p.k, p.scale, p.param);
r = struct();
r.daughter = daughter;
r.fourier_factor = fourier_factor;
r.coi = coi;
r.dofmin = dofmin;
end
