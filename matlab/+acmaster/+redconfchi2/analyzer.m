function [retval,id] = analyzer(params,id)
% redconfchi2.analyzer parameters: datax nw dt pad method.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/redconfchi2.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('redconfchi2-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[f, p, theored, chi90, chi95, chi99, chi999] = redconfchi2(p.datax, p.nw, p.dt, p.pad, p.method);
r = struct();
r.f = f;
r.p = p;
r.theored = theored;
r.chi90 = chi90;
r.chi95 = chi95;
r.chi99 = chi99;
r.chi999 = chi999;
end
