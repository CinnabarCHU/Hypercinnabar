function [retval,id] = analyzer(params,id)
% plomb_robustar1.analyzer parameters: datax timex fmax smoothwin.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/plomb_robustar1.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('plomb_robustar1-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[po, f, pth] = plomb_robustar1(p.datax, p.timex, p.fmax, p.smoothwin, 0);
r = struct();
r.po = po;
r.f = f;
r.pth = pth;
end
