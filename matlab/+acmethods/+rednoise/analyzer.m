function [retval, id] = analyzer(params, id)
% rednoise.analyzer parameters: N g a.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/wavelet/rednoise.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('rednoise-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[yred] = rednoise(p.N, p.g, p.a);
r = struct();
r.yred = yred;
end
