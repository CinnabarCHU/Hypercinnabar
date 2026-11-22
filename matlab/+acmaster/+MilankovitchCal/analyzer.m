function [retval,id] = analyzer(params,id)
% MilankovitchCal.analyzer parameters: age.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/MilankovitchCal.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('MilankovitchCal-v3.1.1+dcba427/analyzer',params,id,@execute);
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
