function [retval, id] = analyzer(params, id)
% pdan.analyzer parameters: data f3 window nw ftmin fterm step pad.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/pdan.m#L2
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('pdan-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[pow] = pdan(p.data, p.f3, p.window, p.nw, p.ftmin, p.fterm, p.step, p.pad);
r = struct();
r.pow = pow;
end
