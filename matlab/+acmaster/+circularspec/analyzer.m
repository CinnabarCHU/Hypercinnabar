function [retval,id] = analyzer(params,id)
% circularspec.analyzer parameters: data p1 p2 pn linlog.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/circularspec.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('circularspec-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[P, R, t0] = circularspec(p.data, p.p1, p.p2, p.pn, p.linlog, 0);
r = struct();
r.P = P;
r.R = R;
r.t0 = t0;
end
