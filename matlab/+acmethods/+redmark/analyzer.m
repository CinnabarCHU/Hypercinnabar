function [retval, id] = analyzer(params, id)
% redmark.analyzer parameters: alfa n.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/redmark.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('redmark-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[yred] = redmark(p.alfa, p.n);
r = struct();
r.yred = yred;
end
