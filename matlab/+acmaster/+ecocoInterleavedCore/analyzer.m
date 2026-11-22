function [retval,id] = analyzer(params,id)
% ecocoInterleavedCore.analyzer parameters: data orbit9 window dt step red pad srGrid nsim method maxFrequency seed options(BatchSize,ProgressFcn,WindowMode,StepDepth,WarnOnPartialTraining).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocoInterleavedCore.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocoInterleavedCore-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
accompat.requireFields(p.options,{'BatchSize','ProgressFcn','WindowMode','StepDepth','WarnOnPartialTraining'});
[result] = ecocoInterleavedCore( ...
    p.data, p.orbit9, p.window, p.dt, p.step, p.red, p.pad, p.srGrid, p.nsim, p.method,  ...
    p.maxFrequency, p.seed, 'BatchSize',p.options.BatchSize,  ...
    'ProgressFcn',p.options.ProgressFcn, 'WindowMode',p.options.WindowMode,  ...
    'StepDepth',p.options.StepDepth, 'WarnOnPartialTraining',p.options.WarnOnPartialTraining);
r = struct();
r.result = result;
end
