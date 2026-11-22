function [retval, id] = analyzer(params, id)
% evofftML.analyzer parameters: data window step fmin fmax normal.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/evofftML.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('evofftML-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[s, x_grid, y_grid] = evofftML(p.data, p.window, p.step, p.fmin, p.fmax, p.normal);
r = struct();
r.s = s;
r.x_grid = x_grid;
r.y_grid = y_grid;
end
