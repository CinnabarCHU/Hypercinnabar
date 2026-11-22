function [retval, id] = analyzer(params, id)
% zeropad2.analyzer parameters: data win padding.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/zeropad2.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('zeropad2-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[dataX] = zeropad2(p.data, p.win, p.padding);
r = struct();
r.dataX = dataX;
end
