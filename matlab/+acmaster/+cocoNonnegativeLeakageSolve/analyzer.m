function [retval,id] = analyzer(params,id)
% cocoNonnegativeLeakageSolve.analyzer parameters: mixingMatrix dataEnergy.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cocoNonnegativeLeakageSolve.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cocoNonnegativeLeakageSolve-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
[groupPower, bestResidual] = cocoNonnegativeLeakageSolve(p.mixingMatrix, p.dataEnergy);
r = struct();
r.groupPower = groupPower;
r.bestResidual = bestResidual;
end
