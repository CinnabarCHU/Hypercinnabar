function [retval, id] = analyzer(params, id)
% gammp.analyzer parameters: a x.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/swa/gammp.m#L2
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('gammp-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[result] = gammp(p.a, p.x);
r = struct();
r.result = result;
end
