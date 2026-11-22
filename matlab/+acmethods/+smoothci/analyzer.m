function [retval, id] = analyzer(params, id)
% smoothci.analyzer parameters: xy xs span method.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/smoothci.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('smoothci-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[ys] = smoothci(p.xy, p.xs, p.span, p.method);
r = struct();
r.ys = ys;
end
