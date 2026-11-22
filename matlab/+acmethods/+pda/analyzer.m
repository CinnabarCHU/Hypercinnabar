function [retval, id] = analyzer(params, id)
% pda.analyzer parameters: data fmin fmax window nw.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/pda.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('pda-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[powratio, m] = pda(p.data, p.fmin, p.fmax, p.window, p.nw);
r = struct();
r.powratio = powratio;
r.m = m;
end
