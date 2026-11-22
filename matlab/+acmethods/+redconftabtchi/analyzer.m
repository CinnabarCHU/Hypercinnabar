function [retval, id] = analyzer(params, id)
% redconftabtchi.analyzer parameters: datax nw dt pad method.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/redconftabtchi.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('redconftabtchi-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[f, p, theored, tabtchi90, tabtchi95, ...
    tabtchi99, tabtchi999] = redconftabtchi(p.datax, p.nw, p.dt, p.pad, p.method);
r = struct();
r.f = f;
r.p = p;
r.theored = theored;
r.tabtchi90 = tabtchi90;
r.tabtchi95 = tabtchi95;
r.tabtchi99 = tabtchi99;
r.tabtchi999 = tabtchi999;
end
