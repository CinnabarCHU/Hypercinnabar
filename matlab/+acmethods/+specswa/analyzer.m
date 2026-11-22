function [retval, id] = analyzer(params, id)
% specswa.analyzer parameters: freq xlogp ndata.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/swa/specswa.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('specswa-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[swa, winfinal] = specswa(p.freq, p.xlogp, p.ndata);
r = struct();
r.swa = swa;
r.winfinal = winfinal;
end
