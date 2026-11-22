function [retval, id] = analyzer(params, id)
% redconfchi2.analyzer parameters: datax nw dt pad method.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/redconfchi2.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('redconfchi2-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[f, p, theored, chi90, chi95, ...
    chi99, chi999] = redconfchi2(p.datax, p.nw, p.dt, p.pad, p.method);
r = struct();
r.f = f;
r.p = p;
r.theored = theored;
r.chi90 = chi90;
r.chi95 = chi95;
r.chi99 = chi99;
r.chi999 = chi999;
end
