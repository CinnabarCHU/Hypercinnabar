function [retval, id] = analyzer(params, id)
% spectralmoments.analyzer parameters: data window step pad srmean smoothmodel padedge.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/spectralmoments.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('spectralmoments-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[depth, uf, Bw, Bwtrend, sr] = spectralmoments(p.data, p.window, p.step, p.pad, p.srmean, p.smoothmodel, p.padedge);
r = struct();
r.depth = depth;
r.uf = uf;
r.Bw = Bw;
r.Bwtrend = Bwtrend;
r.sr = sr;
end
