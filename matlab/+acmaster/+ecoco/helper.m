function [retval,id] = helper(params,id)
% ecoco.helper parameters: method inputs; optional options overrides.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/ecoco.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ecoco-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
options.ProgressFcn = [];
options.SeparateFinalPanel = true;
options.Verbose = true;
options.InterleavedWindowMode = 'physical-depth';
options.InterleavedStepDepth = [];
options.ECOCOWindowMode = 'physical-depth';
options.ECOCOStepDepth = [];
options.ECOCOCenterLimits = [];
options.BlockedConsensusPolicy = 'supported';
options.CrossfitConsensus = '';
r = p;
if isfield(p,'options'), options = accompat.overrideOptions(options,p.options); end
r.options = options;
end
