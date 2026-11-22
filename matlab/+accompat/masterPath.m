function restore = masterPath()
% Scope name resolution to the pinned 3.1.1 sources, even when GUIDE is installed.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
source = fullfile(root,'upstream','master');
code = fullfile(source,'code');
if ~isfile(fullfile(code,'seriesanalysis','acycleSamplingIsUneven.m'))
    error('Acycle:Master:MissingSource','Initialize upstream/master or use a complete method export.');
end
previous = path;
restore = onCleanup(@() path(previous));
% MATLAB always searches the working directory before the search path.
% Refuse to run in another Acycle source directory when it can shadow kernels.
oldRoots = {fullfile(root,'upstream','acycle'),fullfile(root,'upstream','recovered')};
if exist('OCTAVE_VERSION','builtin')
    legacy = which('AC');
else
    legacy = which('AC','-all');
end
if ischar(legacy), legacy = cellstr(legacy); end
for index = 1:numel(legacy)
    if isfile(fullfile(fileparts(legacy{index}),'AC.fig'))
        oldRoots{end+1} = fileparts(fileparts(fileparts(legacy{index}))); %#ok<AGROW>
    end
end
parts = strsplit(previous,pathsep);
keep = true(size(parts));
for index = 1:numel(oldRoots)
    folder = oldRoots{index};
    if strcmp(pwd,folder) || startsWith(pwd,[folder,filesep])
        error('Acycle:Master:WorkingDirectory','Run the master method outside the GUIDE source tree.');
    end
    keep = keep & ~strcmp(parts,folder) & ~startsWith(parts,[folder,filesep]);
end
path(strjoin(parts(keep),pathsep));
addpath(source);
addpath(genpath(code));
data = fullfile(source,'data');
if isfolder(data), addpath(genpath(data)); end
end
