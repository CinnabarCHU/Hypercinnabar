function [retval,id] = plotter(params,id)
% InsolLatDayGif.plotter parameters: II t lat day unit_t_r name_insol.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/InsolLatDayGif.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('InsolLatDayGif-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
InsolLatDayGif(p.II, p.t, p.lat, p.day, p.unit_t_r, p.name_insol);
r = [];
end
