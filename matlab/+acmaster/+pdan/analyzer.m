function [retval,id] = analyzer(params,id)
% pdan.analyzer parameters: data f3 window nw ftmin fterm step pad.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/pdan.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('pdan-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[pow] = pdan(p.data, p.f3, p.window, p.nw, p.ftmin, p.fterm, p.step, p.pad);
r = struct();
r.pow = pow;
end
