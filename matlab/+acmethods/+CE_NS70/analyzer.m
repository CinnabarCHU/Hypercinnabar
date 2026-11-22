function [retval, id] = analyzer(params, id)
% CE_NS70.analyzer parameters: data model.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/CE_NS70.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('CE_NS70-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[ce] = CE_NS70(p.data, p.model);
r = struct();
r.ce = ce;
end
