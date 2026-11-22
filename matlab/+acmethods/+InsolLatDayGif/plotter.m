function [retval, id] = plotter(params, id)
% InsolLatDayGif.plotter parameters: II t lat day unit_t_r name_insol.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/InsolLatDayGif.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('InsolLatDayGif-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
InsolLatDayGif(p.II, p.t, p.lat, p.day, p.unit_t_r, p.name_insol);
r = [];
end
