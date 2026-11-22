function [retval,id] = analyzer(params,id)
% wave_bases.analyzer parameters: mother k scale param.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/wave_bases.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('wave_bases-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[daughter, fourier_factor, coi, dofmin] = wave_bases(p.mother, p.k, p.scale, p.param);
r = struct();
r.daughter = daughter;
r.fourier_factor = fourier_factor;
r.coi = coi;
r.dofmin = dofmin;
end
