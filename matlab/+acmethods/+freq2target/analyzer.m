function [retval, id] = analyzer(params, id)
% freq2target.analyzer parameters: f p fx fray.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/freq2target.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('freq2target-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[px] = freq2target(p.f, p.p, p.fx, p.fray);
r = struct();
r.px = px;
end
