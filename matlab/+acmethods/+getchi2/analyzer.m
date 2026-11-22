function [retval, id] = analyzer(params, id)
% getchi2.analyzer parameters: dof alpha.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/swa/getchi2.m#L7
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('getchi2-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[chi2] = getchi2(p.dof, p.alpha);
r = struct();
r.chi2 = chi2;
end
