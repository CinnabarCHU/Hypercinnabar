function [retval, id] = analyzer(params, id)
% tanerhilbertML.analyzer parameters: data fc fl fh c.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/tanerhilbertML.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('tanerhilbertML-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[tanhilb, ifaze, ifreq] = tanerhilbertML(p.data, p.fc, p.fl, p.fh, p.c);
r = struct();
r.tanhilb = tanhilb;
r.ifaze = ifaze;
r.ifreq = ifreq;
end
