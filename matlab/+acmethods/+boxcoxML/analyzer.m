function [retval, id] = analyzer(params, id)
% boxcoxML.analyzer parameters: y lambda.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/boxcoxML.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('boxcoxML-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[y_trans] = boxcoxML(p.y, p.lambda);
r = struct();
r.y_trans = y_trans;
end
