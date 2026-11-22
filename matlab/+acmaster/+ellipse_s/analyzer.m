function [retval,id] = analyzer(params,id)
% ellipse_s.analyzer parameters: e npts.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/ellipse_s.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ellipse_s-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[x, y] = ellipse_s(p.e, p.npts);
r = struct();
r.x = x;
r.y = y;
end
