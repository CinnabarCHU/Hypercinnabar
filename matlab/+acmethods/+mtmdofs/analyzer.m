function [retval, id] = analyzer(params, id)
% mtmdofs.analyzer parameters: t y NW npad.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/mtmdofs.m#L2
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('mtmdofs-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[freq, dof, wt] = mtmdofs(p.t, p.y, p.NW, p.npad);
r = struct();
r.freq = freq;
r.dof = dof;
r.wt = wt;
end
