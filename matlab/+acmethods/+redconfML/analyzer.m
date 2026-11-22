function [retval, id] = analyzer(params, id)
% redconfML.analyzer parameters: x dt nw nfft linlog smoothwin fmax.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/redconfML.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('redconfML-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[rhoM, s0M, redconfAR1, redconfML96] = redconfML(p.x, p.dt, p.nw, p.nfft, p.linlog, p.smoothwin, p.fmax, 0);
r = struct();
r.rhoM = rhoM;
r.s0M = s0M;
r.redconfAR1 = redconfAR1;
r.redconfML96 = redconfML96;
end
