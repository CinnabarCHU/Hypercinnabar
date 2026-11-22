function [retval,id] = analyzer(params,id)
% swtest.analyzer parameters: x alpha.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/univariate/swtest.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('swtest-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[H, pValue, W] = swtest(p.x, p.alpha);
r = struct();
r.H = H;
r.pValue = pValue;
r.W = W;
end
