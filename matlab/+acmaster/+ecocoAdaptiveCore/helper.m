function [retval,id] = helper(params,id)
% ecocoAdaptiveCore.helper parameters: method inputs; optional options overrides.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecocoAdaptiveCore.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecocoAdaptiveCore-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
options.BatchSimulations = [];
options.ProgressFcn = [];
options.WindowMode = 'legacy-count';
options.StepDepth = [];
options.CenterLimits = [];
r = p;
if isfield(p,'options'), options = accompat.overrideOptions(options,p.options); end
r.options = options;
end
