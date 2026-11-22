function [retval, id] = analyzer(params, id)
% gamser.analyzer parameters: a x.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/swa/gamser.m#L2
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('gamser-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[gamser] = gamser(p.a, p.x);
r = struct();
r.gamser = gamser;
end
