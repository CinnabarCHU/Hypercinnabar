function [retval,id] = analyzer(params,id)
% wave_signif.analyzer parameters: Y dt scale1 sigtest lag1 siglvl dof mother param.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/wave_signif.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('wave_signif-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[signif, fft_theor] = wave_signif(p.Y, p.dt, p.scale1, p.sigtest, p.lag1, p.siglvl, p.dof, p.mother, p.param);
r = struct();
r.signif = signif;
r.fft_theor = fft_theor;
end
