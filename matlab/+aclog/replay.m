function [retval, newId] = replay(id)
% Replay a recorded public method with its parameters and initial random state.
% Every replay creates its own call journal. The caller's random state is restored.
records = regexp(strtrim(fileread(id)), '\r?\n', 'split');
entry = jsondecode(records{1});
if ~strcmp(entry.attr,'init')
    error('Acycle:Replay:MissingInit','The journal has no invocation record.');
end
parts = regexp(entry.info.op, '^([A-Za-z]\w*)-v1\.0/(helper|analyzer|plotter)$', 'tokens', 'once');
if isempty(parts), error('Acycle:Replay:Operation','Unrecognized method or version.'); end
name = ['acmethods.',parts{1},'.',parts{2}];
if isempty(which(name)), error('Acycle:Replay:Unavailable','Missing method %s.',name); end
params = aclog.read(id,entry.info.params);
saved = [id,'.rng.mat'];
if isfile(saved)
    before = rng;
    restore = onCleanup(@() rng(before));
    state = load(saved,'value');
    rng(state.value);
end
method = str2func(name);
[retval,newId] = method(params);
end
