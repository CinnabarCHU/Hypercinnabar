function setup_migration(source)
% Put the portable method packages and the pinned Acycle dependencies on the path.
root = fileparts(mfilename('fullpath'));
if nargin == 0, source = fullfile(root, 'upstream', 'acycle'); end
if ~isfile(fullfile(source, 'code', 'guicode', 'AC.fig'))
    error('Acycle:Setup:MissingSource', 'Initialize the upstream/acycle submodule or pass its path.');
end
addpath(genpath(fullfile(source, 'code')));
addpath(genpath(fullfile(source, 'data')));
addpath(fullfile(root, 'matlab'));
end
