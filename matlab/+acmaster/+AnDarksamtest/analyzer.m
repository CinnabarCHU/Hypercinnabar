function [retval,id] = analyzer(params,id)
% AnDarksamtest.analyzer parameters: X alpha.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/univariate/AnDarksamtest.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('AnDarksamtest-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[AnDarksamtest1] = AnDarksamtest(p.X, p.alpha);
r = struct();
r.AnDarksamtest1 = AnDarksamtest1;
end
