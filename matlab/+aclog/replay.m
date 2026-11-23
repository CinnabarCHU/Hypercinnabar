function [retval, newId] = replay(id)
% Replay a recorded public method with its parameters and initial random state.
% Every replay creates its own call journal. The caller's random state is restored.
if isnumeric(id), id=aclog.interfaceId(id,true); end
records = regexp(strtrim(fileread(id)), '\r?\n', 'split');
entry = jsondecode(records{1});
if ~strcmp(entry.attr,'init')
    error('Acycle:Replay:MissingInit','The journal has no invocation record.');
end
params = aclog.read(id,entry.info.params);
saved = [id,'.rng.mat'];
if isfile(saved)
    before = rng;
    restore = onCleanup(@() rng(before));
    state = load(saved,'value');
    rng(state.value);
end
if ismember(entry.info.op,{'Workflow_Robot-v1','Workflow_Robot_legacy-v1'})
    newId = acMenuNewId();
    retval = accore.robot(params,newId);
    return
end
menu = regexp(entry.info.op,'^Menu_(\w+)-v1/(helper|analyzer|plotter)$','tokens','once');
if ~isempty(menu)
    if isempty(which('acMenuExecute'))
        error('Acycle:Replay:Unavailable','Install the recorded menu interface to replay this invocation.');
    end
    % The master bispectrum includes a creation timestamp in its result.
    % Older menu journals have it in the return snapshot. Preserve it on replay.
    if strcmp(menu{1},'menu_bispectral') && strcmp(menu{2},'analyzer') && ...
            ~isempty(params.args) && isstruct(params.args{1}) && isfield(params.args{1},'operation') && ...
            isequal(params.args{1}.operation,'Bispectral') && isfile([id,'.retval.mat'])
        original = load([id,'.retval.mat'],'value');
        if isfield(original.value,'Created'), params.bispectralCreated = original.value.Created; end
    end
    newId=aclog.newId();
    retval=acMenuExecute(menu{1},menu{2},params,newId,[]);
    return
end
parts = regexp(entry.info.op, '^([A-Za-z]\w*)-(v1\.0|v3\.1\.1\+dcba427)/(helper|analyzer|plotter)$', 'tokens', 'once');
if isempty(parts), error('Acycle:Replay:Operation','Unrecognized method or version.'); end
if strcmp(parts{2},'v1.0'), namespace = 'acmethods'; else, namespace = 'acmaster'; end
name = [namespace,'.',parts{1},'.',parts{3}];
if isempty(which(name)), error('Acycle:Replay:Unavailable','Missing method %s.',name); end
method = str2func(name);
[retval,newId] = method(params);
end
