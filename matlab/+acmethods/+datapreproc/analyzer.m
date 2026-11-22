function [retval, id] = analyzer(params, id)
% datapreproc.analyzer parameters: target.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/datapreproc.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('datapreproc-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[dat] = datapreproc(p.target, 0);
r = struct();
r.dat = dat;
end
