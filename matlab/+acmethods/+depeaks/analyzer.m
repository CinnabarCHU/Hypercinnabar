function [retval, id] = analyzer(params, id)
% depeaks.analyzer parameters: data ymin_cut ymax_cut.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/depeaks.m#L3
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('depeaks-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[depeaksinter] = depeaks(p.data, p.ymin_cut, p.ymax_cut);
r = struct();
r.depeaksinter = depeaksinter;
end
