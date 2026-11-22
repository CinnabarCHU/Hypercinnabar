function [retval,id] = analyzer(params,id)
% redNoisePeriodogramMC.analyzer parameters: data rhoM mcn red pad options(BatchSize,UseParallel,Slices).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/redNoisePeriodogramMC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('redNoisePeriodogramMC-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'BatchSize','UseParallel','Slices'});
[f, pMC] = redNoisePeriodogramMC( ...
    p.data, p.rhoM, p.mcn, p.red, p.pad, 'BatchSize',p.options.BatchSize,  ...
    'UseParallel',p.options.UseParallel, 'Slices',p.options.Slices);
r = struct();
r.f = f;
r.pMC = pMC;
end
