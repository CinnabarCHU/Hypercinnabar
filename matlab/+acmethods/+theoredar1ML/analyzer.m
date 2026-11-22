function [retval, id] = analyzer(params, id)
% theoredar1ML.analyzer parameters: datax f meanp dt.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/theoredar1ML.m#L10
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('theoredar1ML-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[theored] = theoredar1ML(p.datax, p.f, p.meanp, p.dt);
r = struct();
r.theored = theored;
end
