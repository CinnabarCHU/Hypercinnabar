function [retval, id] = analyzer(params, id)
% getpks.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/getpks.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('getpks-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[datapks, m] = getpks(p.data);
r = struct();
r.datapks = datapks;
r.m = m;
end
