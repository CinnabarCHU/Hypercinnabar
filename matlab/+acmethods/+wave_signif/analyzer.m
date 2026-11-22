function [retval, id] = analyzer(params, id)
% wave_signif.analyzer parameters: Y dt scale1 sigtest lag1 siglvl dof mother param.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/wave_signif.m#L65
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('wave_signif-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[signif, fft_theor] = wave_signif(p.Y, p.dt, p.scale1, p.sigtest, p.lag1, p.siglvl, p.dof, p.mother, p.param);
r = struct();
r.signif = signif;
r.fft_theor = fft_theor;
end
