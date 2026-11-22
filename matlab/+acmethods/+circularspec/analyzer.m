function [retval, id] = analyzer(params, id)
% circularspec.analyzer parameters: data p1 p2 pn linlog.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/circularspec.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('circularspec-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[P, R, t0] = circularspec(p.data, p.p1, p.p2, p.pn, p.linlog, 0);
r = struct();
r.P = P;
r.R = R;
r.t0 = t0;
end
