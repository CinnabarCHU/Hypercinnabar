function [retval,id] = helper(params,id)
% cvcoco2.helper parameters: method inputs; optional options overrides.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/cvcoco2.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('cvcoco2-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
options.BatchSize = 100;
options.Seed = 1;
options.ProgressFcn = [];
options.MaxFrequency = [];
options.AnalysisName = '';
options.SplitMode = 'midpoint';
options.InterleavedPhase = 0;
options.Verbose = true;
options.WarnOnPartialTraining = true;
r = p;
if isfield(p,'options'), options = accompat.overrideOptions(options,p.options); end
r.options = options;
end
