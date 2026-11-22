function [retval, id] = analyzer(params, id)
% numorbit.analyzer parameters: orbit7 nyquist rayleigh sr_range mpts.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/numorbit.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('numorbit-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[norbit] = numorbit(p.orbit7, p.nyquist, p.rayleigh, p.sr_range, p.mpts, 0);
r = struct();
r.norbit = norbit;
end
