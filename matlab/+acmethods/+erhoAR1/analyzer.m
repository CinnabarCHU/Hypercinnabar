function [retval, id] = analyzer(params, id)
% erhoAR1.analyzer parameters: data window.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/erhoAR1.m#L10
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('erhoAR1-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[rhox] = erhoAR1(p.data, p.window);
r = struct();
r.rhox = rhox;
end
