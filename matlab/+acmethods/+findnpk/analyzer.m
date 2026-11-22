function [retval, id] = analyzer(params, id)
% findnpk.analyzer parameters: dat n o.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/findnpk.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('findnpk-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[loc, val] = findnpk(p.dat, p.n, p.o);
r = struct();
r.loc = loc;
r.val = val;
end
