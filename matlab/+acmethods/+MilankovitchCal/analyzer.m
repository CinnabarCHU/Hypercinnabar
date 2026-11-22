function [retval, id] = analyzer(params, id)
% MilankovitchCal.analyzer parameters: age.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/misc/MilankovitchCal.m#L17
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('MilankovitchCal-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[daymin, daymax, amin, amax, kmin, ...
    kmax, obmin, obmax, o1min, o1max, ...
    p1min, p1max, p2min, p2max, p3min, ...
    p3max, p4min, p4max] = MilankovitchCal(p.age);
r = struct();
r.daymin = daymin;
r.daymax = daymax;
r.amin = amin;
r.amax = amax;
r.kmin = kmin;
r.kmax = kmax;
r.obmin = obmin;
r.obmax = obmax;
r.o1min = o1min;
r.o1max = o1max;
r.p1min = p1min;
r.p1max = p1max;
r.p2min = p2min;
r.p2max = p2max;
r.p3min = p3min;
r.p3max = p3max;
r.p4min = p4min;
r.p4max = p4max;
end
