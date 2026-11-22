function [retval, id] = analyzer(params, id)
% mmdd2dayi.analyzer parameters: doy.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/mmdd2dayi.m#L2
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('mmdd2dayi-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[mm, dd] = mmdd2dayi(p.doy);
r = struct();
r.mm = mm;
r.dd = dd;
end
