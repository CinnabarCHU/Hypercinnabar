function [retval,id] = analyzer(params,id)
% randspec_sin.analyzer parameters: f n dat_ray.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/randspec_sin.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('randspec_sin-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[randspectrum] = randspec_sin(p.f, p.n, p.dat_ray);
r = struct();
r.randspectrum = randspectrum;
end
