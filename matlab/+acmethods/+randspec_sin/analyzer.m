function [retval, id] = analyzer(params, id)
% randspec_sin.analyzer parameters: f n dat_ray.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/randspec_sin.m#L3
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('randspec_sin-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[randspectrum] = randspec_sin(p.f, p.n, p.dat_ray);
r = struct();
r.randspectrum = randspectrum;
end
