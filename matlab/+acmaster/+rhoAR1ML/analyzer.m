function [retval,id] = analyzer(params,id)
% rhoAR1ML.analyzer parameters: datax.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/rhoAR1ML.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('rhoAR1ML-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[rho] = rhoAR1ML(p.datax);
r = struct();
r.rho = rho;
end
