function [retval,id] = plotter(params,id)
% dynamic_filter.plotter parameters: data window step fmin fmax unit norm padding.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/dynamic_filter.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('dynamic_filter-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
dynamic_filter(p.data, p.window, p.step, p.fmin, p.fmax, p.unit, p.norm, p.padding);
r = [];
end
