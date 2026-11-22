function [retval,id] = helper(params,id)
% ecocoCrossfitCore.helper parameters: method inputs; optional options overrides.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocoCrossfitCore.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocoCrossfitCore-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
options.BatchSize = 20;
options.ComputeLocalP = false;
options.ProgressFcn = [];
options.MemoryBudgetMiB = 256;
options.WindowMode = 'legacy-count';
options.StepDepth = [];
options.CenterLimits = [];
options.WarnOnPartialTraining = true;
r = p;
if isfield(p,'options'), options = accompat.overrideOptions(options,p.options); end
r.options = options;
end
