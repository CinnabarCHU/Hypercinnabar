function [retval, id] = analyzer(params, id)
% gammln.analyzer parameters: xx.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/swa/gammln.m#L3
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('gammln-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[gammln1, xx] = gammln(p.xx);
r = struct();
r.gammln1 = gammln1;
r.xx = xx;
end
