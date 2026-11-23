function probeMethodRoleContracts()
% Exercise public entry points in the two pinned snapshots, reporting differences
% from the proposed contracts without making those differences requirements.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
originalPath = path;
oldLog = getenv('ACYCLE_LOG_DIR');
oldVisibility = get(groot,'defaultFigureVisible');
originalFigures = findall(groot,'Type','figure');
journal = tempname;
mkdir(journal);
cleanup = onCleanup(@() acRoleProbeRestore(originalPath,oldLog,oldVisibility,originalFigures,journal)); %#ok<NASGU>
addpath(root);
setup_migration;
setenv('ACYCLE_LOG_DIR',journal);
set(groot,'defaultFigureVisible','off');

% Supply only one option. Then delete a required option from the resolved input.
p = struct('data',[0 2 5;2 6 9],'samplingInterval',1, ...
    'options',struct('MaximumPoints',23));
h = acmaster.RegularInterpolation.helper(p,aclog.newId());
assert(h.options.MaximumPoints==23 && h.options.MaximumElements==16e6);
id = aclog.newId();
v = acmaster.RegularInterpolation.analyzer(h,id);
assert(isequal(v.interpolated,[0 2 5;1 4 7;2 6 9]));
assert(isequaln(v,aclog.replay(id)));
bad = h;
bad.options = rmfield(h.options,'MaximumElements');
failedId = aclog.newId();
try
    acmaster.RegularInterpolation.analyzer(bad,failedId);
    error('Acycle:Probe:ExpectedFailure','Expected the missing option to fail.');
catch err
    assert(strcmp(err.identifier,'Acycle:Method:MissingOption') && contains(err.message,'MaximumElements'));
end
failed = acRoleProbeRecords(failedId);
assert(any(cellfun(@(r) strcmp(r.attr,'error'),failed)));
assert(strcmp(failed{end}.info.status,'cancelled') && isempty(failed{end}.info.retval));

% Compare explicit top-level and nested settings on the same signal.
t = (0:127)';
data = [t, sin(2*pi*t/16)+0.25*cos(2*pi*t/5)];
requested = struct('data',data,'method','Periodogram','nfft',256,'models',struct('classic',true));
h = acmaster.PowerSpectrum.helper(requested,aclog.newId());
assert(h.models.classic && isfield(h.models,'bendingPowerLaw'));
fprintf('Acycle role probe | spectrum helper | requested nfft=%d returned=%d | classic=%d | model flags=%d\n', ...
    requested.nfft,h.nfft,h.models.classic,numel(fieldnames(h.models)));

% The old periodogram accepts an omitted noise block. Check the actual journal
% and product rather than inferring what happened from a field-name search.
old = struct('data',data,'method','Periodogram','padtimes',1,'nzeropad',128);
oldId = aclog.newId();
v = acmethods.PowerSpectrum.analyzer(old,oldId);
terminal = acRoleProbeRecords(oldId);
assert(~isempty(v.po) && strcmp(terminal{end}.info.status,'done'));
fprintf('Acycle role probe | GUIDE omitted noise | terminal=%s | models present=%d\n', ...
    terminal{end}.info.status,isfield(v,'models'));

% A missing input for an enabled model should be distinguished from a
% numerical convergence problem after all inputs have passed validation.
h.method = 'Multi-taper method';
h.models = struct('robust',true,'classic',false,'ftest',false,'swa',false, ...
    'powerLaw',false,'bendingPowerLaw',false);
h = rmfield(h,'fitModel');
badId = aclog.newId();
try
    v = acmaster.PowerSpectrum.analyzer(h,badId);
    assert(~isempty(v.power) && isfield(v.issues,'robust') && contains(v.issues.robust.message,'fitModel'));
catch err
    if ~contains(err.message,'fitModel'), rethrow(err); end
end
records = acRoleProbeRecords(badId);
assert(any(strcmp(records{end}.info.status,{'incomplete','cancelled'})));
fprintf('Acycle role probe | missing active fitModel | terminal=%s | retval reference=%d\n', ...
    records{end}.info.status,~isempty(records{end}.info.retval));

% Select a caller-owned axes and observe what the unmodified historical
% plotter does. No live graphics handle is serialized into the call journal.
host = figure('Visible','off');
ax = axes('Parent',host);
before = findall(groot,'Type','figure');
plotId = aclog.newId();
v = acmethods.ShowImage.plotter(struct('im_name',uint8([0 255;128 64])),plotId);
after = findall(groot,'Type','figure');
records = acRoleProbeRecords(plotId);
assert(strcmp(records{end}.info.status,'done'));
fprintf('Acycle role probe | GUIDE ShowImage | new figures=%d | host images=%d | empty retval=%d\n', ...
    numel(after)-numel(before),numel(findall(ax,'Type','image')),isempty(v));
end

function records = acRoleProbeRecords(id)
lines = regexp(strtrim(fileread(id)),'\r?\n','split');
records = cellfun(@jsondecode,lines,'UniformOutput',false);
end

function acRoleProbeRestore(originalPath,oldLog,oldVisibility,originalFigures,journal)
for fig = reshape(findall(groot,'Type','figure'),1,[])
    if ~any(originalFigures==fig), delete(fig); end
end
set(groot,'defaultFigureVisible',oldVisibility);
setenv('ACYCLE_LOG_DIR',oldLog);
path(originalPath);
rmdir(journal,'s');
end
