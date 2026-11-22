function [retval, id] = analyzer(params, id)
% gammcf.analyzer parameters: a x.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/swa/gammcf.m#L3
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('gammcf-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[gammcf1, gln] = gammcf(p.a, p.x);
r = struct();
r.gammcf1 = gammcf1;
r.gln = gln;
end
