function [retval,id] = analyzer(params,id)
% period2spectrum.analyzer parameters: orbit7 t1 t2 sr f1 f2 method pad.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/period2spectrum.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('period2spectrum-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[target] = period2spectrum(p.orbit7, p.t1, p.t2, p.sr, p.f1, p.f2, p.method, p.pad);
r = struct();
r.target = target;
end
