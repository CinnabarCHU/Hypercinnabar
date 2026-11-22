function restore = cocoTargetPath(params)
% The 3.1.1 tree still has six kernels that refer to the removed four-argument freq2target.
restore = [];
if ~isfield(params,'legacyTarget')
    if ~isempty(which('freq2target'))
        error('Acycle:COCO:ForeignTarget','Another installation supplies freq2target. Select the historical implementation explicitly.');
    end
    return
end
if ~isequal(char(params.legacyTarget),'guide-b52ea9f')
    error('Acycle:COCO:UnknownTarget','Expected legacyTarget = guide-b52ea9f.');
end
folder = fullfile(fileparts(fileparts(fileparts(mfilename('fullpath')))),'upstream','compatibility','coco');
file = fullfile(folder,'freq2target.m');
if ~isfile(file), error('Acycle:COCO:MissingTarget','The pinned GUIDE compatibility file is missing.'); end
before = path;
restore = onCleanup(@() path(before));
addpath(folder);
if ~strcmp(which('freq2target'),file)
    error('Acycle:COCO:ShadowedTarget','The current directory shadows the historical COCO target.');
end
end
