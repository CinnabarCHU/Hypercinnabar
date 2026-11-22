function [retval, id] = analyzer(params, id)
% lodla04.analyzer parameters: T.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/lodla04.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('lodla04-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[lod, doy] = lodla04(p.T);
r = struct();
r.lod = lod;
r.doy = doy;
end
