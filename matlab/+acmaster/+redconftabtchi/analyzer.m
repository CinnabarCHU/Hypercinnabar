function [retval,id] = analyzer(params,id)
% redconftabtchi.analyzer parameters: datax nw dt pad method.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/redconftabtchi.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('redconftabtchi-v3.1.1+dcba427/analyzer',params,id,@execute);
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
