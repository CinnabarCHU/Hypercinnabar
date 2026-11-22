function [retval,id] = helper(params,id)
% corrcoefslices_rankNew.helper parameters: method inputs; optional options overrides.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/corrcoef/corrcoefslices_rankNew.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('corrcoefslices_rankNew-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
orbit9 = p.orbit9;
targetMode = p.targetMode;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/corrcoefslices_rankNew.m:L56-L61
targetMode = lower(strtrim(char(targetMode)));
if ~any(strcmp(targetMode, ...
        {'adaptive','adaptive9','adaptive9a','adaptive9b','fixed','fixed9'}))
    error(['Select either Adaptive COCO or Fixed-target COCO through ', ...
        'a supported Acycle interface.']);
end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/corrcoefslices_rankNew.m:L64-L68
defaultMaximumFrequency = 0.5;
if isAdaptiveTargetMode(targetMode) && isnumeric(orbit9) && ...
        ~isempty(orbit9) && all(isfinite(orbit9(:))) && all(orbit9(:) > 0)
    defaultMaximumFrequency = 1.2*max(1./orbit9(:));
end
%% End copied source
options.MaxFrequency = defaultMaximumFrequency;
options.Seed = 1;
options.ShowPeriodograms = true;
options.ProgressFcn = [];
r = p;
if isfield(p,'options'), options = accompat.overrideOptions(options,p.options); end
r.options = options;
end

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/corrcoef/corrcoefslices_rankNew.m:L1630-L1633
function tf = isAdaptiveTargetMode(targetMode)
tf = any(strcmp(targetMode, ...
    {'adaptive','adaptive9','adaptive9a','adaptive9b'}));
end
%% End copied source
