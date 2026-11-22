function [retval, id] = analyzer(params, id)
% ar1spectrum.analyzer parameters: ar1 period.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/ar1spectrum.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ar1spectrum-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[P] = ar1spectrum(p.ar1, p.period);
r = struct();
r.P = P;
end
