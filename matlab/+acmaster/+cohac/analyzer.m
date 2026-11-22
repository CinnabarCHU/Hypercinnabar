function [retval,id] = analyzer(params,id)
% cohac.analyzer parameters: x y sr window winsize nooverlap alpha.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/cohac.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cohac-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[Cxy, F1, MSC_critical, significant_freqs, significant_Cxy, ...
    phase_diff_deg, F2, phase_uncertainty_deg] = cohac(p.x, p.y, p.sr, p.window, p.winsize, p.nooverlap, p.alpha, 0);
r = struct();
r.Cxy = Cxy;
r.F1 = F1;
r.MSC_critical = MSC_critical;
r.significant_freqs = significant_freqs;
r.significant_Cxy = significant_Cxy;
r.phase_diff_deg = phase_diff_deg;
r.F2 = F2;
r.phase_uncertainty_deg = phase_uncertainty_deg;
end
