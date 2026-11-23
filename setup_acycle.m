function root = setup_acycle()
% Activate only the assembled runtime, including its pinned numerical dependencies.
root = fileparts(mfilename('fullpath'));
if ~isfile(fullfile(root,'acycle-runtime.json'))
    root = fullfile(root,'.acycle-runtime');
    if ~isfile(fullfile(root,'acycle-runtime.json'))
        error('Acycle:Setup:Build','From the checkout run python migration/poc/build.py --output .acycle-runtime, or unpack the ready-to-run distribution.');
    end
end
source = fullfile(root,'upstream','acycle');
addpath(genpath(fullfile(root,'upstream','recovered','code')));
addpath(genpath(fullfile(source,'code')));
addpath(genpath(fullfile(source,'data')));
addpath(fullfile(source,'doc'));
referenceData = getenv('ACYCLE_REFERENCE_DATA');
if ~isempty(referenceData) && isfolder(referenceData), addpath(referenceData); end
addpath(genpath(fullfile(root,'code','method')));
addpath(genpath(fullfile(root,'code','interface')));
addpath(fullfile(root,'matlab'));
addpath(root);
end
