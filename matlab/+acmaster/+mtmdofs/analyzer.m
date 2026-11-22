function [retval,id] = analyzer(params,id)
% mtmdofs.analyzer parameters: t y NW npad.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/mtmdofs.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('mtmdofs-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[freq, dof, wt] = mtmdofs(p.t, p.y, p.NW, p.npad);
r = struct();
r.freq = freq;
r.dof = dof;
r.wt = wt;
end
