function value = read(id, ref)
% Resolve a params or retval reference relative to the associated journal.
if isempty(ref), value = []; return; end
entry = load(fullfile(fileparts(id), ref), 'value');
value = entry.value;
end
