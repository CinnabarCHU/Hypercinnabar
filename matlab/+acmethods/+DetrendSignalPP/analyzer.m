function [retval, id] = analyzer(params, id)
% DetrendSignalPP.analyzer parameters: signal windowsize fs Porder.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/DetrendSignalPP.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DetrendSignalPP-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[signal, sigo] = DetrendSignalPP(p.signal, p.windowsize, p.fs, p.Porder);
r = struct();
r.signal = signal;
r.sigo = sigo;
end
