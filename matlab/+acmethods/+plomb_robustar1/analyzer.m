function [retval, id] = analyzer(params, id)
% plomb_robustar1.analyzer parameters: datax timex fmax smoothwin.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/plomb_robustar1.m#L2
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('plomb_robustar1-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[po, f, pth] = plomb_robustar1(p.datax, p.timex, p.fmax, p.smoothwin, 0);
r = struct();
r.po = po;
r.f = f;
r.pth = pth;
end
