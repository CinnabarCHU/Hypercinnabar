function [retval, id] = analyzer(params, id)
% FixedMovingMean.analyzer parameters: data window step halfwindow alpha.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/movmeanfbw.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('FixedMovingMean-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[t, meantd, vartd, np, CI_lower, ...
    CI_upper, mediantd] = movmeanfbw(p.data, p.window, p.step, p.halfwindow, p.alpha, 0);
r = struct();
r.t = t;
r.meantd = meantd;
r.vartd = vartd;
r.np = np;
r.CI_lower = CI_lower;
r.CI_upper = CI_upper;
r.mediantd = mediantd;
end
