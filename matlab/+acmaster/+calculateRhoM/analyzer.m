function [retval,id] = analyzer(params,id)
% calculateRhoM.analyzer parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/seriesanalysis/calculateRhoM.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('calculateRhoM-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[rhoM] = calculateRhoM(p.data);
r = struct();
r.rhoM = rhoM;
end
