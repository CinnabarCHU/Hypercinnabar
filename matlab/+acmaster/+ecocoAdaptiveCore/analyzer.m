function [retval,id] = analyzer(params,id)
% ecocoAdaptiveCore.analyzer parameters: data orbit9 window dt step red pad srGrid nsim method maxFrequency seed options(BatchSimulations,ProgressFcn,WindowMode,StepDepth,CenterLimits).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocoAdaptiveCore.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocoAdaptiveCore-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'BatchSimulations','ProgressFcn','WindowMode','StepDepth','CenterLimits'});
[result] = ecocoAdaptiveCore( ...
    p.data, p.orbit9, p.window, p.dt, p.step, p.red, p.pad, p.srGrid, p.nsim, p.method,  ...
    p.maxFrequency, p.seed, 'BatchSimulations',p.options.BatchSimulations,  ...
    'ProgressFcn',p.options.ProgressFcn, 'WindowMode',p.options.WindowMode,  ...
    'StepDepth',p.options.StepDepth, 'CenterLimits',p.options.CenterLimits);
r = struct();
r.result = result;
end
