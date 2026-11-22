function [retval, id] = analyzer(params, id)
% period2spectrumB.analyzer parameters: orbit7 t1 t2 sr f1 f2 method pad.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/period2spectrumB.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('period2spectrumB-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[target] = period2spectrumB(p.orbit7, p.t1, p.t2, p.sr, p.f1, p.f2, p.method, p.pad);
r = struct();
r.target = target;
end
