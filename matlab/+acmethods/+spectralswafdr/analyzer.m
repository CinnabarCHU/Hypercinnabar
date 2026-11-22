function [retval, id] = analyzer(params, id)
% spectralswafdr.analyzer parameters: data method nw padtimes.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/swa/spectralswafdr.m#L2
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('spectralswafdr-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[outputdata] = spectralswafdr(p.data, p.method, p.nw, p.padtimes, 0);
r = struct();
r.outputdata = outputdata;
end
