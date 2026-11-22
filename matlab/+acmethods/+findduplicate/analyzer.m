function [retval, id] = analyzer(params, id)
% findduplicate.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/findduplicate.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('findduplicate-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[data] = findduplicate(p.data);
r = struct();
r.data = data;
end
