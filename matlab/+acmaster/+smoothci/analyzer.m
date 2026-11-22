function [retval,id] = analyzer(params,id)
% smoothci.analyzer parameters: xy xs span method.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/smoothci.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('smoothci-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[ys] = smoothci(p.xy, p.xs, p.span, p.method);
r = struct();
r.ys = ys;
end
