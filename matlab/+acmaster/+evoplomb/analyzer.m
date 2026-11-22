function [retval,id] = analyzer(params,id)
% evoplomb.analyzer parameters: data window step fmin fmax normal.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/evoplomb.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('evoplomb-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[s, x_grid, y_grid] = evoplomb(p.data, p.window, p.step, p.fmin, p.fmax, p.normal);
r = struct();
r.s = s;
r.x_grid = x_grid;
r.y_grid = y_grid;
end
