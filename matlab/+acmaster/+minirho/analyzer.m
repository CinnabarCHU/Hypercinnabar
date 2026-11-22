function [retval,id] = analyzer(params,id)
% minirho.analyzer parameters: s0 fn ft pxxsmooth linlog.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/minirho.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('minirho-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[rho, s0] = minirho(p.s0, p.fn, p.ft, p.pxxsmooth, p.linlog, 0);
r = struct();
r.rho = rho;
r.s0 = s0;
end
