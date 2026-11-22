function [retval, id] = analyzer(params, id)
% redconf_any.analyzer parameters: f pxx dt smoothwin linlog.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/redconf_any.m#L2
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('redconf_any-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[theored1] = redconf_any(p.f, p.pxx, p.dt, p.smoothwin, p.linlog);
r = struct();
r.theored1 = theored1;
end
