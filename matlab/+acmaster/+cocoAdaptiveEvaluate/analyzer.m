function [retval,id] = analyzer(params,id)
% cocoAdaptiveEvaluate.analyzer parameters: dataPower dat pad dataFrequency orbit9 rayleigh srGrid method options(BatchSize,ProgressFcn,RateBounds,MaxFrequency,TargetModel,AmplitudeMode).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cocoAdaptiveEvaluate.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cocoAdaptiveEvaluate-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'BatchSize','ProgressFcn','RateBounds','MaxFrequency','TargetModel','AmplitudeMode'});
[rho, pValue, nMissing, diagnostic] = cocoAdaptiveEvaluate( ...
    p.dataPower, p.dat, p.pad, p.dataFrequency, [], p.orbit9, p.rayleigh, p.srGrid, [],  ...
    p.method, 'BatchSize',p.options.BatchSize, 'ProgressFcn',p.options.ProgressFcn,  ...
    'RateBounds',p.options.RateBounds, 'MaxFrequency',p.options.MaxFrequency,  ...
    'TargetModel',p.options.TargetModel, 'AmplitudeMode',p.options.AmplitudeMode);
r = struct();
r.rho = rho;
r.pValue = pValue;
r.nMissing = nMissing;
r.diagnostic = diagnostic;
end
