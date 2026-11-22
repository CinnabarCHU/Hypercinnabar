function [retval, id] = analyzer(params, id)
% hpsort.analyzer parameters: arr.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/swa/hpsort.m#L3
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('hpsort-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[arr] = hpsort(p.arr);
r = struct();
r.arr = arr;
end
