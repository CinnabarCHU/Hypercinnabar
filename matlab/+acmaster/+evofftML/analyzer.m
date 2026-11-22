function [retval,id] = analyzer(params,id)
% evofftML.analyzer parameters: data window step fmin fmax normal.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/evofftML.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('evofftML-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[s, x_grid, y_grid] = evofftML(p.data, p.window, p.step, p.fmin, p.fmax, p.normal);
r = struct();
r.s = s;
r.x_grid = x_grid;
r.y_grid = y_grid;
end
