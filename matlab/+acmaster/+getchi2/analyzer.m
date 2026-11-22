function [retval,id] = analyzer(params,id)
% getchi2.analyzer parameters: dof alpha.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/swa/getchi2.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('getchi2-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[chi2] = getchi2(p.dof, p.alpha);
r = struct();
r.chi2 = chi2;
end
