function [retval,id] = helper(params,id)
% cocoAdaptiveEvaluate.helper parameters: method inputs; optional options overrides.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cocoAdaptiveEvaluate.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cocoAdaptiveEvaluate-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
options.BatchSize = 100;
options.ProgressFcn = [];
options.RateBounds = [];
options.MaxFrequency = [];
options.TargetModel = 'phase-averaged';
options.AmplitudeMode = 'adaptive';
r = p;
if isfield(p,'options'), options = accompat.overrideOptions(options,p.options); end
r.options = options;
end
