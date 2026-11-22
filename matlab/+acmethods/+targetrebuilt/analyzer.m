function [retval, id] = analyzer(params, id)
% targetrebuilt.analyzer parameters: target.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/targetrebuilt.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('targetrebuilt-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[targetnew] = targetrebuilt(p.target);
r = struct();
r.targetnew = targetnew;
end
