function [retval, id] = analyzer(params, id)
% ellipse_s.analyzer parameters: e npts.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/ellipse_s.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ellipse_s-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[x, y] = ellipse_s(p.e, p.npts);
r = struct();
r.x = x;
r.y = y;
end
