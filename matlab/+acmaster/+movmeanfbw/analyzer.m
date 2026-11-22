function [retval,id] = analyzer(params,id)
% movmeanfbw.analyzer parameters: data window step halfwindow alpha.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/movmeanfbw.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('movmeanfbw-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[t, meantd, vartd, np, CI_lower, CI_upper, mediantd] = movmeanfbw(p.data, p.window, p.step, p.halfwindow, p.alpha, 0);
r = struct();
r.t = t;
r.meantd = meantd;
r.vartd = vartd;
r.np = np;
r.CI_lower = CI_lower;
r.CI_upper = CI_upper;
r.mediantd = mediantd;
end
