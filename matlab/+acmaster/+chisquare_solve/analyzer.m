function [retval,id] = analyzer(params,id)
% chisquare_solve.analyzer parameters: XGUESS P V.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/package/wavelet/chisquare_solve.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('chisquare_solve-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[PDIFF] = chisquare_solve(p.XGUESS, p.P, p.V);
r = struct();
r.PDIFF = PDIFF;
end
